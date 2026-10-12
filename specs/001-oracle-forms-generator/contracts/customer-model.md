# Contrat du modèle client

`model/customer.yaml` est la source de vérité pour le nom et le titre du formulaire généré, ses champs, ses boutons, leurs libellés et leurs types, ainsi que les associations aux colonnes de la base de données.

```yaml
form:
  name: HELLO_WORLD
  title: Gestion des clients
  fields:
    - name: ID_CLIENT2
      type: number
      label: Id Client2
      column: ID_CLIENT
    - name: NOM_CLIENT2
      type: text
      label: Nom du client
      column: NOM_CLIENT
    - name: EMAIL
      type: text
      label: Email
      column: EMAIL
  buttons:
    - name: BTN_BONJOUR
      label: Dire bonjour
```

`form.name`, le `name` et le `label` de chaque objet, ainsi que le `type` pris en charge de chaque champ sont obligatoires. Les noms doivent être des identifiants Oracle Forms valides et uniques parmi les champs et les boutons. Les types de champ pris en charge sont `text` et `number`.

`field.column` associe facultativement le nom de l'élément Forms généré à une colonne de base de données. Par défaut, sa valeur est `field.name`. `field.length` définit facultativement la longueur maximale des champs texte; sinon, la valeur par défaut provient du prototype correspondant dans le template.

Le template XML Oracle Forms fournit la structure du formulaire et les prototypes de présentation des champs et des boutons. Pendant la génération, les éléments de champ et de bouton du bloc de données cible sont reconstruits à partir du YAML : les éléments absents du modèle sont supprimés du résultat généré, et les éléments nommés dans le modèle sont créés à partir d'un prototype compatible même si leurs noms ne figurent pas dans le template. Le template original reste inchangé. Le bloc de données, le canevas, la fenêtre et les autres structures propres à Oracle sont préservés.