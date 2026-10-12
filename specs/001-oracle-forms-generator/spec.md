# Spécification de la fonctionnalité : générateur YAML vers XML Oracle Forms

**Branche de la fonctionnalité** : `001-oracle-forms-generator`

**Créée le** : 2026-10-09

**Statut** : Brouillon

**Entrée** : description utilisateur : créer un plugin MVP qui transforme `customer.yaml` en XML Oracle Forms pour un formulaire `HELLO_WORLD` comprenant un champ `NOM_CLIENT` et un bouton `BTN_BONJOUR`, permet de configurer les noms et libellés dans YAML, valide le XML généré, signale les erreurs en JSON et convertit le XML en FMB lorsque les outils Oracle sont disponibles.

## Scénarios utilisateur et tests *(obligatoire)*

### Récit utilisateur 1 - Générer le formulaire HELLO_WORLD (Priorité : P1)

En tant que développeur de formulaires, je fournis un modèle client valide et obtiens un formulaire XML Oracle Forms basé sur le template Oracle Forms 14.1.2 fourni, afin de pouvoir examiner et utiliser le formulaire généré.

**Pourquoi cette priorité** : la génération du formulaire demandé constitue la valeur essentielle du MVP.

**Test indépendant** : fournir un modèle MVP valide et vérifier qu'un fichier XML est produit, qu'il est bien formé, contient le formulaire, le champ et le bouton attendus, et que le template original reste inchangé.

**Scénarios d'acceptation** :

1. **Étant donné** un modèle valide et un template XML Oracle Forms 14.1.2 disponible, **quand** l'utilisateur lance le générateur, **alors** celui-ci produit un formulaire XML bien formé nommé `HELLO_WORLD`, contenant un champ nommé `NOM_CLIENT` et un bouton nommé `BTN_BONJOUR`.
2. **Étant donné** une génération, **quand** elle se termine, **alors** le template original et tout fichier FMB source restent inchangés.

### Récit utilisateur 2 - Personnaliser les noms et libellés des objets (Priorité : P2)

En tant que développeur de formulaires, je peux modifier les noms et libellés d'objets pris en charge dans le modèle client et retrouver ces valeurs dans le formulaire généré, afin que le résultat corresponde à la définition propre au client.

**Pourquoi cette priorité** : la personnalisation pilotée par YAML rend le générateur réutilisable au-delà d'un exemple codé en dur.

**Test indépendant** : modifier les noms et libellés du champ et du bouton dans un modèle valide, générer le formulaire et comparer les valeurs des objets XML correspondants à celles du modèle.

**Scénarios d'acceptation** :

1. **Étant donné** un modèle valide avec des noms et libellés de champ et de bouton personnalisés, **quand** l'utilisateur génère le XML, **alors** chaque nom et libellé pris en charge dans le résultat correspond à la valeur du modèle.
2. **Étant donné** un modèle valide utilisant les noms MVP `NOM_CLIENT` et `BTN_BONJOUR`, **quand** l'utilisateur génère le XML, **alors** ces noms figurent respectivement sur le champ et le bouton correspondants, et non sur un autre type d'objet.

### Récit utilisateur 3 - Diagnostiquer les entrées et sorties invalides (Priorité : P2)

En tant que développeur de formulaires, je reçois une explication lisible par machine lorsque le modèle est invalide ou que le XML généré échoue à la validation, afin de pouvoir corriger l'entrée sans accepter un formulaire défectueux.

**Pourquoi cette priorité** : une validation et des rapports d'erreur clairs évitent d'utiliser un résultat mal formé ou trompeur.

**Test indépendant** : soumettre un YAML mal formé, un modèle auquel il manque des valeurs obligatoires et un cas produisant un XML invalide; vérifier que chaque échec est signalé en JSON et qu'aucun XML invalide n'est considéré comme un résultat réussi.

**Scénarios d'acceptation** :

1. **Étant donné** un YAML mal formé ou une valeur obligatoire absente du modèle, **quand** l'utilisateur lance la génération, **alors** celle-ci s'arrête avant de produire le XML et un rapport d'erreur JSON identifie l'échec.
2. **Étant donné** un XML mal formé ou dépourvu des objets requis, **quand** la validation du résultat s'exécute, **alors** l'exécution est signalée comme échouée en JSON et les détails de l'erreur restent disponibles dans le journal.
3. **Étant donné** une génération et une validation réussies, **quand** l'utilisateur consulte le rapport JSON, **alors** celui-ci indique la réussite et ne contient aucune erreur.

