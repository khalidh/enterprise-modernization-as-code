# Tâches : générateur YAML vers XML Oracle Forms

**Entrée** : documents de conception de `specs/001-oracle-forms-generator/`

**Prérequis** : `plan.md`, `spec.md`, `research.md`, `data-model.md` et `contracts/`

**Tests** : requis par la spécification de la fonctionnalité. Utiliser pytest et l'exécuter après chaque modification du code, de la configuration ou d'un artefact généré.

**Organisation** : les tâches sont regroupées par récit utilisateur afin de permettre une implémentation et une vérification progressives.

## Format

Chaque tâche suit le format `- [ ] Tnnn [P?] [Story?] Description avec chemin de fichier exact`. `[P]` n'est utilisé que lorsque les fichiers et leur validation peuvent avancer indépendamment sans risque. Les étiquettes de récit apparaissent uniquement dans les phases consacrées aux récits utilisateur.

## Phase 1 : Préparation

**Objectif** : mettre en place les entrées et la configuration du projet pour permettre les tests.

 - [ ] T001 Ajouter un test de fumée réussi vérifiant l'arborescence du dépôt dans `tests/test_oracle_forms.py`, puis lancer `python -m pytest -q tests/test_oracle_forms.py`.
 - [ ] T002 Ajouter les dépendances `PyYAML` et `pytest` à `requirements.txt`, les installer avec `python -m pip install -r requirements.txt`, puis lancer `python -m pytest -q tests/test_oracle_forms.py`.
 - [ ] T003 [P] Configurer le chemin du template, la racine des sorties, le convertisseur facultatif et la réparation IA désactivée par défaut avec une limite de trois tentatives dans `adapters/oracle-forms/plugin.yaml`; puis lancer `python -m pytest -q tests/test_oracle_forms.py`.
 - [ ] T004 [P] Ajouter à `model/customer.yaml` le modèle `HELLO_WORLD` conforme au contrat, avec un `field` nommé `NOM_CLIENT` et un `button` nommé `BTN_BONJOUR`; puis lancer `python -m pytest -q tests/test_oracle_forms.py`.
 - [ ] T005 [P] Obtenir un export Oracle Forms 14.1.2 authentique contenant le formulaire, le champ et le bouton cibles, puis le placer dans `adapters/oracle-forms/templates/hello_world.xml`; ne pas synthétiser ni modifier un FMB source existant, puis lancer `python -m pytest -q tests/test_oracle_forms.py`.

## Phase 2 : Fondations

**Objectif** : mettre en place l'analyse sûre des entrées et le lanceur pytest indépendant avant l'implémentation des récits utilisateur.

 - [ ] T006 Ajouter dans `tests/test_oracle_forms.py` des tests couvrant le chargement d'un YAML valide, un YAML mal formé, l'absence de champs obligatoires, les noms en double et la règle exigeant exactement un champ et un bouton; lancer `python -m pytest -q tests/test_oracle_forms.py` et confirmer l'échec des nouveaux tests de comportement.
 - [ ] T007 Implémenter le chargement sûr du YAML et la validation du modèle client dans `adapters/oracle-forms/generator/validate.py`, y compris la ligne et la colonne source lorsque PyYAML les fournit; lancer immédiatement `python -m pytest -q tests/test_oracle_forms.py`.
 - [ ] T008 Ajouter dans `tests/test_oracle_forms.py` des tests couvrant la construction de la commande pytest, la capture de la sortie, le code de retour et la conservation des journaux de test; lancer `python -m pytest -q tests/test_oracle_forms.py` et confirmer l'échec des nouvelles assertions de comportement.
 - [ ] T009 Implémenter le lanceur pytest dans un processus séparé dans `adapters/oracle-forms/generator/test_runner.py`; capturer stdout/stderr et conserver un journal, puis lancer immédiatement `python -m pytest -q tests/test_oracle_forms.py`.

## Phase 3 : Récit utilisateur 1 - Générer le formulaire HELLO_WORLD (Priorité : P1) 🎯 MVP

**Objectif** : générer un résultat XML Oracle Forms valide à partir d'un modèle YAML MVP valide et du template exporté.

**Test indépendant** : lancer le générateur avec `model/customer.yaml`; vérifier que le XML est bien formé, contient un formulaire `HELLO_WORLD`, un champ `NOM_CLIENT` et un bouton `BTN_BONJOUR`, et que le template source est inchangé.

