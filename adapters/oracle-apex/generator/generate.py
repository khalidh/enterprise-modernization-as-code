from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml


IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,29}\Z")
APEX_ID_BASE = 910000000000000000


def _identifier(value, label):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ValueError(f"Invalid {label}: {value!r}")
    return value.upper()


def _sql_literal(value):
    return "'" + str(value).replace("'", "''") + "'"


def _varchar2_join(lines):
    values = ",\n".join(f"    {_sql_literal(line)}" for line in lines)
    return f"wwv_flow_string.join(wwv_flow_t_varchar2(\n{values}))"


def _load_yaml(path, label):
    with Path(path).open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"{label} must contain a YAML mapping")
    return value


def _prepare(model, config):
    form = model.get("form")
    apex = config.get("apex")
    if not isinstance(form, dict) or not isinstance(apex, dict):
        raise ValueError("Model must define form and config must define apex")

    form_name = _identifier(form.get("name"), "form name")
    title = form.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Form title is required")

    table_name = _identifier(apex.get("table_name"), "table name")
    primary_key = _identifier(apex.get("primary_key_column"), "primary key")
    default_text_length = apex.get("default_text_length")
    if not isinstance(default_text_length, int) or default_text_length < 1:
        raise ValueError("apex.default_text_length must be a positive integer")

    fields = form.get("fields")
    buttons = form.get("buttons")
    if not isinstance(fields, list) or not fields:
        raise ValueError("At least one form field is required")
    if not isinstance(buttons, list) or not buttons:
        raise ValueError("At least one form button is required")

    normalized_fields = []
    field_names = set()
    columns = set()
    for field in fields:
        if not isinstance(field, dict):
            raise ValueError("Each field must be a mapping")
        name = _identifier(field.get("name"), "field name")
        column = _identifier(field.get("column", name), "column name")
        label = field.get("label")
        field_type = field.get("type")
        if not isinstance(label, str) or not label.strip():
            raise ValueError(f"A label is required for field {name}")
        if field_type not in ("number", "text"):
            raise ValueError(f"A supported type is required for field {name}")
        if name in field_names:
            raise ValueError(f"Duplicate field name: {name}")
        if column in columns:
            raise ValueError(f"Duplicate database column: {column}")
        field_names.add(name)
        columns.add(column)

        length = field.get("length", default_text_length)
        if field_type == "text" and (not isinstance(length, int) or length < 1):
            raise ValueError(f"Invalid text length for field {name}")
        if field_type == "number" and "length" in field:
            raise ValueError(f"Numeric field {name} cannot have a text length")
        normalized_fields.append(
            {
                "name": name,
                "column": column,
                "label": label.strip(),
                "type": field_type,
                "length": length if field_type == "text" else None,
            }
        )

    if primary_key not in columns:
        raise ValueError(f"Primary key column {primary_key} is not mapped by a field")
    primary_field = next(field for field in normalized_fields if field["column"] == primary_key)
    if primary_field["type"] != "number":
        raise ValueError("The primary key field must have type number")

    normalized_buttons = []
    object_names = set(field_names)
    for button in buttons:
        if not isinstance(button, dict):
            raise ValueError("Each button must be a mapping")
        name = _identifier(button.get("name"), "button name")
        label = button.get("label")
        if not isinstance(label, str) or not label.strip():
            raise ValueError(f"A label is required for button {name}")
        if name in object_names:
            raise ValueError(f"Duplicate form object name: {name}")
        object_names.add(name)
        normalized_buttons.append({"name": name, "label": label.strip()})

    release = apex.get("release")
    version_date = apex.get("version_date")
    application_id = apex.get("application_id")
    application_alias = _identifier(apex.get("application_alias"), "application alias")
    theme_id = apex.get("universal_theme_id")
    if not isinstance(release, str) or not release.startswith("18.2."):
        raise ValueError("This adapter currently generates APEX 18.2 exports only")
    if not isinstance(application_id, int) or application_id < 1000:
        raise ValueError("apex.application_id must be an integer of at least 1000")
    if theme_id != 42:
        raise ValueError("This adapter requires Universal Theme 42")

    return {
        "form_name": form_name,
        "title": title.strip(),
        "table": table_name,
        "primary_key": primary_key,
        "fields": normalized_fields,
        "buttons": normalized_buttons,
        "release": release,
        "version_date": version_date,
        "application_id": application_id,
        "application_alias": application_alias,
        "theme_id": theme_id,
    }


