# Recherche : générateur YAML vers XML Oracle Forms

## Décisions

### Pipeline Python et limites des dépendances

- **Décision** : utiliser Python 3, PyYAML, `xml.etree.ElementTree` de la bibliothèque standard et pytest. Ne pas inclure les utilitaires Oracle Forms ni le fournisseur de réparation IA parmi les dépendances d'exécution obligatoires.
- **Justification** : ces choix sont explicitement demandés par la fonctionnalité. ElementTree évite d'ajouter une dépendance d'exécution XML, tandis que PyYAML fournit la prise en charge requise des entrées YAML. Les outils externes facultatifs ne doivent pas bloquer la génération et la validation XML.
- **Solutions envisagées** : la construction du XML sous forme de chaînes a été écartée, car elle risque de provoquer des erreurs d'échappement et une perte de structure du template. Rendre obligatoires les paquets Oracle ou IA a été écarté, car ces installations ne sont ni présentes ni spécifiées dans le dépôt.

### Chargement et validation YAML

- **Décision** : charger le YAML avec le chargeur sûr de PyYAML, puis effectuer une validation structurelle et sémantique explicite avant toute génération ou publication de résultat.
- **Justification** : le chargement sûr évite de construire des objets Python arbitraires à partir de l'entrée. Un module de validation distinct rend testable le contrôle constitutionnel imposant la validation avant la génération.
- **Solutions envisagées** : lire directement les valeurs d'une structure YAML non vérifiée a été écarté, car une entrée mal formée ou incomplète pourrait créer des artefacts partiels.

### Génération et préservation du XML

- **Décision** : analyser un véritable export XML Oracle Forms 14.1.2 avec ElementTree, repérer ses nœuds existants correspondant au formulaire, au champ et au bouton cibles, puis ne mettre à jour que les noms et libellés configurés dans un arbre de travail. Préserver les éléments et espaces de noms sans rapport avec la génération; ne jamais sérialiser le résultat sur le template source.
- **Justification** : mettre à jour les objets exportés en place limite les hypothèses sur la structure XML propriétaire d'Oracle et préserve les nœuds sans rapport avec la génération. Le template original reste une entrée immuable.
- **Solutions envisagées** : construire un document Oracle Forms à partir de zéro a été écarté, car le résultat ne serait pas fondé sur le format d'export pris en charge. Deviner les noms des éléments XML sans disposer d'un export réel a également été écarté.
- **Prérequis de validation** : `adapters/oracle-forms/templates/hello_world.xml` est actuellement vide. Avant de définir les sélecteurs ou de revendiquer la compatibilité Oracle, l'implémentation doit le remplacer par un export Oracle Forms 14.1.2 vérifié. Les tests doivent vérifier l'espace de noms de l'export réel et la préservation de sa structure.

### Résultats, rapports et conservation des erreurs

- **Décision** : créer un répertoire d'exécution unique sous `generated/oracle-forms/` avant la validation. Y stocker le rapport JSON et le journal d'erreurs, que l'exécution réussisse ou échoue; ne publier le XML qu'après validation. Enregistrer tout FMB converti dans un fichier distinct du même répertoire d'exécution.
- **Justification** : les répertoires d'exécution uniques préservent les résultats et diagnostics précédents. La copie de travail empêche qu'un candidat invalide soit présenté comme un résultat réussi. L'absence de convertisseur Oracle est représentée par l'état indisponible, sans remettre en cause un XML valide.
- **Solutions envisagées** : réutiliser un chemin de sortie fixe a été écarté, car une exécution ultérieure pourrait effacer les journaux précédents ou remplacer partiellement un formulaire valide.

### Intégration de la conversion Oracle XML vers FMB

- **Décision** : définir le convertisseur comme un processus externe configuré dans `plugin.yaml`, avec un exécutable et une liste d'arguments contenant des placeholders explicites pour l'entrée et la sortie. Vérifier que l'exécutable configuré peut être lancé; l'appeler sans passer par un shell; consigner dans le rapport les états indisponible, réussite ou échec.
- **Justification** : le dépôt ne fournit ni nom de commande Oracle Forms, ni chemin d'installation, ni contrat de variable d'environnement, ni script de conversion. La configuration évite de coder en dur une commande non vérifiée et permet à chaque installation Forms 14.1.2 sous licence de fournir l'appel pris en charge.
- **Solutions envisagées** : coder en dur le nom d'un utilitaire connu de mémoire ou supposer qu'il se trouve dans `PATH` a été écarté, car le dépôt actuel ne fournit aucun élément propre à une version. Exiger les outils Oracle à chaque exécution a également été écarté, car la génération XML reste utile indépendamment.
- **Dépendance d'environnement restante** : pour tester la conversion FMB, un opérateur doit configurer la commande et la tester avec son installation Oracle Forms 14.1.2. Ce plan ne prescrit aucun nom de commande.

### Orchestration des tests et réparation par IA

- **Décision** : conserver l'appel à pytest dans `test_runner.py`, lancé explicitement par le développement/la CI et après chaque modification issue d'une réparation IA. Garder la réparation IA dans `repair_loop.py`, derrière un appel indépendant du fournisseur et configuré séparément. Autoriser au plus trois tentatives de réparation; chacune est suivie d'une validation et de la suite de régression.
- **Justification** : la séparation des responsabilités rend la génération déterministe et permet d'auditer la sortie de pytest ainsi que les modifications de l'IA. Une interface indépendante du fournisseur satisfait l'exigence de réparation IA sans choisir de fournisseur ni imposer d'identifiants aux processus qui ne font pas appel à la réparation.
- **Solutions envisagées** : intégrer le pilotage du processus pytest à la génération XML a été écarté, car cela lierait le comportement du produit aux tests de développement. Une réparation sans limite ou une dépendance directe à une IA a été écartée par la constitution et parce que le fournisseur n'est pas spécifié.

## Risques et mesures d'atténuation

- **La compatibilité XML Oracle ne peut pas être établie avec un template vide** : imposer un véritable export Forms 14.1.2 comme condition préalable à l'implémentation; ajouter des tests de conversion aller-retour et de préservation des objets non ciblés sur cet export.
- **La sérialisation par ElementTree peut normaliser les préfixes ou la mise en forme** : valider la gestion des espaces de noms et la préservation sémantique des objets avec le véritable template. Ne pas exiger une égalité octet par octet de la mise en forme du XML généré; exiger que le fichier template original reste inchangé.
- **L'appel du convertisseur varie selon l'installation** : rendre configurables l'exécutable et la construction des arguments, éviter l'interpolation par le shell et utiliser un faux convertisseur dans les tests par défaut.
- **Les modifications générées par l'IA peuvent endommager du contenu sans rapport** : limiter la réparation à un candidat généré dans une copie de travail, revalider après chaque tentative, conserver les différences et les journaux, puis s'arrêter après le troisième échec.