### Tests du récit utilisateur 1

 - [ ] T010 [US1] Ajouter dans `tests/test_oracle_forms.py` des tests de génération utilisant le template authentique; vérifier que le XML est bien formé, que les types et noms d'objets requis sont présents, que les objets sans rapport sont préservés et que les octets du template sont inchangés; lancer ensuite `python -m pytest -q tests/test_oracle_forms.py` et confirmer l'échec des nouveaux tests de comportement.

### Implémentation du récit utilisateur 1

 - [ ] T011 [US1] Implémenter la génération du formulaire à partir du template avec `xml.etree.ElementTree` dans `adapters/oracle-forms/generator/generate.py`; ne mettre à jour que les nœuds cibles existants et lancer immédiatement `python -m pytest -q tests/test_oracle_forms.py` après la modification.
 - [ ] T012 [US1] Ajouter dans `tests/test_oracle_forms.py` des tests d'intégration d'une exécution réussie, couvrant la mise en attente et l'emplacement des sorties; vérifier que le XML se trouve sous `generated/oracle-forms/<form>/<run-id>/`, puis lancer `python -m pytest -q tests/test_oracle_forms.py` et confirmer l'échec des nouvelles assertions d'orchestration.
 - [ ] T013 [US1] Implémenter le parcours de génération réussie, le répertoire d'exécution unique et la publication après validation dans `adapters/oracle-forms/generator/orchestrate.py`; lancer immédiatement `python -m pytest -q tests/test_oracle_forms.py` après la modification.

**Jalon** : US1 peut être démontré indépendamment des outils de conversion Oracle et de tout fournisseur d'IA.

## Phase 4 : Récit utilisateur 2 - Personnaliser les noms et libellés des objets (Priorité : P2)

**Objectif** : appliquer aux types d'objets correspondants du template les noms et libellés fournis dans YAML, y compris le texte échappé pour XML.

**Test indépendant** : modifier les noms et libellés du champ et du bouton dans un fichier YAML temporaire valide, puis vérifier que les valeurs du XML généré leur correspondent exactement.

### Tests du récit utilisateur 2

 - [ ] T014 [US2] Ajouter dans `tests/test_oracle_forms.py` des tests couvrant la personnalisation des noms de formulaire et d'objets, des libellés, du mappage des types d'objets et des caractères spéciaux XML; lancer `python -m pytest -q tests/test_oracle_forms.py` et confirmer l'échec des nouvelles assertions de comportement.

### Implémentation du récit utilisateur 2

 - [ ] T015 [US2] Appliquer les noms et libellés validés du formulaire, du champ et du bouton aux nœuds correspondants du template dans `adapters/oracle-forms/generator/generate.py`; lancer immédiatement `python -m pytest -q tests/test_oracle_forms.py` après la modification.

**Jalon** : US2 peut être démontré indépendamment en modifiant uniquement les valeurs YAML et en relançant la génération.

## Phase 5 : Récit utilisateur 3 - Diagnostiquer les entrées et sorties invalides (Priorité : P2)

**Objectif** : rejeter les entrées ou sorties invalides et conserver des rapports JSON et des journaux exploitables sans publier de XML invalide.

**Test indépendant** : tester un YAML mal formé, des valeurs manquantes, un XML mal formé et des objets cibles absents; examiner le rapport JSON et le journal d'erreurs de chaque exécution et vérifier qu'aucun XML invalide n'est publié.

### Tests du récit utilisateur 3

 - [ ] T016 [US3] Ajouter dans `tests/test_oracle_forms.py` des tests des chemins d'échec couvrant la validation YAML et XML, le schéma du rapport, les emplacements source, la conservation des journaux et l'absence de publication du XML invalide; lancer `python -m pytest -q tests/test_oracle_forms.py` et confirmer l'échec des nouvelles assertions.

### Implémentation du récit utilisateur 3

 - [ ] T017 [US3] Implémenter dans `adapters/oracle-forms/generator/validate.py` les contrôles de bonne formation avec ElementTree et les contrôles des objets et noms requis; lancer immédiatement `python -m pytest -q tests/test_oracle_forms.py` après la modification.
 - [ ] T018 [US3] Implémenter dans `adapters/oracle-forms/generator/orchestrate.py` des rapports JSON d'échec structurés et la conservation des journaux d'erreurs par exécution, conformément à `specs/001-oracle-forms-generator/contracts/run-report.schema.json`; s'assurer qu'aucun XML invalide n'est publié et lancer immédiatement `python -m pytest -q tests/test_oracle_forms.py` après la modification.

