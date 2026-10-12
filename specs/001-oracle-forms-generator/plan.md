# Plan d'implémentation : générateur YAML vers XML Oracle Forms

**Branche** : `001-oracle-forms-generator` | **Date** : 2026-10-09 | **Spécification** : [spec.md](spec.md)

**Entrée** : spécification de la fonctionnalité dans `specs/001-oracle-forms-generator/spec.md`

## Résumé

Construire un pipeline de plugin Python qui charge et valide de manière sûre `customer.yaml`, modifie uniquement les nœuds désignés du formulaire, du champ et du bouton dans un export XML Oracle Forms 14.1.2 à l'aide de `xml.etree.ElementTree`, valide le résultat et écrit les artefacts de chaque exécution sous `generated/oracle-forms/`. Séparer la génération, la validation XML, l'orchestration de pytest, la conversion Oracle et la réparation par IA dans des modules distincts. Rendre la conversion Oracle et la réparation par IA configurables; conserver un rapport JSON et des journaux d'erreurs pour chaque exécution.

## Contexte technique

**Langage/version** : Python 3; développer et vérifier dans l'environnement Python 3.13.15 du dépôt; aucune compatibilité n'est garantie en dessous de Python 3.11.

**Dépendances principales** : PyYAML pour analyser YAML de manière sûre; `xml.etree.ElementTree` de la bibliothèque standard Python pour manipuler l'arbre XML; pytest pour les tests de régression. Les utilitaires de conversion Oracle Forms sont des outils externes facultatifs.

**Stockage** : fichiers locaux uniquement. Les entrées et le template original restent à leur emplacement source; les rapports, journaux, XML générés et éventuels fichiers FMB sont stockés sous `generated/oracle-forms/`.

**Tests** : pytest, lancé et capturé par un module dédié d'exécution des tests. Par défaut, les tests du convertisseur utilisent un faux exécutable et ne nécessitent pas d'installation Oracle.

**Plateforme cible** : Python 3 sur la plateforme de développement du projet. Le processus facultatif de conversion Oracle doit s'exécuter dans un environnement pris en charge par les outils Oracle Forms 14.1.2 installés.

**Type de projet** : plugin/adaptateur Python local avec un point d'entrée d'orchestration en ligne de commande.

**Objectifs de performance** : aucun objectif de latence pour le MVP; un petit formulaire est traité par exécution.

**Contraintes** : utiliser un véritable export Oracle Forms 14.1.2 comme base XML; ne jamais modifier le template XML original ni le FMB source; valider YAML avant la génération; préserver les sous-arbres XML non ciblés; conserver les rapports JSON et journaux d'erreurs par exécution; lancer pytest après chaque modification du code ou d'un artefact généré; arrêter la réparation par IA après trois tentatives au maximum.

**Échelle/périmètre** : un formulaire `HELLO_WORLD` par modèle, avec un champ et un bouton; un résultat XML et, éventuellement, un FMB converti par exécution.

## Vérification de la constitution

**Contrôle préalable à la conception : RÉUSSI**

- Compatibilité du template : la génération modifie un véritable export Forms 14.1.2; le fichier template actuel du dépôt est vide, l'obtention et la vérification de l'export sont donc des prérequis à l'implémentation.
- Préservation et immutabilité du FMB : modifier uniquement les nœuds ciblés dans une copie analysée; ne jamais écrire dans les chemins du template ou du FMB source.
- Validation des entrées : analyser et valider sans risque le modèle YAML complet avant de créer le XML généré.
- Modifications soumises aux tests : isoler l'orchestration de pytest et l'exécuter après chaque modification du code ou d'un artefact généré.
- Réparation limitée et auditable : isoler la réparation par IA, la limiter à trois tentatives et conserver les rapports et journaux.

Aucune dérogation à la constitution n'est nécessaire. La disponibilité des outils Oracle est une condition d'intégration facultative, et non un motif pour affaiblir la génération ou la validation XML.

## Structure du projet

### Documentation (cette fonctionnalité)

```text
specs/001-oracle-forms-generator/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── customer-model.md
│   ├── plugin-config.md
│   └── run-report.schema.json
├── checklists/requirements.md
└── tasks.md
```

### Code source (racine du dépôt)

```text
adapters/oracle-forms/
├── plugin.yaml
├── generator/
│   ├── generate.py          # Génération XML basée uniquement sur le template
│   ├── validate.py          # Validation YAML et XML généré
│   ├── orchestrate.py       # Pipeline par exécution et publication des artefacts
│   ├── test_runner.py       # Orchestration de pytest et journaux de test
│   ├── oracle_converter.py  # Processus facultatif et configurable de conversion XML vers FMB
│   └── repair_loop.py       # Réparation IA limitée et indépendante du fournisseur
└── templates/
	└── hello_world.xml      # Genuine Oracle Forms 14.1.2 export
agents/forms-repair/SKILL.md
model/customer.yaml
generated/oracle-forms/<form>/<run-id>/
tests/test_oracle_forms.py
```

**Décision de structure** : étendre l'organisation d'adaptateurs existante plutôt que d'introduire une nouvelle arborescence de paquets. Aligner les limites des modules sur les responsabilités demandées. `orchestrate.py` gère l'ordre des opérations et les rapports, sans implémenter la modification XML, la validation, pytest, le convertisseur ni le fournisseur d'IA. Chaque exécution dispose d'un répertoire de sortie unique afin qu'un échec ultérieur ne puisse pas effacer les diagnostics précédents.

## Phase 0 : Recherche

Voir [research.md](research.md). Les choix d'architecture sont arrêtés. Deux éléments d'environnement restent des prérequis d'implémentation plutôt que des questions de conception ouvertes : un export XML Forms 14.1.2 vérifié et un exécutable de conversion Oracle configuré localement pour tester la conversion FMB.

## Phase 1 : Conception et contrats

- Le [modèle de données](data-model.md) définit le modèle de formulaire validé, l'exécution générée, le rapport et les enregistrements d'erreur.
- Le [contrat du modèle client](contracts/customer-model.md) définit la structure YAML et les contraintes d'objets du MVP.
- Le [contrat de configuration du plugin](contracts/plugin-config.md) définit les chemins du template et des sorties, les paramètres du convertisseur et ceux de la réparation facultative.
- Le [schéma du rapport d'exécution](contracts/run-report.schema.json) définit l'état JSON, les étapes, les sorties et les erreurs.
- Le [guide de démarrage rapide](quickstart.md) décrit les prérequis et la validation de bout en bout sans exiger les outils Oracle pour le MVP XML.

**Contrôle après conception : RÉUSSI**

La conception respecte toutes les contraintes de la constitution. La génération et la réparation ne ciblent qu'une copie de travail; la publication a lieu après validation YAML et XML; la conversion Oracle configurée écrit un fichier distinct; pytest est isolé dans `test_runner.py`; chaque tentative de réparation par IA est limitée et journalisée. Le template initial et la configuration facultative du convertisseur Oracle doivent être fournis avant que les tests d'intégration correspondants puissent réussir.
