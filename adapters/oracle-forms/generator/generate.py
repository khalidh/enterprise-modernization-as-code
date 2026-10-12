
from pathlib import Path
import argparse
import copy
import re
import yaml
import xml.etree.ElementTree as ET

def valid_name(name):
    return (
        isinstance(name, str)
        and re.fullmatch(
            r"[A-Za-z][A-Za-z0-9_]{0,29}", name
        ) is not None
    )


def _local_name(element):
    return element.tag.rsplit("}", 1)[-1]


def _column_type(field_type):
    return {"number": "NUMBER", "text": "VARCHAR2"}[field_type]


def generate(model_path, template_path, output_path):
    model_path = Path(model_path)
    template_path = Path(template_path)
    output_path = Path(output_path)

    model = yaml.safe_load(
        model_path.read_text(encoding="utf-8")
    )
    form = model["form"]

    if not valid_name(form["name"]):
        raise ValueError("Nom de formulaire invalide")

    tree = ET.parse(template_path)
    root = tree.getroot()

    form_module = next(
        (
            element
            for element in root.iter()
            if element.tag.rsplit("}", 1)[-1] == "FormModule"
        ),
        None,
    )
    if form_module is None:
        raise ValueError("Module Oracle Forms absent du template")
    form_module.set("Name", form["name"])
    if form.get("title") is not None:
        form_module.set("Title", form["title"])

    blocks = [element for element in root.iter() if _local_name(element) == "Block"]
    if not blocks:
        raise ValueError("Bloc Oracle Forms absent du template")
    block = blocks[0]
    children = list(block)
    template_items = [child for child in children if _local_name(child) == "Item"]
    template_columns = [
        child for child in children if _local_name(child) == "DataSourceColumn"
    ]
    field_prototypes = [
        item
        for item in template_items
        if item.get("ItemType", "").lower() != "push button"
    ]
    button_prototypes = [
        item
        for item in template_items
        if item.get("ItemType", "").lower() == "push button"
    ]
    if not field_prototypes and form.get("fields"):
        raise ValueError("Aucun champ modèle disponible dans le template Oracle")
    if not button_prototypes and form.get("buttons"):
        raise ValueError("Aucun bouton modèle disponible dans le template Oracle")

    fields = form.get("fields", [])
    buttons = form.get("buttons", [])
    new_items = []
    new_columns = []
    used_names = set()
    used_columns = set()

    for index, field in enumerate(fields):
        name = field["name"]
        if not valid_name(name):
            raise ValueError(f"Nom invalide : {name}")
        if name in used_names:
            raise ValueError(f"Nom d'objet dupliqué : {name}")
        used_names.add(name)

        if "type" not in field:
            raise ValueError(
                f"Type de champ requis : {field.get('name', '<inconnu>')}"
            )
        field_type = field["type"]
        if field_type not in ("number", "text"):
            raise ValueError(f"Type de champ non pris en charge : {field_type}")
        column_name = field.get("column", name)
        if not valid_name(column_name):
            raise ValueError(f"Nom de colonne invalide : {column_name}")
        if column_name in used_columns:
            raise ValueError(f"Colonne de base de données dupliquée : {column_name}")
        used_columns.add(column_name)

        expected_column_type = _column_type(field_type)
        matching_item = next(
            (
                item
                for item in field_prototypes
                if item.get("ColumnName") == column_name
                and any(
                    column.get("DSCName") == column_name
                    and column.get("DSCType") == expected_column_type
                    for column in template_columns
                )
            ),
            None,
        )
        prototype = matching_item
        if prototype is None:
            prototype = next(
                (
                    item
                    for item in field_prototypes
                    if any(
                        column.get("DSCName") == item.get("ColumnName")
                        and column.get("DSCType") == expected_column_type
                        for column in template_columns
                    )
                ),
                None,
            )
        if prototype is None:
            raise ValueError(
                f"Aucun champ modèle compatible avec le type {field_type}"
            )

        item = copy.deepcopy(prototype)
        item.set("Name", name)
        item.set("Prompt", field["label"])
        item.set("ColumnName", column_name)
        item.set("YPosition", str(80 + index * 40))
        if field_type == "number":
            item.set("DataType", "Number")
            item.attrib.pop("MaximumLength", None)
        else:
            item.attrib.pop("DataType", None)
            if "length" in field:
                length = field["length"]
                if not isinstance(length, int) or length < 1:
                    raise ValueError(f"Longueur de texte invalide pour {name}")
                item.set("MaximumLength", str(length))
        new_items.append(item)

        column_prototype = next(
            (
                column
                for column in template_columns
                if column.get("DSCName") == column_name
                and column.get("DSCType") == expected_column_type
            ),
            None,
        )
        if column_prototype is None:
            column_prototype = next(
                (
                    column
                    for column in template_columns
                    if column.get("DSCType") == expected_column_type
                ),
                None,
            )
        if column_prototype is None:
            raise ValueError(
                f"Aucune colonne modèle compatible avec le type {field_type}"
            )

        data_column = copy.deepcopy(column_prototype)
        data_column.set("DSCName", column_name)
        if field_type == "number":
            data_column.set("DSCType", "NUMBER")
            data_column.set("DSCLength", "0")
            data_column.set("DSCPrecision", data_column.get("DSCPrecision", "38"))
            data_column.set("DSCScale", data_column.get("DSCScale", "0"))
        else:
            text_length = field.get("length", data_column.get("DSCLength", "100"))
            data_column.set("DSCType", "VARCHAR2")
            data_column.set("DSCLength", str(text_length))
            data_column.set("DSCPrecision", "0")
            data_column.set("DSCScale", "0")
        new_columns.append(data_column)

    for button in buttons:
        name = button["name"]
        if not valid_name(name):
            raise ValueError(f"Nom invalide : {name}")
        if name in used_names:
            raise ValueError(f"Nom d'objet dupliqué : {name}")
        used_names.add(name)
        if not button_prototypes:
            raise ValueError("Aucun bouton modèle disponible dans le template Oracle")
        item = copy.deepcopy(button_prototypes[0])
        item.set("Name", name)
        item.set("Label", button["label"])
        item.set("XPosition", button_prototypes[0].get("XPosition", "400"))
        item.set("YPosition", str(80 + len(fields) * 40))
        new_items.append(item)

    insert_at = min(
        (
            index
            for index, child in enumerate(children)
            if _local_name(child) in ("Item", "DataSourceColumn")
        ),
        default=len(children),
    )
    for child in children:
        if _local_name(child) in ("Item", "DataSourceColumn"):
            block.remove(child)
    for index, item in enumerate(new_items):
        block.insert(insert_at + index, item)
    for index, column in enumerate(new_columns):
        block.insert(insert_at + len(new_items) + index, column)

    required_height = 80 + (len(fields) + bool(buttons)) * 40 + 80
    for element in root.iter():
        if _local_name(element) in ("Canvas", "Window"):
            height = int(element.get("Height", "0"))
            if height < required_height:
                element.set("Height", str(required_height))
                if element.get("ViewportHeight") is not None:
                    element.set("ViewportHeight", str(required_height))

    output_path.parent.mkdir(
        parents=True, exist_ok=True
    )
    if root.tag.startswith("{"):
        namespace = root.tag[1:].split("}", 1)[0]
        ET.register_namespace("", namespace)
    tree.write(
        output_path,
        encoding="utf-8",
        xml_declaration=True
    )
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("template")
    parser.add_argument("output")
    args = parser.parse_args()

    print(generate(
        args.model, args.template, args.output
    ))
