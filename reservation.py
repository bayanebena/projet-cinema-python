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
    """Exception levée lorsqu'on tente de réserver une place déjà prise ou que la salle est pleine."""
    pass


@dataclass
class Reservation:
    """
    Représente une réservation pour une séance, pour une place précise.
    """
    client_nom: str
    place: str  # ex: H12
    seance_id: int

    def __str__(self) -> str:
        return f"Réservation: {self.client_nom} - Place {self.place} (séance #{self.seance_id})"


class Seance:
    """
    Représente une séance : un film projeté dans une salle à un horaire donné.
    Gère le plan de la salle et les réservations individuelles par place.
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
        """
        Génère le plan de la salle sous forme de liste de listes, chaque place est identifiée par une lettre et un numéro.
        """
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
        """Retourne le nombre de places encore disponibles pour la séance."""
        return self.salle.capacite - len(self._places_reservees)

    def est_place_disponible(self, place: str) -> bool:
        """Vérifie si une place donnée est disponible."""
        return place not in self._places_reservees

    def reserver(self, client_nom: str, place: str) -> Reservation:
        """Réserve une place précise pour un client, lève une exception si la place est déjà prise."""
        if not self.est_place_disponible(place):
            raise SallePleineError(f"La place {place} n'est pas disponible.")
        self._places_reservees.add(place)
        r = Reservation(client_nom, place, self.id)
        self._reservations.append(r)
        return r

    def lister_reservations(self) -> List[Reservation]:
        """Retourne la liste des réservations pour cette séance."""
        return list(self._reservations)

    def annuler_reservation(self, client_nom: str, place: str) -> bool:
        """Annule la réservation pour le client et la place donnée. Retourne True si annulée."""
        # Trouver la réservation correspondante
        to_remove = None
        for r in self._reservations:
            if r.client_nom == client_nom and r.place == place:
                to_remove = r
                break
        if to_remove:
            try:
                self._reservations.remove(to_remove)
            except ValueError:
                pass
            # libérer la place
            if place in self._places_reservees:
                self._places_reservees.remove(place)
            return True
        return False

    def __str__(self) -> str:
        # Affiche les infos principales de la séance
        return (
            f"Séance #{self.id} : {self.film.titre} - Salle {self.salle.numero} - "
            f"Horaire: {self.horaire} - Places dispo: {self.places_disponibles()}/{self.salle.capacite}"
        )


class GestionSeances:
    """
    Gère l'ensemble des séances du cinéma.
    """

    def __init__(self):
        self._seances: Dict[int, Seance] = {}
        self._next_id = 1

    def creer_seance(self, film: Film, salle: Salle, horaire: str) -> Seance:
        """Crée une nouvelle séance avec un film, une salle et un horaire."""
        s = Seance(self._next_id, film, salle, horaire)
        self._seances[self._next_id] = s
        self._next_id += 1
        return s

    def get_seance(self, seance_id: int) -> Seance:
        """Retourne la séance par son identifiant, lève une exception si elle n'existe pas."""
        if seance_id not in self._seances:
            raise KeyError(f"La séance #{seance_id} n'existe pas.")
        return self._seances[seance_id]

    def lister_seances(self) -> List[Seance]:
        """Retourne la liste de toutes les séances enregistrées."""
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