def _render_schema(data):
    definitions = []
    for field in data["fields"]:
        if field["column"] == data["primary_key"]:
            definitions.append(
                f"    {field['column']} NUMBER GENERATED BY DEFAULT ON NULL AS IDENTITY NOT NULL"
            )
        elif field["type"] == "number":
            definitions.append(f"    {field['column']} NUMBER")
        else:
            definitions.append(
                f"    {field['column']} VARCHAR2({field['length']} CHAR)"
            )
    definitions.append(
        f"    CONSTRAINT PK_{data['table']} PRIMARY KEY ({data['primary_key']})"
    )
    return (
        "-- Generated from model/customer.yaml. Run as the APEX parsing schema.\n"
        "-- This script does not alter an existing table.\n"
        f"CREATE TABLE {data['table']} (\n"
        + ",\n".join(definitions)
        + "\n);\n"
    )


def _page_item_id(index):
    return APEX_ID_BASE + 100 + index


def _field_apex_item_name(field):
    return f"P2_{field['name']}"


def _render_page_items(data, region_id):
    statements = []
    for index, field in enumerate(data["fields"], start=1):
        is_key = field["column"] == data["primary_key"]
        display = "NATIVE_HIDDEN" if is_key else (
            "NATIVE_NUMBER_FIELD" if field["type"] == "number" else "NATIVE_TEXT_FIELD"
        )
        attributes = [
            "wwv_flow_api.create_page_item(",
            f" p_id=>wwv_flow_api.id({_page_item_id(index)})",
            f",p_name=>{_sql_literal(_field_apex_item_name(field))}",
            f",p_item_sequence=>{index * 10}",
            f",p_item_plug_id=>wwv_flow_api.id({region_id})",
            f",p_prompt=>{_sql_literal(field['label'])}",
            ",p_display_as=>" + _sql_literal(display),
            f",p_field_template=>wwv_flow_api.id({APEX_ID_BASE + 4})",
            ",p_item_template_options=>'#DEFAULT#'",
        ]
        if field["type"] == "text" and not is_key:
            attributes.extend(
                [
                    f",p_cSize=>{min(field['length'], 60)}",
                    f",p_cMaxlength=>{field['length']}",
                    ",p_attribute_01=>'N'",
                    ",p_attribute_02=>'N'",
                    ",p_attribute_04=>'TEXT'",
                    ",p_attribute_05=>'NONE'",
                ]
            )
        elif field["type"] == "number" and not is_key:
            attributes.extend(
                [",p_cSize=>20", ",p_attribute_03=>'right'"]
            )
        attributes.append(");")
        statements.append("\n".join(attributes))
    return "\n".join(statements)