### Récit utilisateur 4 - Convertir le XML en FMB si les outils Oracle sont disponibles (Priorité : P3)

En tant que développeur de formulaires disposant des outils de conversion Oracle requis, je peux convertir le XML validé en fichier FMB, afin de poursuivre le travail dans l'environnement Oracle Forms.

**Pourquoi cette priorité** : la conversion en FMB complète le processus en aval, mais dépend d'outils qui ne sont pas nécessairement installés dans tous les environnements.

**Test indépendant** : lorsque les outils de conversion Oracle sont disponibles, convertir un fichier XML valide et vérifier qu'un fichier FMB distinct est produit; en leur absence, vérifier que la conversion est signalée comme indisponible et non comme réussie.

**Scénarios d'acceptation** :

1. **Étant donné** un XML généré valide et des outils de conversion Oracle disponibles, **quand** la conversion s'exécute, **alors** elle réussit et écrit le FMB à part de tout FMB source.
2. **Étant donné** un XML généré valide et des outils de conversion Oracle indisponibles, **quand** le processus vérifie la conversion, **alors** il indique clairement que celle-ci n'a pas pu être lancée tout en conservant le résultat de validation XML.

### Cas limites

- Le fichier YAML est absent, vide, mal formé ou contient une structure non prise en charge; la génération s'arrête et signale l'erreur d'entrée en JSON.
- Le nom du formulaire, le nom d'un objet ou un libellé obligatoire est absent ou vide; la validation identifie la valeur manquante avant la génération du XML.
- Un nom ou un libellé configuré contient des caractères nécessitant un échappement XML; le XML généré reste bien formé et préserve le texte voulu.
- Le template XML est absent ou n'est pas l'export Oracle Forms 14.1.2 requis; la génération s'arrête sans modifier le template ni le FMB source.
- La génération XML réussit, mais sa validation échoue; le résultat n'est pas déclaré réussi et les détails de l'erreur sont conservés.
- Les outils de conversion Oracle sont indisponibles; la génération et la validation XML restent utilisables indépendamment, et la conversion FMB est signalée comme ignorée ou indisponible.

## Exigences *(obligatoire)*

### Règles métier

 - **BR-001** : chaque champ configuré DOIT avoir un nom, un libellé et un type pris en charge avant de pouvoir être généré.
 - **BR-002** : les noms des champs et des boutons DOIVENT être des identifiants Oracle Forms valides et DOIVENT être uniques parmi les champs et les boutons du formulaire.
 - **BR-003** : le type d'un champ DOIT être `text` ou `number`; les types non pris en charge DOIVENT être rejetés avant la génération XML.
 - **BR-004** : un champ PEUT être associé à une colonne de base de données différente du nom de son objet de formulaire. Si aucune colonne n'est configurée, le nom de l'objet champ est utilisé comme nom de colonne.
 - **BR-005** : un champ texte PEUT définir une longueur maximale, qui DOIT être un entier positif. Si elle est omise, le prototype compatible du template fournit la longueur par défaut.
 - **BR-006** : les libellés configurés des champs et des boutons DOIVENT être appliqués aux objets correspondants et conservés dans le résultat généré.

