# Modèle de données : générateur YAML vers XML Oracle Forms

## Modèle de formulaire client

Source : `model/customer.yaml`.

| Champ | Type | Obligatoire | Validation |
|---|---|---:|---|
| `form.name` | chaîne | Oui | Non vide; identifie le formulaire dans le XML généré |
| `form.objects` | liste | Oui | Le MVP contient exactement un `field` et un `button` |
| `form.objects[].type` | enum | Oui | `field` ou `button`; chaque type apparaît une fois dans le MVP |
| `form.objects[].name` | chaîne | Oui | Non vide et unique dans le formulaire |
| `form.objects[].label` | chaîne | Oui | Présent; sa valeur est appliquée à l'objet correspondant du template |

L'exemple MVP utilise le formulaire `HELLO_WORLD`, le champ `NOM_CLIENT` et le bouton `BTN_BONJOUR`. Les noms et les libellés sont des données, pas des constantes du générateur. Les autres types d'objets et les formulaires multiples sont hors périmètre.

## Template Oracle Forms

Source : `adapters/oracle-forms/templates/hello_world.xml`.

Le template est un export Oracle Forms 14.1.2 complet contenant un formulaire cible, un champ et un bouton. La génération retrouve ces nœuds existants dans l'export et ne met à jour que leurs propriétés configurées. Tous les autres éléments, y compris les nœuds Oracle inconnus, restent dans l'arbre analysé. Le fichier source est en lecture seule; la génération travaille sur une copie en mémoire ou une copie de travail.

Le fichier template actuel du dépôt est vide. Un export Forms 14.1.2 vérifié doit être fourni avant de pouvoir implémenter ou vérifier ses sélecteurs et le mappage de ses propriétés.

## Exécution de génération

| Champ | Type | Signification |
|---|---|---|
| `run_id` | chaîne | Identifiant unique utilisé pour le répertoire de sortie |
| `form_name` | chaîne | Nom validé utilisé pour regrouper les sorties |
| `status` | enum | `success` uniquement après la validation XML requise; sinon `failure` |
| `stages` | mapping | État de chaque étape : validation YAML, génération, validation XML et conversion FMB |
| `outputs` | liste | Chemins relatifs au dépôt et types d'artefacts générés |
| `errors` | liste | Erreurs structurées associées à l'étape en échec |
| `error_log_path` | chaîne | Chemin du journal texte persistant dans le répertoire d'exécution |

Chaque exécution est stockée sous `generated/oracle-forms/<form-name>/<run-id>/`. Les exécutions en échec conservent le rapport et le journal; un XML invalide n'est pas publié comme résultat réussi.

## Erreur d'exécution

| Champ | Type | Obligatoire | Signification |
|---|---|---:|---|
| `code` | chaîne | Oui | Catégorie d'erreur stable et lisible par machine |
| `stage` | chaîne | Oui | Validation YAML, génération XML, validation XML, exécution des tests, réparation IA ou conversion FMB |
| `message` | chaîne | Oui | Description compréhensible et exploitable |
| `source` | chaîne | Non | Chemin de l'entrée ou de l'artefact, s'il est connu |
| `line` | entier | Non | Numéro de ligne source à partir de 1, si disponible |
| `column` | entier | Non | Numéro de colonne source à partir de 1, si disponible |

## Cycle d'état

`created -> yaml_validated -> xml_generated -> xml_validated -> [fmb_converted | fmb_unavailable] -> success`

Tout échec d'une étape obligatoire entraîne l'état `failure`, conserve un rapport et un journal d'erreurs et empêche la publication d'un XML invalide. La réparation par IA peut répéter les étapes de génération, validation et test d'un candidat jusqu'à trois fois; chaque tentative échouée est enregistrée. Le template original, le YAML d'entrée et le FMB source ne sont jamais modifiés par le processus.