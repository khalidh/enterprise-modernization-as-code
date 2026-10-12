# Data Model: Oracle Forms YAML-to-XML Generator

## Customer Form Model

Source: `model/customer.yaml`.

| Field | Type | Required | Validation |
|---|---|---:|---|
| `form.name` | string | Yes | Non-empty; identifies the form in generated XML |
| `form.objects` | list | Yes | MVP contains exactly one `field` and one `button` |
| `form.objects[].type` | enum | Yes | `field` or `button`; each type occurs once in the MVP |
| `form.objects[].name` | string | Yes | Non-empty and unique within the form |
| `form.objects[].label` | string | Yes | Present; its value is applied to the corresponding template object |

The MVP example uses form `HELLO_WORLD`, field `NOM_CLIENT`, and button `BTN_BONJOUR`. Names and labels are data, not generator constants. Additional object types and multiple forms are out of scope.

## Oracle Forms Template

Source: `adapters/oracle-forms/templates/hello_world.xml`.

The template is a complete Oracle Forms 14.1.2 export with one target form, one field, and one button. Generation resolves these existing nodes from the export and updates only their configured properties. All other elements, including unknown Oracle-specific nodes, remain in the parsed tree. The source file is read-only; generation works on an in-memory or staged copy.

The repository's current template file is empty. A verified Forms 14.1.2 export must be supplied before its selectors and property mapping can be implemented or verified.

## Generation Run

| Field | Type | Meaning |
|---|---|---|
| `run_id` | string | Unique identifier used for the output directory |
| `form_name` | string | Validated name used to group outputs |
| `status` | enum | `success` only after required XML validation; otherwise `failure` |
| `stages` | mapping | Per-stage status for YAML validation, generation, XML validation, and FMB conversion |
| `outputs` | list | Repository-relative paths and kinds of generated artifacts |
| `errors` | list | Structured errors associated with the failing stage |
| `error_log_path` | string | Persistent text log path under the run directory |

Each run is stored under `generated/oracle-forms/<form-name>/<run-id>/`. Failed runs retain the report and log; invalid XML is not published as a successful output.

## Run Error

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `code` | string | Yes | Stable machine-readable error category |
| `stage` | string | Yes | YAML validation, XML generation, XML validation, test execution, AI repair, or FMB conversion |
| `message` | string | Yes | Actionable human-readable description |
| `source` | string | No | Input or artifact path when known |
| `line` | integer | No | One-based source line when available |
| `column` | integer | No | One-based source column when available |

## State Flow

`created -> yaml_validated -> xml_generated -> xml_validated -> [fmb_converted | fmb_unavailable] -> success`

Any required-stage failure leads to `failure`, retains a report and error log, and prevents invalid XML from being published. AI repair may repeat candidate generation/validation/test stages up to three times; each failed attempt is recorded. The original template, input YAML, and source FMB are never states that the workflow writes to.