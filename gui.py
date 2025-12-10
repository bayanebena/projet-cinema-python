import tkinter as tk
from tkinter import messagebox, simpledialog
from film import GestionFilms, FilmInexistantError
from salle import GestionSalles, SalleInexistanteError
from reservation import GestionSeances, SallePleineError
import os
from film import charger_films_csv
from salle import salles_par_defaut

class CinemaApp:
    def __init__(self, root):
        # Initialise l'application graphique et les gestionnaires de films, salles, séances
        self.root = root
        self.root.title("Cinéma - Application Graphique")
        chemin_csv = os.path.join(os.path.dirname(__file__), "films_init.csv")
        self.gestion_films = charger_films_csv(chemin_csv)
        self.gestion_salles = salles_par_defaut()
        self.gestion_seances = GestionSeances()
        self.creer_seances_par_defaut()
        self.menu_principal()

    def creer_seances_par_defaut(self):
        # Crée 5 séances par défaut au lancement
        films = self.gestion_films.lister_films()
        salles = self.gestion_salles.lister_salles()
        horaires = [
            "2025-12-10 18:00",
            "2025-12-10 20:00",
            "2025-12-11 18:00",
            "2025-12-11 20:00",
            "2025-12-12 21:00"
        ]
        for i in range(min(5, len(films), len(salles))):
            try:
                self.gestion_seances.creer_seance(films[i], salles[i], horaires[i])
            except Exception:
                pass

    def menu_principal(self):
        # Affiche le menu principal (choix client/gestionnaire)
        self.clear()
        tk.Label(self.root, text="Bienvenue au Cinéma!", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Client", width=20, command=self.menu_client).pack(pady=5)
        tk.Button(self.root, text="Gestionnaire", width=20, command=self.menu_gestionnaire).pack(pady=5)
        tk.Button(self.root, text="Quitter", width=20, command=self.root.quit).pack(pady=5)

    def menu_client(self):
        # Affiche le menu client
        self.clear()
        tk.Label(self.root, text="Menu Client", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="Voir les films à l'affiche", width=30, command=self.afficher_films).pack(pady=5)
        tk.Button(self.root, text="Voir les séances", width=30, command=self.afficher_seances).pack(pady=5)
        tk.Button(self.root, text="Retour", width=30, command=self.menu_principal).pack(pady=5)

    def menu_gestionnaire(self):
        # Affiche le menu gestionnaire
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
        # Efface tous les widgets de la fenêtre
        for widget in self.root.winfo_children():
            widget.destroy()

    def afficher_films(self):
        # Affiche la liste des films à l'affiche
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
        # Affiche la liste des séances disponibles (films existants uniquement)
        self.clear()
        tk.Label(self.root, text="Séances", font=("Arial", 14)).pack(pady=10)
        # On ne garde que les séances dont le film existe encore
        films_existants = set(f.titre for f in self.gestion_films.lister_films())
        seances = [s for s in self.gestion_seances.lister_seances() if s.film.titre in films_existants]
        if not seances:
            tk.Label(self.root, text="Aucune séance disponible.").pack()
        else:
            tk.Label(self.root, text="Cliquez sur une séance pour voir le plan de salle et réserver :", font=("Arial", 10)).pack(pady=5)
            for s in seances:
                tk.Button(self.root, text=str(s), wraplength=400, command=lambda seance=s: self.afficher_plan_salle(seance)).pack(pady=2, fill='x')
        tk.Button(self.root, text="Retour", command=self.menu_client).pack(pady=10)

    def afficher_plan_salle(self, seance):
        # Affiche le plan de la salle pour une séance donnée, avec code couleur
        self.clear()
        tk.Label(self.root, text=f"Plan de la salle {seance.salle.numero} - {seance.film.titre}", font=("Arial", 13)).pack(pady=5)
        tk.Label(self.root, text=f"Horaire : {seance.horaire}", font=("Arial", 10)).pack(pady=2)
        plan = seance.plan
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        colonnes = max(len(row) for row in plan) if plan else 0
        # Affichage de la numérotation des colonnes en haut
        for j in range(colonnes):
            tk.Label(frame, text=str(j+1), width=4, height=2, font=("Arial", 9, "bold")).grid(row=0, column=j+1)
        # Affichage du plan avec lettres à gauche
        for i, row in enumerate(plan):
            # Lettre de la rangée à gauche
            tk.Label(frame, text=chr(65+i), width=4, height=2, font=("Arial", 9, "bold")).grid(row=i+1, column=0)
            for j, place in enumerate(row):
                couleur = "green" if seance.est_place_disponible(place) else "red"
                etat = tk.NORMAL if seance.est_place_disponible(place) else tk.DISABLED
                btn = tk.Button(frame, text="", width=4, height=2, bg=couleur, fg="white", state=etat,
                                command=lambda p=place: self.reserver_place_graphique(seance, p))
                btn.grid(row=i+1, column=j+1, padx=2, pady=2)
        # Ajout de la légende du code couleur
        legend_frame = tk.Frame(self.root)
        legend_frame.pack(pady=5)
        tk.Label(legend_frame, text="", width=2, height=1, bg="green").pack(side=tk.LEFT, padx=2)
        tk.Label(legend_frame, text=": disponible", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Label(legend_frame, text="", width=2, height=1, bg="red").pack(side=tk.LEFT, padx=10)
        tk.Label(legend_frame, text=": réservée", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Button(self.root, text="Retour", command=self.afficher_seances).pack(pady=10)

    def reserver_place_graphique(self, seance, place):
        # Permet au client de réserver une place précise dans le plan de salle
        confirm = messagebox.askyesno("Confirmation", f"Voulez-vous réserver la place {place} ?")
        if not confirm:
            return
        client_nom = simpledialog.askstring("Réservation", f"Votre nom pour la place {place} :")
        if not client_nom:
            messagebox.showerror("Erreur", "Le nom ne peut pas être vide.")
            return
        try:
            reservation = seance.reserver(client_nom, place)
            messagebox.showinfo("Succès", f"Réservation confirmée : {reservation}")
            self.afficher_plan_salle(seance)
        except SallePleineError as e:
            messagebox.showerror("Erreur", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def reserver_depuis_seance(self, seance):
        client_nom = simpledialog.askstring("Réservation", "Votre nom:")
        try:
            nb_places = simpledialog.askinteger("Réservation", "Nombre de places:")
            if nb_places is None or nb_places <= 0:
                raise ValueError("Le nombre de places doit être un entier strictement positif.")
        except Exception:
            messagebox.showerror("Erreur", "Entrée invalide pour le nombre de places : un entier strictement positif est attendu.")
            return
        try:
            reservation = seance.reserver(client_nom, nb_places)
            messagebox.showinfo("Succès", f"Réservation confirmée: {reservation}")
        except SallePleineError as e:
            messagebox.showerror("Erreur", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

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
        # Ajoute un film via une boîte de dialogue
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
        # Supprime un film après affichage de la liste
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
        # Supprime une salle après affichage de la liste
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
        # Affecte un film à une salle après affichage des listes
        films = self.gestion_films.lister_films()
        salles = self.gestion_salles.lister_salles()
        if not films:
            messagebox.showinfo("Info", "Aucun film disponible à affecter.")
            return
        if not salles:
            messagebox.showinfo("Info", "Aucune salle disponible pour l'affectation.")
            return
        films_str = "\n".join(str(f) for f in films)
        salles_str = "\n".join(str(s) for s in salles)
        messagebox.showinfo("Films existants", f"Films enregistrés :\n{films_str}")
        messagebox.showinfo("Salles existantes", f"Salles enregistrées :\n{salles_str}")
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
        # Crée une séance après affichage des films et salles
        films = self.gestion_films.lister_films()
        salles = self.gestion_salles.lister_salles()
        if not films:
            messagebox.showinfo("Info", "Aucun film disponible pour créer une séance.")
            return
        if not salles:
            messagebox.showinfo("Info", "Aucune salle disponible pour créer une séance.")
            return
        films_str = "\n".join(str(f) for f in films)
        salles_str = "\n".join(str(s) for s in salles)
        messagebox.showinfo("Films existants", f"Films enregistrés :\n{films_str}")
        messagebox.showinfo("Salles existantes", f"Salles enregistrées :\n{salles_str}")
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
    # Lance l'application graphique avec une fenêtre élargie
    root = tk.Tk()
    root.geometry("1200x700")  # Largeur x Hauteur
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