def _render_application(data):
    field_by_column = {field["column"]: field for field in data["fields"]}
    key_field = field_by_column[data["primary_key"]]
    key_item = _field_apex_item_name(key_field)
    user_columns = [field for field in data["fields"] if field["column"] != data["primary_key"]]
    button = data["buttons"][0]
    app_name = data["title"]
    app_id = data["application_id"]
    theme_id = data["theme_id"]
    ui_id = APEX_ID_BASE + 1
    theme_record_id = APEX_ID_BASE + 6
    authentication_id = APEX_ID_BASE + 7
    page_template_id = APEX_ID_BASE + 2
    region_template_id = APEX_ID_BASE + 3
    field_template_id = APEX_ID_BASE + 4
    button_template_id = APEX_ID_BASE + 5
    list_region_id = APEX_ID_BASE + 10
    form_region_id = APEX_ID_BASE + 11
    save_button_id = APEX_ID_BASE + 20
    greeting_button_id = APEX_ID_BASE + 21
    load_process_id = APEX_ID_BASE + 30
    save_process_id = APEX_ID_BASE + 31
    greeting_process_id = APEX_ID_BASE + 32

    list_source = [
        "declare",
        "  l_url varchar2(4000);",
        "begin",
        "  htp.p('<p><a class=\"t-Button t-Button--hot\" href=\"' ||",
        "         apex_util.prepare_url('f?p=' || :APP_ID || ':2:' || :APP_SESSION || '::NO::') ||",
        "         '\">Nouveau client</a></p>');",
        "  htp.p('<table class=\"t-Report-report\"><thead><tr>');",
    ]
    for field in data["fields"]:
        list_source.append(f"  htp.p('<th>' || apex_escape.html({_sql_literal(field['label'])}) || '</th>');")
    list_source.extend(
        [
            "  htp.p('<th>Action</th></tr></thead><tbody>');",
            f"  for r in (select {', '.join(field['column'] for field in data['fields'])} from {data['table']} order by {data['primary_key']}) loop",
            f"    l_url := apex_util.prepare_url('f?p=' || :APP_ID || ':2:' || :APP_SESSION || '::NO::{key_item}:' || to_char(r.{data['primary_key']}));",
            "    htp.p('<tr>');",
        ]
    )
    for field in data["fields"]:
        if field["type"] == "number":
            value = f"apex_escape.html(to_char(r.{field['column']}))"
        else:
            value = f"apex_escape.html(r.{field['column']})"
        list_source.append(f"    htp.p('<td>' || {value} || '</td>');")
    list_source.extend(
        [
            "    htp.p('<td><a class=\"t-Button t-Button--small\" href=\"' || apex_escape.html_attribute(l_url) || '\">Modifier</a></td></tr>');",
            "  end loop;",
            "  htp.p('</tbody></table>');",
            "end;",
        ]
    )

    load_lines = [
        "begin",
        f"  if :{key_item} is not null then",
        f"    select {', '.join(field['column'] for field in data['fields'])}",
        f"      into {', '.join(':' + _field_apex_item_name(field) for field in data['fields'])}",
        f"      from {data['table']} where {data['primary_key']} = :{key_item};",
        "  end if;",
        "end;",
    ]
    insert_columns = ", ".join(field["column"] for field in user_columns)
    insert_values = ", ".join(":" + _field_apex_item_name(field) for field in user_columns)
    update_lines = [
        f"        {field['column']} = :{_field_apex_item_name(field)}"
        for field in user_columns
    ]
    save_lines = [
        "begin",
        f"  if :{key_item} is null then",
        f"    insert into {data['table']} ({insert_columns})",
        f"    values ({insert_values})",
        f"    returning {data['primary_key']} into :{key_item};",
        "  else",
        f"    update {data['table']} set",
        *update_lines,
        f"      where {data['primary_key']} = :{key_item};",
        "  end if;",
        "  apex_application.g_print_success_message := 'Client enregistré.';",
        "end;",
    ]
    greet_field = next(
        (field for field in data["fields"] if field["type"] == "text" and field["column"] != data["primary_key"]),
        None,
    )
    greet_item = _field_apex_item_name(greet_field) if greet_field else key_item
    greeting_lines = [
        "begin",
        f"  apex_application.g_print_success_message := 'Bonjour ' || apex_escape.html(nvl(:{greet_item}, '')) || ' !';",
        "end;",
    ]

    sql = [
        "-- Oracle APEX 18.2 application export generated from customer.yaml.",
        "-- Import through APEX App Builder in a workspace whose parsing schema owns CLIENTS.",
        "-- Static generation only: validate this export in an installed APEX 18.2 instance before production use.",
        "prompt --application/set_environment",
        "set define off verify off feedback off",
        "begin",
        "wwv_flow_api.import_begin (",
        f" p_version_yyyy_mm_dd=>{_sql_literal(data['version_date'])}",
        f",p_release=>{_sql_literal(data['release'])}",
        ",p_default_workspace_id=>nvl(wwv_flow_application_install.get_workspace_id,0)",
        f",p_default_application_id=>{app_id}",
        ",p_default_owner=>user",
        ");",
        "end;",
        "/",
        "begin",
        "wwv_flow_api.remove_flow(wwv_flow.g_flow_id);",
        "end;",
        "/",
        "begin",
        "wwv_flow_api.create_flow(",
        " p_id=>wwv_flow.g_flow_id",
        f",p_display_id=>nvl(wwv_flow_application_install.get_application_id,{app_id})",
        ",p_owner=>nvl(wwv_flow_application_install.get_schema,user)",
        f",p_name=>nvl(wwv_flow_application_install.get_application_name,{_sql_literal(app_name)})",
        f",p_alias=>nvl(wwv_flow_application_install.get_application_alias,{_sql_literal(data['application_alias'])})",
        ",p_page_view_logging=>'YES'",
        ",p_compatibility_mode=>'5.1'",
        ",p_flow_language=>'fr'",
        ",p_flow_language_derived_from=>'FLOW_PRIMARY_LANGUAGE'",
        ",p_authentication=>'PLUGIN'",
        f",p_authentication_id=>wwv_flow_api.id({authentication_id})",
        ",p_application_tab_set=>1",
        ",p_ui_type_name=>null",
        f",p_theme_id=>{theme_id}",
        ",p_flow_status=>'AVAILABLE_W_EDIT_LINK'",
        ",p_auto_time_zone=>'N'",
        ");",
        "end;",
        "/",
        "begin",
        "wwv_flow_api.create_theme(",
        f" p_id=>wwv_flow_api.id({theme_record_id})",
        f",p_theme_id=>{theme_id}",
        ",p_theme_name=>'Universal Theme'",
        ",p_theme_internal_name=>'UNIVERSAL_THEME'",
        ",p_ui_type_name=>'DESKTOP'",
        ",p_navigation_type=>'L'",
        ",p_nav_bar_type=>'NAVBAR'",
        ",p_is_locked=>false",
        f",p_default_page_template=>wwv_flow_api.id({page_template_id})",
        f",p_default_dialog_template=>wwv_flow_api.id({page_template_id})",
        f",p_default_region_template=>wwv_flow_api.id({region_template_id})",
        f",p_default_button_template=>wwv_flow_api.id({button_template_id})",
        ");",
        "wwv_flow_api.create_template(",
        f" p_id=>wwv_flow_api.id({page_template_id})",
        f",p_theme_id=>{theme_id}",
        ",p_name=>'Clients Page'",
        ",p_internal_name=>'CLIENTS_PAGE'",
        ",p_is_popup=>false",
        f",p_header_template=>{_sql_literal('<!doctype html><html lang="#BROWSER_LANGUAGE#"><head><meta charset="utf-8"><title>#TITLE#</title>#APEX_CSS##THEME_CSS##HEAD#</head><body>#FORM_OPEN#')}",
        f",p_box=>{_sql_literal('<main class="t-Body">#REGION_POSITION_01##BODY#</main>')}",
        f",p_footer_template=>{_sql_literal('#FORM_CLOSE##APEX_JAVASCRIPT##THEME_JAVASCRIPT#</body></html>')}",
        ",p_theme_class_id=>1",
        ");",
        "wwv_flow_api.create_plug_template(",
        f" p_id=>wwv_flow_api.id({region_template_id})",
        f",p_theme_id=>{theme_id}",
        ",p_page_plug_template_name=>'Clients Region'",
        ",p_internal_name=>'CLIENTS_REGION'",
        ",p_template=>'<section class=\"t-Region\"><h2>#TITLE#</h2><div class=\"t-Region-body\">#BODY#</div></section>'",
        ",p_template2=>null",
        ",p_theme_class_id=>1",
        ");",
        "wwv_flow_api.create_button_templates(",
        f" p_id=>wwv_flow_api.id({button_template_id})",
        ",p_theme_id=>42",
        ",p_template_name=>'Text'",
        ",p_internal_name=>'TEXT'",
        ",p_template=>'<button class=\"t-Button #BUTTON_CSS_CLASSES#\" type=\"button\" #BUTTON_ATTRIBUTES# id=\"#BUTTON_ID#\"><span class=\"t-Button-label\">#LABEL#</span></button>'",
        ",p_hot_template=>'<button class=\"t-Button t-Button--hot #BUTTON_CSS_CLASSES#\" type=\"button\" #BUTTON_ATTRIBUTES# id=\"#BUTTON_ID#\"><span class=\"t-Button-label\">#LABEL#</span></button>'",
        ",p_translate_this_template=>'N'",
        ",p_theme_class_id=>1",
        ");",
        "wwv_flow_api.create_field_template(",
        f" p_id=>wwv_flow_api.id({field_template_id})",
        ",p_template_name=>'Client Label'",
        ",p_internal_name=>'CLIENT_LABEL'",
        ",p_template_body1=>'<div class=\"t-Form-labelContainer\"><label for=\"#CURRENT_ITEM_NAME#\" id=\"#LABEL_ID#\" class=\"t-Form-label\">'",
        ",p_template_body2=>'</label></div>'",
        ",p_before_item=>'<div class=\"t-Form-fieldContainer\">'",
        ",p_after_item=>'</div>'",
        ",p_before_element=>'<div class=\"t-Form-inputContainer\">'",
        ",p_after_element=>'</div>'",
        ",p_error_template=>'<span class=\"t-Form-error\">#ERROR_MESSAGE#</span>'",
        f",p_theme_id=>{theme_id}",
        ",p_theme_class_id=>3",
        ",p_translate_this_template=>'N'",
        ");",
        "wwv_flow_api.create_user_interface(",
        f" p_id=>wwv_flow_api.id({ui_id})",
        ",p_ui_type_name=>'DESKTOP'",
        ",p_display_name=>'Desktop'",
        ",p_display_seq=>10",
        ",p_use_auto_detect=>true",
        ",p_is_default=>true",
        f",p_theme_id=>{theme_id}",
        ",p_home_url=>'f?p=&APP_ID.:1:&SESSION.'",
        ",p_theme_style_by_user_pref=>false",
        ",p_global_page_id=>null",
        ",p_navigation_list_position=>'SIDE'",
        ",p_include_legacy_javascript=>'PRE18:18'",
        ",p_nav_bar_type=>'NAVBAR'",
        ");",
        "wwv_flow_api.create_authentication(",
        f" p_id=>wwv_flow_api.id({authentication_id})",
        ",p_name=>'No Authentication'",
        ",p_scheme_type=>'NATIVE_DAD'",
        f",p_attribute_15=>'{authentication_id}'",
        ",p_invalid_session_type=>'LOGIN'",
        ",p_use_secure_cookie_yn=>'N'",
        ",p_ras_mode=>0",
        ");",
        "end;",
        "/",
    ]

    sql.extend(
        [
            "begin",
            "wwv_flow_api.create_page(",
            " p_id=>1",
            f",p_user_interface_id=>wwv_flow_api.id({ui_id})",
            ",p_name=>'Clients'",
            ",p_alias=>'CLIENTS'",
            f",p_step_title=>{_sql_literal(app_name)}",
            ",p_reload_on_submit=>'A'",
            ",p_warn_on_unsaved_changes=>'N'",
            ",p_step_sub_title_type=>'TEXT_WITH_SUBSTITUTIONS'",
            ",p_autocomplete_on_off=>'ON'",
            f",p_step_template=>wwv_flow_api.id({page_template_id})",
            ",p_page_template_options=>'#DEFAULT#'",
            ");",
            "wwv_flow_api.create_page_plug(",
            f" p_id=>wwv_flow_api.id({list_region_id})",
            ",p_plug_name=>'Clients'",
            f",p_plug_template=>wwv_flow_api.id({region_template_id})",
            ",p_plug_display_sequence=>10",
            ",p_plug_display_point=>'REGION_POSITION_01'",
            ",p_plug_source_type=>'NATIVE_PLSQL'",
            f",p_plug_source=>{_varchar2_join(list_source)}",
            ",p_attribute_01=>'N'",
            ",p_attribute_02=>'TEXT'",
            ");",
            "end;",
            "/",
            "begin",
            "wwv_flow_api.create_page(",
            " p_id=>2",
            f",p_user_interface_id=>wwv_flow_api.id({ui_id})",
            ",p_name=>'Client'",
            ",p_alias=>'CLIENT'",
            f",p_step_title=>{_sql_literal(app_name)}",
            ",p_reload_on_submit=>'A'",
            ",p_warn_on_unsaved_changes=>'N'",
            ",p_step_sub_title_type=>'TEXT_WITH_SUBSTITUTIONS'",
            ",p_autocomplete_on_off=>'ON'",
            f",p_step_template=>wwv_flow_api.id({page_template_id})",
            ",p_page_template_options=>'#DEFAULT#'",
            ");",
            "wwv_flow_api.create_page_plug(",
            f" p_id=>wwv_flow_api.id({form_region_id})",
            ",p_plug_name=>'Client details'",
            f",p_plug_template=>wwv_flow_api.id({region_template_id})",
            ",p_plug_display_sequence=>10",
            ",p_plug_display_point=>'REGION_POSITION_01'",
            ",p_plug_source_type=>'NATIVE_STATIC'",
            ",p_attribute_01=>'N'",
            ",p_attribute_02=>'TEXT'",
            ");",
            _render_page_items(data, form_region_id),
            "wwv_flow_api.create_page_button(",
            f" p_id=>wwv_flow_api.id({save_button_id})",
            ",p_button_sequence=>10",
            f",p_button_plug_id=>wwv_flow_api.id({form_region_id})",
            ",p_button_name=>'SAVE_CLIENT'",
            ",p_button_action=>'SUBMIT'",
            ",p_button_template_options=>'#DEFAULT#'",
            f",p_button_template_id=>wwv_flow_api.id({button_template_id})",
            ",p_button_image_alt=>'Enregistrer'",
            ",p_button_position=>'REGION_TEMPLATE_NEXT'",
            ",p_grid_new_grid=>false",
            ");",
            "wwv_flow_api.create_page_button(",
            f" p_id=>wwv_flow_api.id({greeting_button_id})",
            ",p_button_sequence=>20",
            f",p_button_plug_id=>wwv_flow_api.id({form_region_id})",
            f",p_button_name=>{_sql_literal(button['name'])}",
            ",p_button_action=>'SUBMIT'",
            ",p_button_template_options=>'#DEFAULT#'",
            f",p_button_template_id=>wwv_flow_api.id({button_template_id})",
            f",p_button_image_alt=>{_sql_literal(button['label'])}",
            ",p_button_position=>'REGION_TEMPLATE_NEXT'",
            ",p_grid_new_grid=>false",
            ");",
            "wwv_flow_api.create_page_process(",
            f" p_id=>wwv_flow_api.id({load_process_id})",
            ",p_process_sequence=>10",
            ",p_process_point=>'BEFORE_HEADER'",
            ",p_process_type=>'NATIVE_PLSQL'",
            ",p_process_name=>'Load client'",
            f",p_process_sql_clob=>{_varchar2_join(load_lines)}",
            ");",
            "wwv_flow_api.create_page_process(",
            f" p_id=>wwv_flow_api.id({save_process_id})",
            ",p_process_sequence=>10",
            ",p_process_point=>'AFTER_SUBMIT'",
            ",p_process_type=>'NATIVE_PLSQL'",
            ",p_process_name=>'Save client'",
            f",p_process_sql_clob=>{_varchar2_join(save_lines)}",
            f",p_process_when_button_id=>wwv_flow_api.id({save_button_id})",
            ");",
            "wwv_flow_api.create_page_process(",
            f" p_id=>wwv_flow_api.id({greeting_process_id})",
            ",p_process_sequence=>20",
            ",p_process_point=>'AFTER_SUBMIT'",
            ",p_process_type=>'NATIVE_PLSQL'",
            ",p_process_name=>'Greet client'",
            f",p_process_sql_clob=>{_varchar2_join(greeting_lines)}",
            f",p_process_when_button_id=>wwv_flow_api.id({greeting_button_id})",
            ");",
            "end;",
            "/",
            "begin",
            "wwv_flow_api.import_end;",
            "commit;",
            "end;",
            "/",
        ]
    )
    return "\n".join(sql) + "\n"


def generate_bundle(model_path, config_path, output_dir):
    model = _load_yaml(model_path, "Customer model")
    config = _load_yaml(config_path, "Plugin configuration")
    data = _prepare(model, config)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    schema_path = output_dir / "01_create_clients_table.sql"
    application_path = output_dir / "02_clients_apex_18_2.sql"
    schema_path.write_text(_render_schema(data), encoding="utf-8")
    application_path.write_text(_render_application(data), encoding="utf-8")
    return {"schema": schema_path, "application": application_path}


def main():
    parser = argparse.ArgumentParser(description="Generate an Oracle APEX 18.2 client app bundle")
    parser.add_argument("--model", default="model/customer.yaml")
    parser.add_argument("--config", default="adapters/oracle-apex/plugin.yaml")
    parser.add_argument("--output", default="generated/oracle-apex")
    args = parser.parse_args()
    outputs = generate_bundle(args.model, args.config, args.output)
    for kind, path in outputs.items():
        print(f"{kind}: {path}")


if __name__ == "__main__":
    main()