"""
Module : reservation
Responsable : Personne 2
Fonction : gestion des séances et des réservations.
"""
from typing import List, Dict
from dataclasses import dataclass

from film import Film, FilmInexistantError
from salle import Salle


class SallePleineError(Exception):
    """Levée lorsqu'on tente de réserver plus de places que la capacité restante."""
    pass


@dataclass
class Reservation:
    client_nom: str
    nb_places: int
    seance_id: int

    def __str__(self) -> str:
        return f"Réservation: {self.client_nom} - {self.nb_places} place(s) (séance #{self.seance_id})"


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
        self._places_reservees = 0

    def places_disponibles(self) -> int:
        return self.salle.capacite - self._places_reservees

    def reserver(self, client_nom: str, nb_places: int) -> Reservation:
        if nb_places <= 0:
            raise ValueError("Le nombre de places doit être strictement positif.")
        if nb_places > self.places_disponibles():
            raise SallePleineError("Pas assez de places disponibles pour cette séance.")
        self._places_reservees += nb_places
        r = Reservation(client_nom, nb_places, self.id)
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
        se.reserver("Alice", 3)
        se.reserver("Bob", 8)
    except Exception as e:
        print("Erreur:", e)
    print(se)
    for r in se.lister_reservations():
        print(r)
