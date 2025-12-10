import tkinter as tk
from tkinter import messagebox, simpledialog
from film import GestionFilms, FilmInexistantError
from salle import GestionSalles, SalleInexistanteError
from reservation import GestionSeances, SallePleineError
import os
from film import charger_films_csv

class CinemaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cinéma - Application Graphique")
        chemin_csv = os.path.join(os.path.dirname(__file__), "films_init.csv")
        self.gestion_films = charger_films_csv(chemin_csv)
        self.gestion_salles = GestionSalles()
        self.gestion_seances = GestionSeances()
        self.menu_principal()

    def menu_principal(self):
        self.clear()
        tk.Label(self.root, text="Bienvenue au Cinéma!", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Client", width=20, command=self.menu_client).pack(pady=5)
        tk.Button(self.root, text="Gestionnaire", width=20, command=self.menu_gestionnaire).pack(pady=5)
        tk.Button(self.root, text="Quitter", width=20, command=self.root.quit).pack(pady=5)

    def menu_client(self):
        self.clear()
        tk.Label(self.root, text="Menu Client", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="Voir les films à l'affiche", width=30, command=self.afficher_films).pack(pady=5)
        tk.Button(self.root, text="Réserver une place", width=30, command=self.reserver_place).pack(pady=5)
        tk.Button(self.root, text="Voir les séances", width=30, command=self.afficher_seances).pack(pady=5)
        tk.Button(self.root, text="Retour", width=30, command=self.menu_principal).pack(pady=5)

    def menu_gestionnaire(self):
        self.clear()
        tk.Label(self.root, text="Menu Gestionnaire", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="Ajouter un film", width=30, command=self.ajouter_film).pack(pady=5)
        tk.Button(self.root, text="Supprimer un film", width=30, command=self.supprimer_film).pack(pady=5)
        tk.Button(self.root, text="Ajouter une salle", width=30, command=self.ajouter_salle).pack(pady=5)
        tk.Button(self.root, text="Supprimer une salle", width=30, command=self.supprimer_salle).pack(pady=5)
        tk.Button(self.root, text="Affecter un film à une salle", width=30, command=self.affecter_film_salle).pack(pady=5)
        tk.Button(self.root, text="Créer une séance", width=30, command=self.creer_seance).pack(pady=5)
        tk.Button(self.root, text="Retour", width=30, command=self.menu_principal).pack(pady=5)

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def afficher_films(self):
        self.clear()
        tk.Label(self.root, text="Films à l'affiche", font=("Arial", 14)).pack(pady=10)
        films = self.gestion_films.lister_films()
        if not films:
            tk.Label(self.root, text="Aucun film à l'affiche.").pack()
        else:
            for f in films:
                tk.Label(self.root, text=str(f)).pack()
        tk.Button(self.root, text="Retour", command=self.menu_client).pack(pady=10)

    def afficher_seances(self):
        self.clear()
        tk.Label(self.root, text="Séances", font=("Arial", 14)).pack(pady=10)
        seances = self.gestion_seances.lister_seances()
        if not seances:
            tk.Label(self.root, text="Aucune séance disponible.").pack()
        else:
            for s in seances:
                tk.Label(self.root, text=str(s)).pack()
        tk.Button(self.root, text="Retour", command=self.menu_client).pack(pady=10)

    def reserver_place(self):
        seances = self.gestion_seances.lister_seances()
        if not seances:
            messagebox.showinfo("Info", "Aucune séance disponible.")
            return
        seance_ids = [s.id for s in seances]
        try:
            seance_id = simpledialog.askinteger("Réservation", f"Numéro de séance ({seance_ids}):")
            if seance_id is None:
                raise ValueError("Le numéro de séance doit être un entier.")
        except Exception:
            messagebox.showerror("Erreur", "Entrée invalide pour le numéro de séance : un entier est attendu.")
            return
        client_nom = simpledialog.askstring("Réservation", "Votre nom:")
        try:
            nb_places = simpledialog.askinteger("Réservation", "Nombre de places:")
            if nb_places is None or nb_places <= 0:
                raise ValueError("Le nombre de places doit être un entier strictement positif.")
        except Exception:
            messagebox.showerror("Erreur", "Entrée invalide pour le nombre de places : un entier strictement positif est attendu.")
            return
        try:
            seance = self.gestion_seances.get_seance(seance_id)
            reservation = seance.reserver(client_nom, nb_places)
            messagebox.showinfo("Succès", f"Réservation confirmée: {reservation}")
        except SallePleineError as e:
            messagebox.showerror("Erreur", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def ajouter_film(self):
        titre = simpledialog.askstring("Ajouter Film", "Titre du film:")
        try:
            duree = simpledialog.askinteger("Ajouter Film", "Durée (min):")
            if duree is None or duree <= 0:
                raise ValueError("La durée doit être un entier strictement positif.")
        except Exception:
            messagebox.showerror("Erreur", "Entrée invalide pour la durée : un entier strictement positif est attendu.")
            return
        genre = simpledialog.askstring("Ajouter Film", "Genre:")
        from film import Film, FilmDejaExistantError
        try:
            film = Film(titre, duree, genre)
            self.gestion_films.ajouter_film(film)
            messagebox.showinfo("Succès", f"Film ajouté: {film}")
        except FilmDejaExistantError:
            messagebox.showerror("Erreur", f"Le film '{titre}' existe déjà.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def supprimer_film(self):
        films = self.gestion_films.lister_films()
        if not films:
            messagebox.showinfo("Info", "Aucun film à supprimer.")
            return
        films_str = "\n".join(str(f) for f in films)
        messagebox.showinfo("Films existants", f"Films enregistrés :\n{films_str}")
        titre = simpledialog.askstring("Supprimer Film", "Titre du film à supprimer:")
        try:
            self.gestion_films.supprimer_film(titre)
            messagebox.showinfo("Succès", f"Film supprimé: {titre}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def ajouter_salle(self):
        try:
            numero = simpledialog.askinteger("Ajouter Salle", "Numéro de la salle:")
            if numero is None or numero <= 0:
                raise ValueError("Le numéro de salle doit être un entier strictement positif.")
        except Exception:
            messagebox.showerror("Erreur", "Entrée invalide pour le numéro de salle : un entier strictement positif est attendu.")
            return
        try:
            capacite = simpledialog.askinteger("Ajouter Salle", "Capacité:")
            if capacite is None or capacite <= 0:
                raise ValueError("La capacité doit être un entier strictement positif.")
        except Exception:
            messagebox.showerror("Erreur", "Entrée invalide pour la capacité : un entier strictement positif est attendu.")
            return
        from salle import Salle, SalleDejaExistanteError
        try:
            salle = Salle(numero, capacite)
            self.gestion_salles.ajouter_salle(salle)
            messagebox.showinfo("Succès", f"Salle ajoutée: {salle}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def supprimer_salle(self):
        salles = self.gestion_salles.lister_salles()
        if not salles:
            messagebox.showinfo("Info", "Aucune salle à supprimer.")
            return
        salles_str = "\n".join(str(s) for s in salles)
        messagebox.showinfo("Salles existantes", f"Salles enregistrées :\n{salles_str}")
        try:
            numero = simpledialog.askinteger("Supprimer Salle", "Numéro de la salle à supprimer:")
            if numero is None:
                return
            self.gestion_salles.supprimer_salle(numero)
            messagebox.showinfo("Succès", f"Salle supprimée: {numero}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def affecter_film_salle(self):
        numero = simpledialog.askinteger("Affecter Film", "Numéro de la salle:")
        titre = simpledialog.askstring("Affecter Film", "Titre du film:")
        try:
            film = self.gestion_films.get_film(titre)
            try:
                salle = self.gestion_salles.get_salle(numero)
            except Exception:
                messagebox.showerror("Erreur", f"La salle {numero} n'existe pas.")
                return
            salle.affecter_film(film)
            messagebox.showinfo("Succès", f"Film '{titre}' affecté à la salle {numero}")
        except FilmInexistantError:
            messagebox.showerror("Erreur", f"Le film '{titre}' n'existe pas.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def creer_seance(self):
        titre = simpledialog.askstring("Créer Séance", "Titre du film:")
        try:
            numero = simpledialog.askinteger("Créer Séance", "Numéro de la salle:")
            if numero is None or numero <= 0:
                raise ValueError("Le numéro de salle doit être un entier strictement positif.")
        except Exception:
            messagebox.showerror("Erreur", "Entrée invalide pour le numéro de salle : un entier strictement positif est attendu.")
            return
        horaire = simpledialog.askstring("Créer Séance", "Horaire (ex: 2025-12-31 20:00):")
        try:
            film = self.gestion_films.get_film(titre)
            salle = self.gestion_salles.get_salle(numero)
            seance = self.gestion_seances.creer_seance(film, salle, horaire)
            messagebox.showinfo("Succès", f"Séance créée: {seance}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

def main():
    root = tk.Tk()
    app = CinemaApp(root)
    root.mainloop()

if __name__ == "__main__":
    try:
        print("Lancement de l'interface graphique...")
        main()
    except Exception as e:
        import traceback
        print("Erreur lors du lancement de l'interface graphique :")
        traceback.print_exc()
        input("Appuyez sur Entrée pour quitter...")