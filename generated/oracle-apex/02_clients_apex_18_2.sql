-- Oracle APEX 18.2 application export generated from customer.yaml.
-- Import through APEX App Builder in a workspace whose parsing schema owns CLIENTS.
-- Static generation only: validate this export in an installed APEX 18.2 instance before production use.
prompt --application/set_environment
set define off verify off feedback off
begin
wwv_flow_api.import_begin (
 p_version_yyyy_mm_dd=>'2018.05.24'
,p_release=>'18.2.0.00.12'
,p_default_workspace_id=>nvl(wwv_flow_application_install.get_workspace_id,0)
,p_default_application_id=>9010
,p_default_owner=>user
);
end;
/
begin
wwv_flow_api.remove_flow(wwv_flow.g_flow_id);
end;
/
begin
wwv_flow_api.create_flow(
 p_id=>wwv_flow.g_flow_id
,p_display_id=>nvl(wwv_flow_application_install.get_application_id,9010)
,p_owner=>nvl(wwv_flow_application_install.get_schema,user)
,p_name=>nvl(wwv_flow_application_install.get_application_name,'Gestion des clients')
,p_alias=>nvl(wwv_flow_application_install.get_application_alias,'CLIENTS_APP')
,p_page_view_logging=>'YES'
,p_compatibility_mode=>'5.1'
,p_flow_language=>'fr'
,p_flow_language_derived_from=>'FLOW_PRIMARY_LANGUAGE'
,p_authentication=>'PLUGIN'
,p_authentication_id=>wwv_flow_api.id(910000000000000007)
,p_application_tab_set=>1
,p_ui_type_name=>null
,p_theme_id=>42
,p_flow_status=>'AVAILABLE_W_EDIT_LINK'
,p_auto_time_zone=>'N'
);
end;
/
begin
wwv_flow_api.create_theme(
 p_id=>wwv_flow_api.id(910000000000000006)
,p_theme_id=>42
,p_theme_name=>'Universal Theme'
,p_theme_internal_name=>'UNIVERSAL_THEME'
,p_ui_type_name=>'DESKTOP'
,p_navigation_type=>'L'
,p_nav_bar_type=>'NAVBAR'
,p_is_locked=>false
,p_default_page_template=>wwv_flow_api.id(910000000000000002)
,p_default_dialog_template=>wwv_flow_api.id(910000000000000002)
,p_default_region_template=>wwv_flow_api.id(910000000000000003)
,p_default_button_template=>wwv_flow_api.id(910000000000000005)
);
wwv_flow_api.create_template(
 p_id=>wwv_flow_api.id(910000000000000002)
,p_theme_id=>42
,p_name=>'Clients Page'
,p_internal_name=>'CLIENTS_PAGE'
,p_is_popup=>false
,p_header_template=>'<!doctype html><html lang="#BROWSER_LANGUAGE#"><head><meta charset="utf-8"><title>#TITLE#</title>#APEX_CSS##THEME_CSS##HEAD#</head><body>#FORM_OPEN#'
,p_box=>'<main class="t-Body">#REGION_POSITION_01##BODY#</main>'
,p_footer_template=>'#FORM_CLOSE##APEX_JAVASCRIPT##THEME_JAVASCRIPT#</body></html>'
,p_theme_class_id=>1
);
wwv_flow_api.create_plug_template(
 p_id=>wwv_flow_api.id(910000000000000003)
,p_theme_id=>42
,p_page_plug_template_name=>'Clients Region'
,p_internal_name=>'CLIENTS_REGION'
,p_template=>'<section class="t-Region"><h2>#TITLE#</h2><div class="t-Region-body">#BODY#</div></section>'
,p_template2=>null
,p_theme_class_id=>1
);
wwv_flow_api.create_button_templates(
 p_id=>wwv_flow_api.id(910000000000000005)
,p_theme_id=>42
,p_template_name=>'Text'
,p_internal_name=>'TEXT'
,p_template=>'<button class="t-Button #BUTTON_CSS_CLASSES#" type="button" #BUTTON_ATTRIBUTES# id="#BUTTON_ID#"><span class="t-Button-label">#LABEL#</span></button>'
,p_hot_template=>'<button class="t-Button t-Button--hot #BUTTON_CSS_CLASSES#" type="button" #BUTTON_ATTRIBUTES# id="#BUTTON_ID#"><span class="t-Button-label">#LABEL#</span></button>'
,p_translate_this_template=>'N'
,p_theme_class_id=>1
);
wwv_flow_api.create_field_template(
 p_id=>wwv_flow_api.id(910000000000000004)
,p_template_name=>'Client Label'
,p_internal_name=>'CLIENT_LABEL'
,p_template_body1=>'<div class="t-Form-labelContainer"><label for="#CURRENT_ITEM_NAME#" id="#LABEL_ID#" class="t-Form-label">'
,p_template_body2=>'</label></div>'
,p_before_item=>'<div class="t-Form-fieldContainer">'
,p_after_item=>'</div>'
,p_before_element=>'<div class="t-Form-inputContainer">'
,p_after_element=>'</div>'
,p_error_template=>'<span class="t-Form-error">#ERROR_MESSAGE#</span>'
,p_theme_id=>42
,p_theme_class_id=>3
,p_translate_this_template=>'N'
);
wwv_flow_api.create_user_interface(
 p_id=>wwv_flow_api.id(910000000000000001)
,p_ui_type_name=>'DESKTOP'
,p_display_name=>'Desktop'
,p_display_seq=>10
,p_use_auto_detect=>true
,p_is_default=>true
,p_theme_id=>42
,p_home_url=>'f?p=&APP_ID.:1:&SESSION.'
,p_theme_style_by_user_pref=>false
,p_global_page_id=>null
,p_navigation_list_position=>'SIDE'
,p_include_legacy_javascript=>'PRE18:18'
,p_nav_bar_type=>'NAVBAR'
);
wwv_flow_api.create_authentication(
 p_id=>wwv_flow_api.id(910000000000000007)
,p_name=>'No Authentication'
,p_scheme_type=>'NATIVE_DAD'
,p_attribute_15=>'910000000000000007'
,p_invalid_session_type=>'LOGIN'
,p_use_secure_cookie_yn=>'N'
,p_ras_mode=>0
);
end;
/
begin
wwv_flow_api.create_page(
 p_id=>1
,p_user_interface_id=>wwv_flow_api.id(910000000000000001)
,p_name=>'Clients'
,p_alias=>'CLIENTS'
,p_step_title=>'Gestion des clients'
,p_reload_on_submit=>'A'
,p_warn_on_unsaved_changes=>'N'
,p_step_sub_title_type=>'TEXT_WITH_SUBSTITUTIONS'
,p_autocomplete_on_off=>'ON'
,p_step_template=>wwv_flow_api.id(910000000000000002)
,p_page_template_options=>'#DEFAULT#'
);
wwv_flow_api.create_page_plug(
 p_id=>wwv_flow_api.id(910000000000000010)
,p_plug_name=>'Clients'
,p_plug_template=>wwv_flow_api.id(910000000000000003)
,p_plug_display_sequence=>10
,p_plug_display_point=>'REGION_POSITION_01'
,p_plug_source_type=>'NATIVE_PLSQL'
,p_plug_source=>wwv_flow_string.join(wwv_flow_t_varchar2(
    'declare',
    '  l_url varchar2(4000);',
    'begin',
    '  htp.p(''<p><a class="t-Button t-Button--hot" href="'' ||',
    '         apex_util.prepare_url(''f?p='' || :APP_ID || '':2:'' || :APP_SESSION || ''::NO::'') ||',
    '         ''">Nouveau client</a></p>'');',
    '  htp.p(''<table class="t-Report-report"><thead><tr>'');',
    '  htp.p(''<th>'' || apex_escape.html(''Id Client2'') || ''</th>'');',
    '  htp.p(''<th>'' || apex_escape.html(''Nom du client'') || ''</th>'');',
    '  htp.p(''<th>'' || apex_escape.html(''Email'') || ''</th>'');',
    '  htp.p(''<th>Action</th></tr></thead><tbody>'');',
    '  for r in (select ID_CLIENT, NOM_CLIENT, EMAIL from CLIENTS order by ID_CLIENT) loop',
    '    l_url := apex_util.prepare_url(''f?p='' || :APP_ID || '':2:'' || :APP_SESSION || ''::NO::P2_ID_CLIENT2:'' || to_char(r.ID_CLIENT));',
    '    htp.p(''<tr>'');',
    '    htp.p(''<td>'' || apex_escape.html(to_char(r.ID_CLIENT)) || ''</td>'');',
    '    htp.p(''<td>'' || apex_escape.html(r.NOM_CLIENT) || ''</td>'');',
    '    htp.p(''<td>'' || apex_escape.html(r.EMAIL) || ''</td>'');',
    '    htp.p(''<td><a class="t-Button t-Button--small" href="'' || apex_escape.html_attribute(l_url) || ''">Modifier</a></td></tr>'');',
    '  end loop;',
    '  htp.p(''</tbody></table>'');',
    'end;'))
,p_attribute_01=>'N'
,p_attribute_02=>'TEXT'
);
end;
/
begin
wwv_flow_api.create_page(
 p_id=>2
,p_user_interface_id=>wwv_flow_api.id(910000000000000001)
,p_name=>'Client'
,p_alias=>'CLIENT'
,p_step_title=>'Gestion des clients'
,p_reload_on_submit=>'A'
,p_warn_on_unsaved_changes=>'N'
,p_step_sub_title_type=>'TEXT_WITH_SUBSTITUTIONS'
,p_autocomplete_on_off=>'ON'
,p_step_template=>wwv_flow_api.id(910000000000000002)
,p_page_template_options=>'#DEFAULT#'
);
wwv_flow_api.create_page_plug(
 p_id=>wwv_flow_api.id(910000000000000011)
,p_plug_name=>'Client details'
,p_plug_template=>wwv_flow_api.id(910000000000000003)
,p_plug_display_sequence=>10
,p_plug_display_point=>'REGION_POSITION_01'
,p_plug_source_type=>'NATIVE_STATIC'
,p_attribute_01=>'N'
,p_attribute_02=>'TEXT'
);
wwv_flow_api.create_page_item(
 p_id=>wwv_flow_api.id(910000000000000101)
,p_name=>'P2_ID_CLIENT2'
,p_item_sequence=>10
,p_item_plug_id=>wwv_flow_api.id(910000000000000011)
,p_prompt=>'Id Client2'
,p_display_as=>'NATIVE_HIDDEN'
,p_field_template=>wwv_flow_api.id(910000000000000004)
,p_item_template_options=>'#DEFAULT#'
);
wwv_flow_api.create_page_item(
 p_id=>wwv_flow_api.id(910000000000000102)
,p_name=>'P2_NOM_CLIENT2'
,p_item_sequence=>20
,p_item_plug_id=>wwv_flow_api.id(910000000000000011)
,p_prompt=>'Nom du client'
,p_display_as=>'NATIVE_TEXT_FIELD'
,p_field_template=>wwv_flow_api.id(910000000000000004)
,p_item_template_options=>'#DEFAULT#'
,p_cSize=>60
,p_cMaxlength=>120
,p_attribute_01=>'N'
,p_attribute_02=>'N'
,p_attribute_04=>'TEXT'
,p_attribute_05=>'NONE'
);
wwv_flow_api.create_page_item(
 p_id=>wwv_flow_api.id(910000000000000103)
,p_name=>'P2_EMAIL'
,p_item_sequence=>30
,p_item_plug_id=>wwv_flow_api.id(910000000000000011)
,p_prompt=>'Email'
,p_display_as=>'NATIVE_TEXT_FIELD'
,p_field_template=>wwv_flow_api.id(910000000000000004)
,p_item_template_options=>'#DEFAULT#'
,p_cSize=>60
,p_cMaxlength=>200
,p_attribute_01=>'N'
,p_attribute_02=>'N'
,p_attribute_04=>'TEXT'
,p_attribute_05=>'NONE'
);
wwv_flow_api.create_page_button(
 p_id=>wwv_flow_api.id(910000000000000020)
,p_button_sequence=>10
,p_button_plug_id=>wwv_flow_api.id(910000000000000011)
,p_button_name=>'SAVE_CLIENT'
,p_button_action=>'SUBMIT'
,p_button_template_options=>'#DEFAULT#'
,p_button_template_id=>wwv_flow_api.id(910000000000000005)
,p_button_image_alt=>'Enregistrer'
,p_button_position=>'REGION_TEMPLATE_NEXT'
,p_grid_new_grid=>false
);
wwv_flow_api.create_page_button(
 p_id=>wwv_flow_api.id(910000000000000021)
,p_button_sequence=>20
,p_button_plug_id=>wwv_flow_api.id(910000000000000011)
,p_button_name=>'BTN_BONJOUR'
,p_button_action=>'SUBMIT'
,p_button_template_options=>'#DEFAULT#'
,p_button_template_id=>wwv_flow_api.id(910000000000000005)
,p_button_image_alt=>'Dire bonjour'
,p_button_position=>'REGION_TEMPLATE_NEXT'
,p_grid_new_grid=>false
);
wwv_flow_api.create_page_process(
 p_id=>wwv_flow_api.id(910000000000000030)
,p_process_sequence=>10
,p_process_point=>'BEFORE_HEADER'
,p_process_type=>'NATIVE_PLSQL'
,p_process_name=>'Load client'
,p_process_sql_clob=>wwv_flow_string.join(wwv_flow_t_varchar2(
    'begin',
    '  if :P2_ID_CLIENT2 is not null then',
    '    select ID_CLIENT, NOM_CLIENT, EMAIL',
    '      into :P2_ID_CLIENT2, :P2_NOM_CLIENT2, :P2_EMAIL',
    '      from CLIENTS where ID_CLIENT = :P2_ID_CLIENT2;',
    '  end if;',
    'end;'))
);
wwv_flow_api.create_page_process(
 p_id=>wwv_flow_api.id(910000000000000031)
,p_process_sequence=>10
,p_process_point=>'AFTER_SUBMIT'
,p_process_type=>'NATIVE_PLSQL'
,p_process_name=>'Save client'
,p_process_sql_clob=>wwv_flow_string.join(wwv_flow_t_varchar2(
    'begin',
    '  if :P2_ID_CLIENT2 is null then',
    '    insert into CLIENTS (NOM_CLIENT, EMAIL)',
    '    values (:P2_NOM_CLIENT2, :P2_EMAIL)',
    '    returning ID_CLIENT into :P2_ID_CLIENT2;',
    '  else',
    '    update CLIENTS set',
    '        NOM_CLIENT = :P2_NOM_CLIENT2',
    '        EMAIL = :P2_EMAIL',
    '      where ID_CLIENT = :P2_ID_CLIENT2;',
    '  end if;',
    '  apex_application.g_print_success_message := ''Client enregistré.'';',
    'end;'))
,p_process_when_button_id=>wwv_flow_api.id(910000000000000020)
);
wwv_flow_api.create_page_process(
 p_id=>wwv_flow_api.id(910000000000000032)
,p_process_sequence=>20
,p_process_point=>'AFTER_SUBMIT'
,p_process_type=>'NATIVE_PLSQL'
,p_process_name=>'Greet client'
,p_process_sql_clob=>wwv_flow_string.join(wwv_flow_t_varchar2(
    'begin',
    '  apex_application.g_print_success_message := ''Bonjour '' || apex_escape.html(nvl(:P2_NOM_CLIENT2, '''')) || '' !'';',
    'end;'))
,p_process_when_button_id=>wwv_flow_api.id(910000000000000021)
);
end;
/
begin
wwv_flow_api.import_end;
commit;
end;
/
