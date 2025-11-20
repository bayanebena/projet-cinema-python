# Projet Python S1 – Application de Gestion de Cinéma

Ce dépôt contient la partie réalisée par la Personne 1, dédiée à la gestion des films et des salles dans le cadre du projet de cinéma du module Python S1.

## Objectifs du projet

- Développer une application modulaire en Python.
- Utiliser la programmation orientée objet (POO).
- Créer des interactions cohérentes entre plusieurs classes.
- Préparer une base solide pour les autres parties du projet (gestion des réservations, gestion des séances, etc.).

## Contenu du dépôt

Ce dépôt contient trois fichiers principaux :

### 1. `film.py`
Module responsable de la gestion des films.  
Il contient :
- La classe `Film` (titre, durée, genre).
- La classe `GestionFilms` permettant d’ajouter, supprimer, rechercher et lister les films enregistrés.

### 2. `salle.py`
Module responsable de la gestion des salles.  
Il contient :
- La classe `Salle` (numéro, capacité, film projeté).
- La classe `GestionSalles` permettant d’ajouter, supprimer, rechercher et lister les salles.
- Une méthode permettant d’affecter un film à une salle.

### 3. `menu.py`
Programme principal permettant d’utiliser la partie Personne 1 de manière interactive via un menu texte.  
Ce menu permet :
- D’ajouter un film.
- D’ajouter une salle.
- De lister les films.
- De lister les salles.
- D’affecter un film à une salle.
- D’afficher les salles avec les films projetés.

## Structure du projet

