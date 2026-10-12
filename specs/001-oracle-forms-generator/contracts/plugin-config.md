# Plugin Configuration Contract

`adapters/oracle-forms/plugin.yaml` configures paths and optional integrations. Relative paths are resolved from the repository root.

```yaml
template: adapters/oracle-forms/templates/hello_world.xml
output_root: generated/oracle-forms

oracle_converter:
  command: null
  args: []

ai_repair:
  enabled: false
  max_attempts: 3
```

- `template` must refer to the genuine, read-only Oracle Forms 14.1.2 XML export.
- `output_root` must remain within `generated/` for this feature.
- `oracle_converter.command` is an installation-specific executable path or command. It is not hard-coded by the plugin. `args` is an argument array; `{input_xml}` and `{output_fmb}` tokens are replaced with the current run paths. The process is invoked without shell interpretation.
- When the command is absent or cannot be found, conversion is reported as `unavailable`. A configured command that runs and fails is reported as a conversion failure.
- `ai_repair.enabled` enables repair only when an AI repair provider is configured. `max_attempts` is capped at three regardless of configuration; the provider may edit only a staged generated candidate.

Configuration errors are reported before generation and do not cause source files to be changed.