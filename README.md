# Application de gestion de cinéma

## Description
Ce projet est une application Python permettant de gérer un cinéma : films, salles, séances, réservations. Il propose une interface graphique moderne (Tkinter) pour le client et le gestionnaire, avec gestion des places individuelles et plan de salle interactif.

## Fonctionnalités principales
- **Gestionnaire** :
  - Ajouter/supprimer des films et des salles
  - Affecter un film à une salle
  - Créer des séances (film, salle, horaire)
  - Visualiser les films et salles existants
- **Client** :
  - Voir les films à l'affiche
  - Voir les séances disponibles
  - Réserver une place sur le plan de salle 
  - Saisie du nom et confirmation de la réservation
- **Gestion des exceptions** :
  - Salle pleine, film inexistant, saisie invalide, etc.
- **Données initiales** :
  - 10 salles et 10 films sont chargés automatiquement au lancement
  - 5 séances sont créées par défaut

## Installation
### Prérequis
- Python 3.7 ou plus recommandé
- Tkinter (installé par défaut sur Windows, à installer sur Ubuntu si besoin)

#### Ubuntu
```bash
sudo apt update
sudo apt install python3 python3-tk
```

#### Windows
- Installez Python depuis [python.org](https://www.python.org/downloads/)
- Tkinter est inclus par défaut

## Lancement
Dans le dossier du projet, lancez simplement :
```bash
python3 gui.py
```
Ou sur Windows :
```bat
python gui.py
```

## Utilisation
- **Au lancement** :
  - Choisissez le mode Client ou Gestionnaire
- **Client** :
  - Voir les films et séances
  - Cliquez sur une séance pour afficher le plan de salle
  - Cliquez sur une place verte pour réserver, saisissez votre nom
- **Gestionnaire** :
  - Ajoutez/supprimez films et salles
  - Affectez un film à une salle
  - Créez des séances
  - Les listes de films et salles sont affichées avant chaque action

## Structure du projet
- `film.py` : gestion des films
- `salle.py` : gestion des salles
- `reservation.py` : gestion des séances et réservations
- `gui.py` : interface graphique principale
- `films_init.csv` : films chargés au démarrage
- `README.md` : ce guide

## Remarques
- Les couleurs du plan de salle :
  - **Vert** : place disponible
  - **Rouge** : place réservée
- Les données sont en mémoire (pas de base de données)
- Compatible Windows et Ubuntu