**Jalon** : US3 peut être démontré indépendamment avec des jeux de test invalides et ne nécessite pas d'installation Oracle.

## Phase 6 : Récit utilisateur 4 - Convertir le XML en FMB si les outils Oracle sont disponibles (Priorité : P3)

**Objectif** : convertir le XML validé avec l'outil Oracle configuré lorsqu'il est disponible, sans lier la disponibilité de la conversion à la réussite du XML.

**Test indépendant** : utiliser un faux convertisseur configuré pour vérifier les parcours de réussite et d'échec; vérifier qu'un convertisseur absent est signalé comme indisponible. N'exécuter le cas d'acceptation avec le véritable convertisseur que dans un environnement Oracle Forms 14.1.2.

### Tests du récit utilisateur 4

 - [ ] T019 [US4] Ajouter dans `tests/test_oracle_forms.py` des tests avec un faux processus couvrant la réussite du convertisseur, un code de sortie non nul, un exécutable absent, le remplacement des arguments et la production d'un FMB distinct; lancer `python -m pytest -q tests/test_oracle_forms.py` et confirmer l'échec des nouvelles assertions.

### Implémentation du récit utilisateur 4

 - [ ] T020 [US4] Implémenter dans `adapters/oracle-forms/generator/oracle_converter.py` l'exécution configurée de la conversion XML vers FMB sans interpolation par le shell; prendre en charge les arguments `{input_xml}` et `{output_fmb}`, puis lancer immédiatement `python -m pytest -q tests/test_oracle_forms.py`.
 - [ ] T021 [US4] Intégrer la disponibilité du convertisseur et ses résultats au rapport d'exécution, ainsi que des chemins de sortie distincts, dans `adapters/oracle-forms/generator/orchestrate.py`; lancer immédiatement `python -m pytest -q tests/test_oracle_forms.py`.

**Jalon** : US4 peut être démontré indépendamment avec un faux convertisseur; le test de conversion Oracle sous licence reste conditionné à la configuration des outils Oracle.

## Phase 7 : Finitions - réparation par IA et validation transversale

**Objectif** : ajouter une réparation limitée et auditable, puis vérifier l'ensemble du guide de démarrage rapide.

 - [ ] T022 Ajouter dans `tests/test_oracle_forms.py` des tests couvrant la réparation désactivée, l'échec du fournisseur, la réussite d'une réparation, l'immutabilité des fichiers source et l'arrêt après exactement trois tentatives échouées; lancer `python -m pytest -q tests/test_oracle_forms.py` et confirmer l'échec des nouvelles assertions de comportement.
 - [ ] T023 Implémenter dans `adapters/oracle-forms/generator/repair_loop.py` une réparation IA indépendante du fournisseur, limitée strictement à trois tentatives, avec validation et pytest après chaque modification d'un candidat, ainsi que la conservation des journaux de tentative; lancer immédiatement `python -m pytest -q tests/test_oracle_forms.py`.
 - [ ] T024 Intégrer la boucle de réparation uniquement pour les candidats en échec dans une copie de travail, dans `adapters/oracle-forms/generator/orchestrate.py`; appliquer la limite configurée, préserver le YAML, le template et le FMB source, puis lancer immédiatement `python -m pytest -q tests/test_oracle_forms.py`.
 - [ ] T025 Documenter le périmètre autorisé de réparation, la limite de tentatives et la conservation des journaux dans `agents/forms-repair/SKILL.md`; lancer `python -m pytest -q tests/test_oracle_forms.py` après la modification documentaire.
 - [ ] T026 Exécuter la suite complète via `adapters/oracle-forms/generator/test_runner.py` et valider les étapes de bout en bout de `specs/001-oracle-forms-generator/quickstart.md`; confirmer que les artefacts générés restent sous `generated/oracle-forms/` et que tous les rapports et journaux restent disponibles.

## Dépendances et ordre d'exécution

### Dépendances entre phases

