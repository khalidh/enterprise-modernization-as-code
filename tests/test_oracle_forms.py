
import importlib.util
import xml.etree.ElementTree as ET
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]

MODULE = (
    ROOT / "adapters/oracle-forms"
    / "generator/generate.py"
)

spec = importlib.util.spec_from_file_location(
    "forms_generator", MODULE
)
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)

def test_valid_names():
    assert generator.valid_name("NOM_CLIENT")
    assert not generator.valid_name("NOM CLIENT")
    assert not generator.valid_name("1CLIENT")

def test_generation_requires_field_type(tmp_path):
    model = tmp_path / "customer.yaml"
    template = tmp_path / "template.xml"
    output = tmp_path / "result.xml"

    model.write_text(
        "form:\n"
        "  name: HELLO_WORLD\n"
        "  fields:\n"
        "    - name: NOM_CLIENT\n"
        "      label: Nom du client\n"
        "  buttons: []\n",
        encoding="utf-8",
    )
    template.write_text(
        '<FormModule Name="HELLO_WORLD"><Block Name="CLIENTS">'
        '<Item Name="NOM_CLIENT" ColumnName="NOM_CLIENT"/>'
        '<DataSourceColumn DSCName="NOM_CLIENT" DSCType="VARCHAR2" '
        'DSCLength="100" DSCPrecision="0" DSCScale="0"/>'
        '</Block></FormModule>',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="(?i)type.*requis"):
        generator.generate(model, template, output)

def test_generation_reconciles_items_from_model(tmp_path):
    model = tmp_path / "customer.yaml"
    template = tmp_path / "template.xml"
    output = tmp_path / "result.xml"

    model.write_text(
        "form:\n"
        "  name: HELLO_WORLD\n"
        "  title: Gestion des clients\n"
        "  fields:\n"
        "    - name: ID_CLIENT2\n"
        "      type: number\n"
        "      label: Id Client2\n"
        "      column: ID_CLIENT\n"
        "    - name: NOM_CLIENT2\n"
        "      type: text\n"
        "      label: Nom du client\n"
        "      column: NOM_CLIENT\n"
        "    - name: EMAIL\n"
        "      type: text\n"
        "      label: Email\n"
        "  buttons:\n"
        "    - name: BTN_SALUT\n"
        "      label: Dire bonjour\n",
        encoding="utf-8",
    )

    template.write_text("""
<Module xmlns="http://xmlns.oracle.com/Forms">
    <FormModule Name="CUSTOMER_FORM" Title="Ancien titre">
        <Block Name="CLIENTS">
            <Item Name="ID_CLIENT" Prompt="Id Client" DataType="Number" ColumnName="ID_CLIENT"/>
            <Item Name="NOM_CLIENT" Prompt="Nom Client" ColumnName="NOM_CLIENT"/>
            <Item Name="EMAIL" Prompt="Email" ColumnName="EMAIL"/>
            <Item Name="BTN_BONJOUR" ItemType="Push Button" Label="Ancien bouton"/>
            <DataSourceColumn DSCName="ID_CLIENT" DSCType="NUMBER" DSCLength="0" DSCPrecision="38" DSCScale="0"/>
            <DataSourceColumn DSCName="NOM_CLIENT" DSCType="VARCHAR2" DSCLength="100" DSCPrecision="0" DSCScale="0"/>
            <DataSourceColumn DSCName="EMAIL" DSCType="VARCHAR2" DSCLength="150" DSCPrecision="0" DSCScale="0"/>
        </Block>
    </FormModule>
</Module>
""", encoding="utf-8")

    template_before = template.read_bytes()
    generator.generate(model, template, output)

    root = ET.parse(output).getroot()
    items = {e.get("Name"): e for e in root.iter() if e.tag.endswith("Item")}
    data_columns = {
        e.get("DSCName"): e
        for e in root.iter()
        if e.tag.endswith("DataSourceColumn")
    }
    form_module = next(
        element
        for element in root.iter()
        if element.tag.rsplit("}", 1)[-1] == "FormModule"
    )

    assert form_module.get("Name") == "HELLO_WORLD"
    assert form_module.get("Title") == "Gestion des clients"
    assert set(items) == {"ID_CLIENT2", "NOM_CLIENT2", "EMAIL", "BTN_SALUT"}
    assert items["ID_CLIENT2"].get("DataType") == "Number"
    assert items["ID_CLIENT2"].get("ColumnName") == "ID_CLIENT"
    assert items["NOM_CLIENT2"].get("ColumnName") == "NOM_CLIENT"
    assert items["NOM_CLIENT2"].get("Prompt") == (
        "Nom du client"
    )
    assert items["BTN_SALUT"].get("Label") == (
        "Dire bonjour"
    )
    assert set(data_columns) == {"ID_CLIENT", "NOM_CLIENT", "EMAIL"}
    assert template.read_bytes() == template_before

def test_generation_removes_template_objects_absent_from_model(tmp_path):
    model = tmp_path / "model.yaml"
    template = tmp_path / "template.xml"
    output = tmp_path / "result.xml"

    model.write_text("""
form:
  name: HELLO_WORLD
  fields:
    - name: NOM_CLIENT
      type: text
      label: Nom
  buttons: []
""", encoding="utf-8")

    template.write_text(
        '<Module xmlns="http://xmlns.oracle.com/Forms">'
        '<FormModule Name="CUSTOMER_FORM"><Block Name="CLIENTS">'
        '<Item Name="NOM_CLIENT" ColumnName="NOM_CLIENT"/>'
        '<Item Name="EMAIL" ColumnName="EMAIL"/>'
        '<Item Name="BTN_BONJOUR" ItemType="Push Button"/>'
        '<DataSourceColumn DSCName="NOM_CLIENT" DSCType="VARCHAR2"/>'
        '<DataSourceColumn DSCName="EMAIL" DSCType="VARCHAR2"/>'
        '</Block></FormModule>'
        '</Module>',
        encoding="utf-8"
    )

    generator.generate(model, template, output)
    root = ET.parse(output).getroot()
    item_names = {e.get("Name") for e in root.iter() if e.tag.endswith("Item")}
    column_names = {
        e.get("DSCName")
        for e in root.iter()
        if e.tag.endswith("DataSourceColumn")
    }

    assert item_names == {"NOM_CLIENT"}
    assert column_names == {"NOM_CLIENT"}