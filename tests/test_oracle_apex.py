import importlib.util
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "adapters/oracle-apex/generator/generate.py"
spec = importlib.util.spec_from_file_location("oracle_apex_generator", MODULE)
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


def test_generates_client_schema_and_apex_application(tmp_path):
    outputs = generator.generate_bundle(
        ROOT / "model/customer.yaml",
        ROOT / "adapters/oracle-apex/plugin.yaml",
        tmp_path,
    )

    assert set(outputs) == {"schema", "application"}
    schema = outputs["schema"].read_text(encoding="utf-8")
    application = outputs["application"].read_text(encoding="utf-8")

    assert "CREATE TABLE CLIENTS" in schema
    assert "ID_CLIENT NUMBER" in schema
    assert "NOM_CLIENT VARCHAR2(120 CHAR)" in schema
    assert "EMAIL VARCHAR2(200 CHAR)" in schema
    assert "p_release=>'18.2.0.00.12'" in application
    assert "wwv_flow_api.import_begin" in application
    flow_start = application.index("wwv_flow_api.create_flow(")
    flow_end = application.index("\n);", flow_start)
    flow = application[flow_start:flow_end]
    assert ",p_application_tab_set=>1" in flow
    assert ",p_authentication=>'PLUGIN'" in flow
    assert ",p_authentication_id=>wwv_flow_api.id(910000000000000007)" in flow
    assert ",p_ui_type_name=>null" in flow
    assert ",p_theme_id=>42" in flow
    assert "wwv_flow_api.create_authentication(" in application
    assert ",p_scheme_type=>'NATIVE_DAD'" in application
    assert ",p_attribute_15=>'910000000000000007'" in application
    assert "wwv_flow_api.create_user_interface(" in application
    assert "p_theme_id=>42" in application
    assert ",p_global_page_id=>null" in application
    assert ",p_page_plug_template_name=>'Clients Region'" in application
    assert "#TAIL#" not in application
    assert "Clients" in application
    assert "NOM_CLIENT2" in application
    assert "BTN_BONJOUR" in application
    assert "'        NOM_CLIENT = :P2_NOM_CLIENT2'," in application
    assert "'        EMAIL = :P2_EMAIL'," in application
    assert ",\n        EMAIL = :P2_EMAIL'" not in application


def test_rejects_field_without_required_type(tmp_path):
    model_path = tmp_path / "customer.yaml"
    model_path.write_text(
        "form:\n"
        "  name: HELLO_WORLD\n"
        "  title: Gestion des clients\n"
        "  fields:\n"
        "    - name: NOM_CLIENT\n"
        "      label: Nom du client\n"
        "  buttons:\n"
        "    - name: BTN_BONJOUR\n"
        "      label: Dire bonjour\n",
        encoding="utf-8",
    )
    config_path = ROOT / "adapters/oracle-apex/plugin.yaml"

    with pytest.raises(ValueError, match="type"):
        generator.generate_bundle(model_path, config_path, tmp_path / "out")


def test_escapes_model_labels_in_generated_sql(tmp_path):
    model = yaml.safe_load((ROOT / "model/customer.yaml").read_text(encoding="utf-8"))
    model["form"]["buttons"][0]["label"] = "Dire l'été"
    model_path = tmp_path / "customer.yaml"
    model_path.write_text(yaml.safe_dump(model, allow_unicode=True), encoding="utf-8")

    outputs = generator.generate_bundle(
        model_path,
        ROOT / "adapters/oracle-apex/plugin.yaml",
        tmp_path / "out",
    )
    application = outputs["application"].read_text(encoding="utf-8")

    assert "Dire l''été" in application