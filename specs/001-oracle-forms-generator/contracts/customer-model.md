# Customer Model Contract

`model/customer.yaml` is the source of truth for the generated form's name,
title, fields, buttons, labels, types, and database-column mappings.

```yaml
form:
  name: HELLO_WORLD
  title: Gestion des clients
  fields:
    - name: ID_CLIENT2
      type: number
      label: Id Client2
      column: ID_CLIENT
    - name: NOM_CLIENT2
      type: text
      label: Nom du client
      column: NOM_CLIENT
    - name: EMAIL
      type: text
      label: Email
      column: EMAIL
  buttons:
    - name: BTN_BONJOUR
      label: Dire bonjour
```

`form.name`, each object's `name` and `label`, and each field's supported
`type` are required. Names must be valid Oracle Forms identifiers and unique
across fields and buttons. Supported field types are `text` and `number`.

`field.column` optionally maps the generated Forms item name to a database
column. It defaults to `field.name`. `field.length` optionally sets the maximum
length for text fields; otherwise the matching template prototype supplies the
default.

The Oracle Forms XML template supplies the form structure and prototypes for
field and button presentation. During generation, the field and button items
inside its target data block are rebuilt from the YAML: items omitted from the
model are removed from the generated output, and items named in the model are
created from a compatible prototype even when their names are not in the
template. The original template remains unchanged. The data block, canvas,
window, and other Oracle-specific structure are preserved.