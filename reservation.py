"""
Module : reservation
Responsable : Personne 2
Fonction : gestion des séances et des réservations.
"""
from typing import List, Dict
from dataclasses import dataclass
import string

from film import Film, FilmInexistantError
from salle import Salle


class SallePleineError(Exception):
    """Levée lorsqu'on tente de réserver plus de places que la capacité restante."""
    pass


@dataclass
class Reservation:
    client_nom: str
    place: str  
    seance_id: int

    def __str__(self) -> str:
        return f"Réservation: {self.client_nom} - Place {self.place} (séance #{self.seance_id})"


class Seance:
    """Représente une séance : un film projeté dans une salle à un horaire donné.

    La gestion des places réservées est tenue ici.
    """

    def __init__(self, seance_id: int, film: Film, salle: Salle, horaire: str):
        self.id = seance_id
        self.film = film
        self.salle = salle
        self.horaire = horaire
        self._reservations: List[Reservation] = []
        self._places_reservees = set()  # set de places réservées, ex: {'A1', 'B2'}
        self.plan = self._generer_plan_salle()

    def _generer_plan_salle(self):
        nb_places = self.salle.capacite
        colonnes = 12  # nombre de colonnes par défaut
        lignes = max(1, nb_places // colonnes + (1 if nb_places % colonnes else 0))
        alphabet = string.ascii_uppercase
        plan = []
        cpt = 0
        for i in range(lignes):
            row = []
            for j in range(colonnes):
                if cpt < nb_places:
                    row.append(f"{alphabet[i]}{j+1}")
                    cpt += 1
            plan.append(row)
        return plan

    def places_disponibles(self) -> int:
        return self.salle.capacite - len(self._places_reservees)

    def est_place_disponible(self, place: str) -> bool:
        return place not in self._places_reservees

    def reserver(self, client_nom: str, place: str) -> Reservation:
        if not self.est_place_disponible(place):
            raise SallePleineError(f"La place {place} n'est pas disponible.")
        self._places_reservees.add(place)
        r = Reservation(client_nom, place, self.id)
        self._reservations.append(r)
        return r

    def lister_reservations(self) -> List[Reservation]:
        return list(self._reservations)

    def __str__(self) -> str:
        return (
            f"Séance #{self.id} : {self.film.titre} - Salle {self.salle.numero} - "
            f"Horaire: {self.horaire} - Places dispo: {self.places_disponibles()}/{self.salle.capacite}"
        )


class GestionSeances:
    """Gère l'ensemble des séances."""

    def __init__(self):
        self._seances: Dict[int, Seance] = {}
        self._next_id = 1

    def creer_seance(self, film: Film, salle: Salle, horaire: str) -> Seance:
        s = Seance(self._next_id, film, salle, horaire)
        self._seances[self._next_id] = s
        self._next_id += 1
        return s

    def get_seance(self, seance_id: int) -> Seance:
        if seance_id not in self._seances:
            raise KeyError(f"La séance #{seance_id} n'existe pas.")
        return self._seances[seance_id]

    def lister_seances(self) -> List[Seance]:
        return list(self._seances.values())


# petit test rapide
if __name__ == "__main__":
    from film import Film
    from salle import Salle

    f = Film("Test Movie", 100, "Drame")
    s = Salle(1, 10)
    gs = GestionSeances()
    se = gs.creer_seance(f, s, "2025-12-31 20:00")
    print(se)
    try:
        se.reserver("Alice", "A1")
        se.reserver("Bob", "A2")
    except Exception as e:
        print("Erreur:", e)
    print(se)
    for r in se.lister_reservations():
        print(r)