### Exigences fonctionnelles

 - **FR-001** : le plugin DOIT accepter `customer.yaml` comme modèle de formulaire MVP et DOIT en valider la syntaxe et les valeurs obligatoires avant de générer le résultat.
 - **FR-002** : le plugin DOIT générer un formulaire XML Oracle Forms nommé `HELLO_WORLD` à partir d'un template exporté par Oracle Forms 14.1.2.
 - **FR-003** : le résultat MVP DOIT contenir un champ nommé `NOM_CLIENT` et un bouton nommé `BTN_BONJOUR`, sous forme d'objets Oracle Forms distincts.
 - **FR-004** : les noms pris en charge du formulaire et des objets, ainsi que leurs libellés, DOIVENT être configurables dans le modèle YAML et apparaître sur les objets générés correspondants.
 - **FR-005** : le plugin DOIT préserver le template XML original et le FMB source; le XML généré et tout FMB converti DOIVENT être écrits dans des fichiers distincts.
 - **FR-006** : avant de déclarer une réussite, le plugin DOIT vérifier que le XML généré est bien formé et que les objets requis, avec leurs noms, sont présents.
 - **FR-007** : le plugin DOIT produire un rapport JSON par exécution indiquant la réussite ou l'échec, ainsi qu'une collection d'erreurs comportant une description et, si possible, l'emplacement dans le fichier source.
 - **FR-008** : le plugin DOIT conserver les journaux d'erreurs liés aux échecs d'entrée, de génération, de validation XML, de test et de conversion, afin que les utilisateurs puissent diagnostiquer les échecs.
 - **FR-009** : la fonctionnalité DOIT inclure une suite de tests de régression automatisés couvrant la génération valide, la personnalisation pilotée par YAML, les entrées invalides, la validation XML, les objets requis, la préservation du template et les rapports d'erreur.
 - **FR-010** : si les outils de conversion Oracle sont disponibles, le plugin DOIT pouvoir convertir le XML validé en un fichier FMB distinct et signaler le résultat; s'ils sont indisponibles, il DOIT le signaler sans invalider la réussite de la génération et de la validation XML.
 - **FR-011** : la suite de régression automatisée DOIT s'exécuter après chaque modification du code ou d'un artefact généré, et la correction automatique DOIT s'arrêter après au plus trois tentatives pour une opération de génération.

### Entités clés *(si des données sont concernées)*

- **Modèle client** : définition du formulaire fournie en YAML, comprenant le nom du formulaire ainsi que les noms et libellés des objets pris en charge.
- **Objet de formulaire** : élément Oracle Forms nommé, notamment le formulaire MVP, le champ et le bouton, avec son libellé configuré le cas échéant.
- **Template XML** : document XML original exporté par Oracle Forms 14.1.2, utilisé comme base de génération et préservé sans modification.
- **Formulaire généré** : fichier XML distinct contenant les objets de formulaire configurés et validé avant que la réussite soit signalée.
- **Rapport d'exécution** : résultat JSON décrivant la génération, la validation et l'état de la conversion facultative, y compris les erreurs éventuelles.
- **Journal d'erreurs** : détails de diagnostic conservés pour les échecs de validation, de génération, de test ou de conversion.

## Critères de réussite *(obligatoire)*

### Résultats mesurables

- **SC-001** : tous les cas de modèle MVP valides de la suite d'acceptation produisent un XML bien formé contenant exactement un formulaire `HELLO_WORLD`, un champ `NOM_CLIENT` et un bouton `BTN_BONJOUR`.
- **SC-002** : dans 100 % des cas de personnalisation de la suite d'acceptation, les noms et libellés des objets générés correspondent aux valeurs YAML associées.
- **SC-003** : dans 100 % des cas d'entrée ou de sortie invalide de la suite d'acceptation, l'exécution signale un échec en JSON, identifie l'erreur et ne déclare pas l'XML invalide comme réussi.
- **SC-004** : après chaque cas de génération de la suite d'acceptation, le template XML original et tout FMB source fourni restent inchangés.
- **SC-005** : lorsque les outils de conversion Oracle sont disponibles, chaque cas d'acceptation de conversion produit avec succès un FMB distinct; sinon, le rapport indique que la conversion est indisponible.
- **SC-006** : la suite de régression automatisée réussit après la dernière modification et chaque exécution en échec conserve son journal de diagnostic.

## Hypothèses

- Le MVP traite un formulaire par modèle d'entrée et prend en charge un champ et un bouton; les autres types d'objets et les formulaires multiples sont hors périmètre.
- Le modèle YAML fournit les libellés des objets du formulaire; cette spécification n'impose aucun libellé par défaut.
- Le template existant du projet est un export Oracle Forms 14.1.2. S'il est absent ou si sa provenance ne peut pas être établie, la génération doit échouer plutôt que d'utiliser silencieusement un autre template.
- Les utilitaires de conversion Oracle peuvent ne pas être installés. Leur absence empêche uniquement la conversion XML vers FMB, pas la génération ni la validation XML.
- La suite de régression automatisée demandée utilisera pytest; ses comportements requis sont spécifiés ici sans dépendre d'une implémentation de test particulière.
