# Démarrage rapide : générateur YAML vers XML Oracle Forms

## Prérequis

- Python 3.11 ou version ultérieure; l'environnement actuel de l'espace de travail utilise Python 3.13.15.
- PyYAML et pytest installés dans l'environnement Python sélectionné.
- Un véritable export XML Oracle Forms 14.1.2 placé dans `adapters/oracle-forms/templates/hello_world.xml`. La copie présente dans le dépôt est actuellement vide; la génération ne peut donc pas réussir tant que cet artefact n'est pas fourni.
- Les outils de conversion Oracle Forms et une commande de convertisseur configurée sont nécessaires uniquement pour tester la conversion XML vers FMB.
- Un fournisseur de réparation IA est nécessaire uniquement pour tester la réparation activée explicitement.

## Installer et lancer la suite de régression

Depuis la racine du dépôt, dans PowerShell :

```powershell
python -m pip install PyYAML pytest
python .\adapters\oracle-forms\generator\test_runner.py
```

Résultat attendu : pytest s'exécute depuis la racine du dépôt, renvoie un code différent de zéro en cas d'échec et conserve sa sortie capturée au chemin de journal de test documenté par l'implémentation.

## Générer et valider un formulaire

1. Renseigner `model/customer.yaml` conformément au [contrat du modèle client](contracts/customer-model.md).
2. Vérifier que `adapters/oracle-forms/plugin.yaml` pointe vers le template authentique en lecture seule et vers `generated/oracle-forms`.
3. Lancer l'adaptateur depuis la racine du dépôt :

```powershell
python .\adapters\oracle-forms\generator\orchestrate.py `
  --model .\model\customer.yaml `
  --config .\adapters\oracle-forms\plugin.yaml
```

Résultat attendu : l'exécution valide le YAML avant de générer le XML, valide ensuite le XML obtenu et écrit un rapport JSON ainsi qu'un journal d'erreurs dans un répertoire unique `generated/oracle-forms/HELLO_WORLD/<run-id>/`. Une exécution réussie contient `HELLO_WORLD.xml`; une exécution invalide conserve son rapport et son journal sans publier de XML invalide.

## Vérifier la conversion Oracle facultative

Configurer l'exécutable de conversion Oracle installé et son tableau d'arguments dans `plugin.yaml`, avec les placeholders `{input_xml}` et `{output_fmb}`. Relancer la même commande.

Résultat attendu : un convertisseur configuré qui réussit produit un FMB distinct dans le répertoire d'exécution. Si aucun convertisseur n'est configuré ou disponible, le rapport indique `unavailable` tout en conservant le résultat positif de la validation XML. Par défaut, la suite de régression utilise un faux convertisseur et ne nécessite pas les exécutables Oracle.

## Vérifier la réparation par IA

Activer la réparation uniquement après avoir configuré un fournisseur de réparation IA. Introduire un échec de validation contrôlé dans un jeu de test jetable, puis lancer la suite.

Résultat attendu : chaque correction proposée est appliquée uniquement à un candidat généré dans une copie de travail, puis suivie d'une validation et de pytest; le nombre de tentatives ne dépasse pas trois et leurs détails figurent dans le rapport d'exécution ou le journal d'erreurs. Le YAML, le template original et le FMB source restent inchangés.