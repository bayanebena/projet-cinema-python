"""
Module : salle
Responsable : Personne 1
Fonction : gestion des salles et affectation de films à des salles.
"""

import os
import sys
from typing import Dict, List, Optional

# Assure que le répertoire du fichier est dans sys.path
# pour que l'import "from film import ..." fonctionne,
# même lorsque VS Code lance le script avec un autre cwd.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from film import Film, GestionFilms


class SalleDejaExistanteError(Exception):
    pass


class SalleInexistanteError(Exception):
    pass


class Salle:
    """
    Représente une salle de cinéma pouvant projeter un film.
    """

    def __init__(self, numero: int, capacite: int):
        if capacite <= 0:
            raise ValueError("La capacité d'une salle doit être strictement positive.")

        self.numero = numero
        self.capacite = capacite
        self.film: Optional[Film] = None  # film actuellement projeté dans la salle

    def affecter_film(self, film: Film) -> None:
        """
        Associe un film à la salle.
        """
        self.film = film

    def __str__(self) -> str:
        if self.film:
            return f"Salle {self.numero} ({self.capacite} places) - Film: {self.film.titre}"
        else:
            return f"Salle {self.numero} ({self.capacite} places) - Aucun film"


class GestionSalles:
    """
    Gère un ensemble de salles : ajout, suppression, recherche,
    et affectation de films à des salles.
    """

    def __init__(self):
        self._salles: Dict[int, Salle] = {}

    def ajouter_salle(self, salle: Salle) -> None:
        if salle.numero in self._salles:
            raise SalleDejaExistanteError(f"La salle {salle.numero} existe déjà.")
        self._salles[salle.numero] = salle

    def supprimer_salle(self, numero: int) -> None:
        if numero not in self._salles:
            raise SalleInexistanteError(f"La salle {numero} n'existe pas.")
        del self._salles[numero]

    def get_salle(self, numero: int) -> Salle:
        if numero not in self._salles:
            raise SalleInexistanteError(f"La salle {numero} n'existe pas.")
        return self._salles[numero]

    def lister_salles(self) -> List[Salle]:
        return list(self._salles.values())

    def affecter_film_a_salle(self, numero_salle: int, film: Film) -> None:
        """
        Associe un film à une salle.
        """
        salle = self.get_salle(numero_salle)
        salle.affecter_film(film)


def salles_par_defaut() -> GestionSalles:
    gestion = GestionSalles()
    try:
        gestion.ajouter_salle(Salle(1, 100))
        gestion.ajouter_salle(Salle(2, 80))
        gestion.ajouter_salle(Salle(3, 120))
        gestion.ajouter_salle(Salle(4, 60))
        gestion.ajouter_salle(Salle(5, 150))
        gestion.ajouter_salle(Salle(6, 90))
        gestion.ajouter_salle(Salle(7, 110))
        gestion.ajouter_salle(Salle(8, 70))
        gestion.ajouter_salle(Salle(9, 130))
        gestion.ajouter_salle(Salle(10, 140))
    except Exception:
        pass
    return gestion


def main():
    """
    Petit scénario de test pour vérifier que tout fonctionne :
    - création de films via GestionFilms
    - création de salles
    - affectation de films aux salles
    - affichage du résultat
    """
    gestion_films = GestionFilms()
    gestion_salles = GestionSalles()

    # Création de quelques films
    f1 = Film("Inception", 148, "Science-fiction")
    f2 = Film("Avatar", 162, "Aventure")

    gestion_films.ajouter_film(f1)
    gestion_films.ajouter_film(f2)

    # Création de salles
    gestion_salles.ajouter_salle(Salle(1, 100))
    gestion_salles.ajouter_salle(Salle(2, 80))

    # Affectation des films aux salles
    gestion_salles.affecter_film_a_salle(1, f1)
    gestion_salles.affecter_film_a_salle(2, f2)

    # Affichage
    print("Salles et films affectés :")
    for s in gestion_salles.lister_salles():
        print(" -", s)


if __name__ == "__main__":
    main()

