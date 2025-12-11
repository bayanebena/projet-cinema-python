"""
Module : film
Fonction : gestion des films (sans les salles ni les réservations).
"""

from typing import Optional, Dict, List
import csv
import os


class FilmDejaExistantError(Exception):
    """Exception levée si on tente d'ajouter un film déjà existant."""
    pass


class FilmInexistantError(Exception):
    """Exception levée si on tente d'accéder à un film qui n'existe pas."""
    pass


class Film:
    """
    Représente un film projeté au cinéma.
    Chaque film a un titre, une durée et un genre.
    """

    def __init__(self, titre: str, duree: int, genre: Optional[str] = None, affiche: Optional[str] = None):
        # Vérifie que la durée est positive
        if duree <= 0:
            raise ValueError("La durée d'un film doit être strictement positive.")

        self.titre = titre
        self.duree = duree
        self.genre = genre
        # chemin relatif ou None vers une image d'affiche (png/jpg/gif)
        self.affiche = affiche

    def __str__(self) -> str:
        # Affiche le film avec son genre si disponible
        base = f"{self.titre} ({self.duree} min)"
        return f"{base} - {self.genre}" if self.genre else base


class GestionFilms:
    """
    Gère un ensemble de films : ajout, suppression, recherche, listing.
    """

    def __init__(self):
        self._films: Dict[str, Film] = {}

    def ajouter_film(self, film: Film) -> None:
        """Ajoute un film au système, lève une exception si le titre existe déjà."""
        if film.titre in self._films:
            raise FilmDejaExistantError(f"Le film '{film.titre}' existe déjà.")
        self._films[film.titre] = film

    def supprimer_film(self, titre: str) -> None:
        """Supprime un film par son titre, lève une exception si il n'existe pas."""
        if titre not in self._films:
            raise FilmInexistantError(f"Le film '{titre}' n'existe pas.")
        del self._films[titre]

    def get_film(self, titre: str) -> Film:
        """Retourne le film par son titre, lève une exception si il n'existe pas."""
        if titre not in self._films:
            raise FilmInexistantError(f"Le film '{titre}' n'existe pas.")
        return self._films[titre]

    def lister_films(self) -> List[Film]:
        """Retourne la liste de tous les films enregistrés."""
        return list(self._films.values())


def charger_films_csv(path_csv: str) -> GestionFilms:
    """
    Charge les films depuis un fichier CSV et retourne un objet GestionFilms pré-rempli.
    """
    gestion = GestionFilms()
    if not os.path.exists(path_csv):
        return gestion
    with open(path_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                titre = row['titre']
                duree = int(row['duree'])
                genre = row.get('genre', None)
                affiche = row.get('affiche', None)
                film = Film(titre, duree, genre, affiche)
                gestion.ajouter_film(film)
            except Exception:
                pass  # Ignore les lignes invalides
    return gestion


if __name__ == "__main__":
    # Petit test rapide, optionnel
    gestion = GestionFilms()
    gestion.ajouter_film(Film("Inception", 148, "Science-fiction"))
    gestion.ajouter_film(Film("Avatar", 162, "Aventure"))

    print("Films enregistrés :")
    for f in gestion.lister_films():
        print(" -", f)
