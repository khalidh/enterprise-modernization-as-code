# Quickstart: Oracle Forms YAML-to-XML Generator

## Prerequisites

- Python 3.11 or newer; the current workspace environment uses Python 3.13.15.
- PyYAML and pytest installed in the selected Python environment.
- A genuine Oracle Forms 14.1.2 XML export installed at `adapters/oracle-forms/templates/hello_world.xml`. The repository copy is currently empty, so generation cannot succeed until that asset is supplied.
- Oracle Forms conversion tools and a configured converter command only when testing XML-to-FMB conversion.
- An AI repair provider only when opt-in repair is being tested.

## Install and Run the Regression Suite

From the repository root in PowerShell:

```powershell
python -m pip install PyYAML pytest
python .\adapters\oracle-forms\generator\test_runner.py
```

Expected result: pytest runs from the repository root, returns a nonzero status on failure, and its captured output is retained under the test log path documented by the implementation.

## Generate and Validate a Form

1. Populate `model/customer.yaml` using the [customer model contract](contracts/customer-model.md).
2. Verify `adapters/oracle-forms/plugin.yaml` points to the genuine read-only template and to `generated/oracle-forms`.
3. Run the adapter from the repository root:

```powershell
python .\adapters\oracle-forms\generator\orchestrate.py `
  --model .\model\customer.yaml `
  --config .\adapters\oracle-forms\plugin.yaml
```

Expected result: the run validates YAML before generating XML, validates the resulting XML, and writes a JSON report and error log in a unique `generated/oracle-forms/HELLO_WORLD/<run-id>/` directory. A successful run includes `HELLO_WORLD.xml`; an invalid run retains its report and log but does not publish invalid XML.

## Verify Optional Oracle Conversion

Configure the installed Oracle conversion executable and its argument array in `plugin.yaml`, using `{input_xml}` and `{output_fmb}` placeholders. Run the same command again.

Expected result: a configured, successful converter produces a separate FMB in the run directory. With no configured or available converter, the report marks conversion as `unavailable` while preserving the successful XML validation result. The default regression suite uses a fake converter and does not require Oracle binaries.

## Verify AI Repair

Enable repair only after configuring an AI repair provider. Introduce a controlled validation failure in a disposable test fixture, then run the suite.

Expected result: each proposed correction is applied only to a staged generated candidate, followed by validation and pytest; no more than three attempts occur, and all attempt details remain in the run report or error log. The YAML, original template, and source FMB remain unchanged.