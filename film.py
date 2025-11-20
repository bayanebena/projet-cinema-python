"""
Module : film
Responsable : Personne 1
Fonction : gestion des films (sans les salles ni les réservations).
"""

from typing import Optional, Dict, List


class FilmDejaExistantError(Exception):
    pass


class FilmInexistantError(Exception):
    pass


class Film:
    """
    Représente un film projeté au cinéma.
    """

    def __init__(self, titre: str, duree: int, genre: Optional[str] = None):
        if duree <= 0:
            raise ValueError("La durée d'un film doit être strictement positive.")

        self.titre = titre
        self.duree = duree
        self.genre = genre

    def __str__(self) -> str:
        base = f"{self.titre} ({self.duree} min)"
        return f"{base} - {self.genre}" if self.genre else base


class GestionFilms:
    """
    Gère un ensemble de films : ajout, suppression, recherche, listing.
    """

    def __init__(self):
        self._films: Dict[str, Film] = {}

    def ajouter_film(self, film: Film) -> None:
        if film.titre in self._films:
            raise FilmDejaExistantError(f"Le film '{film.titre}' existe déjà.")
        self._films[film.titre] = film

    def supprimer_film(self, titre: str) -> None:
        if titre not in self._films:
            raise FilmInexistantError(f"Le film '{titre}' n'existe pas.")
        del self._films[titre]

    def get_film(self, titre: str) -> Film:
        if titre not in self._films:
            raise FilmInexistantError(f"Le film '{titre}' n'existe pas.")
        return self._films[titre]

    def lister_films(self) -> List[Film]:
        return list(self._films.values())


if __name__ == "__main__":
    # Petit test rapide, optionnel
    gestion = GestionFilms()
    gestion.ajouter_film(Film("Inception", 148, "Science-fiction"))
    gestion.ajouter_film(Film("Avatar", 162, "Aventure"))

    print("Films enregistrés :")
    for f in gestion.lister_films():
        print(" -", f)
