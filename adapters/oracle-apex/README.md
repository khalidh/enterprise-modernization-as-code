# Adaptateur Oracle APEX

Cet adaptateur transforme `model/customer.yaml` en deux artefacts : un script SQL pour créer la table `CLIENTS` et un export d'application destiné à Oracle APEX 18.2. L'application comprend une liste des clients, un formulaire de création/modification et le bouton configuré dans le modèle.

## Générer le paquet

Depuis la racine du dépôt, avec l'environnement Python du projet :

```powershell
python .\adapters\oracle-apex\generator\generate.py `
  --model .\model\customer.yaml `
  --config .\adapters\oracle-apex\plugin.yaml `
  --output .\generated\oracle-apex
```

Le générateur écrit `01_create_clients_table.sql` et `02_clients_apex_18_2.sql` sous `generated/oracle-apex/`. Les types de colonne proviennent des types YAML; la longueur des champs texte utilise `field.length` si elle est fournie, sinon `default_text_length` dans `plugin.yaml`. `ID_CLIENT` est créé comme clé primaire auto-incrémentée.

## Importer

1. Vérifier que l'instance cible exécute Oracle APEX 18.2 et que le schéma d'analyse choisi est celui de l'application.
2. Exécuter `01_create_clients_table.sql` une fois, connecté au schéma d'analyse. Le script échoue si `CLIENTS` existe déjà; vérifier alors sa structure avant de poursuivre.
3. Dans APEX App Builder, importer `02_clients_apex_18_2.sql` dans le workspace cible et utiliser le schéma d'analyse qui possède `CLIENTS`.
4. L'export utilise le schéma APEX « No Authentication » (`NATIVE_DAD`) pour les essais locaux. Il ne protège pas les données; configurez un schéma d'authentification avant toute exposition hors développement.
5. Après import, tester les parcours liste, création, modification et salutation.

## Limite de validation

Le dépôt contient les médias d'installation APEX 18.2, mais APEX n'est pas enregistré dans la base locale `ORCL`. Les tests vérifient la structure des scripts générés; l'import effectif et l'exécution de l'application doivent être validés dans une instance APEX 18.2 installée. Ne pas déployer l'application avant d'avoir vérifié son schéma d'authentification.