# Contrat de configuration du plugin

`adapters/oracle-forms/plugin.yaml` configure les chemins et les intégrations facultatives. Les chemins relatifs sont résolus depuis la racine du dépôt.

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

- `template` doit désigner l'export XML Oracle Forms 14.1.2 authentique et en lecture seule.
- Pour cette fonctionnalité, `output_root` doit rester sous `generated/`.
- `oracle_converter.command` est un chemin d'exécutable ou une commande propre à l'installation. Le plugin ne le code pas en dur. `args` est un tableau d'arguments; les jetons `{input_xml}` et `{output_fmb}` sont remplacés par les chemins de l'exécution en cours. Le processus est lancé sans interprétation par un shell.
- Si la commande est absente ou introuvable, la conversion est signalée comme `unavailable`. Si une commande configurée s'exécute mais échoue, l'échec de conversion est signalé.
- `ai_repair.enabled` active la réparation uniquement si un fournisseur de réparation IA est configuré. `max_attempts` est plafonné à trois quelle que soit la configuration; le fournisseur ne peut modifier qu'un candidat généré dans une copie de travail.

Les erreurs de configuration sont signalées avant la génération et ne modifient pas les fichiers source.