- **Préparation (phase 1)** : T001-T002 mettent en place pytest et les dépendances. Après T002, T003-T005 peuvent être exécutées en parallèle, car elles modifient des fichiers d'entrée, de configuration et de template distincts.
- **Fondations (phase 2)** : dépend de la préparation. T006-T007 mettent en place la validation des entrées; T008-T009 mettent en place l'orchestration des tests. Ces tâches bloquent l'implémentation des récits utilisateur.
- **US1 (phase 3)** : dépend du modèle validé, des chemins configurés et du template authentique des phases 1 et 2. Il s'agit du MVP.
- **US2 (phase 4)** : dépend de la génération US1 et du mappage de son template.
- **US3 (phase 5)** : dépend du validateur partagé et de l'orchestration d'une exécution réussie de US1; ajoute les rapports d'échec et la conservation des journaux.
- **US4 (phase 6)** : dépend du résultat de US1 et du contrat de rapport de US3. Un test avec le convertisseur réel nécessite en plus les outils Oracle Forms 14.1.2 et la configuration locale de la commande.
- **Finitions (phase 7)** : dépendent de US1 à US3; US4 n'est nécessaire que si la réparation par IA doit traiter les échecs de conversion.

### Dépendances entre récits utilisateur

- **US1 (P1)** : après la préparation et les fondations; fournit la génération XML sans conversion Oracle ni réparation par IA.
- **US2 (P2)** : après US1, car ce récit étend le mappage des nœuds cibles du générateur.
- **US3 (P2)** : après le validateur fondamental et l'orchestration US1; peut être implémenté avant US2 si les modifications de fichiers partagés sont exécutées séquentiellement.
- **US4 (P3)** : après US1 et le contrat de rapport; les outils Oracle restent facultatifs pour tous les autres récits.

### Possibilités de parallélisation

- Après T002, T003 (`plugin.yaml`), T004 (`customer.yaml`) et T005 (artefact template) modifient des fichiers distincts et peuvent être préparées en parallèle; exécuter leurs tests de fumée séquentiellement s'ils partagent le même espace de travail.
- Dans chaque récit, les tâches de test précèdent l'implémentation et partagent souvent `tests/test_oracle_forms.py`; ne pas paralléliser ces paires dans un même arbre de travail.
- US2 et US3 modifient toutes deux les parties génération, validation et rapports; les exécuter séquentiellement dans un même clone, même si leurs jeux de données de test sont indépendants en théorie.
- Les tests avec faux convertisseur et l'implémentation du convertisseur pour US4 sont séquentiels; la vérification avec Oracle réel peut être faite séparément une fois l'environnement configuré.

### Exemples d'exécution en parallèle

```text
Préparation après T002 (fichiers distincts) :
T003 adapters/oracle-forms/plugin.yaml
T004 model/customer.yaml
T005 adapters/oracle-forms/templates/hello_world.xml

US1 : T010 test -> T011 générateur -> T012 test d'intégration -> T013 orchestration
US2 : T014 test -> T015 personnalisation
US3 : T016 test -> T017 validation -> T018 rapport/journal JSON
US4 : T019 test du faux outil -> T020 convertisseur -> T021 intégration
```

## Stratégie d'implémentation

### MVP d'abord (récit utilisateur 1 uniquement)

1. Terminer les tâches de préparation et de fondation, notamment la fourniture d'un template Forms 14.1.2 authentique.
2. Terminer les tests et l'implémentation de US1.
3. Lancer pytest et le contrôle indépendant de génération US1; s'arrêter si les contrôles du template ou de sa préservation échouent.
4. Démontrer que le XML sous `generated/oracle-forms/` est bien formé avant de poursuivre.

### Livraison incrémentale

1. Ajouter la personnalisation pilotée par YAML et l'échappement XML de US2.
2. Ajouter les diagnostics JSON de US3 et conserver les journaux de tous les chemins d'échec.
3. Ajouter la conversion facultative de US4 à l'aide de tests avec faux processus, puis la valider avec les outils Oracle lorsqu'ils sont disponibles.
4. Ajouter la réparation IA en dernier, avec une limite stricte de trois tentatives et une validation ainsi qu'un lancement de pytest après chaque modification de candidat.

## Critères d'achèvement

- Cocher les tâches uniquement après leur achèvement; chaque entrée doit respecter le format de case à cocher, d'identifiant séquentiel, d'étiquettes de parallélisation/récit applicables et de chemin de fichier exact.
- La suite pytest complète réussit après la dernière modification de l'implémentation.
- Les XML générés, rapports JSON, FMB convertis et journaux d'erreurs restent sous `generated/oracle-forms/`.
- Le template original et le FMB source restent inchangés; aucun parcours de réparation IA ne dépasse trois tentatives.
