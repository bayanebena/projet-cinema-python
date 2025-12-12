import tkinter as tk
from tkinter import messagebox, simpledialog
from film import GestionFilms, FilmInexistantError
from salle import GestionSalles, SalleInexistanteError
from reservation import GestionSeances, SallePleineError
import os
import urllib.request
import urllib.parse
import json
import mimetypes
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except Exception:
    HAS_PIL = False
from film import charger_films_csv
from salle import salles_par_defaut

# Palette "néon futuriste"
BG_COLOR = "#05080F"           # noir bleuté
NEON_VIOLET = "#A020F0"       # violet néon (titres)
ELECTRIC_BLUE = "#FFFFFF"     # blanc (remplace bleu électrique)
TEXT_LIGHT = "#E6F0FF"        # texte clair
SEANCE_COLOR = "#EF5C48"      # couleur pour les séances (laissé pour compatibilité)

# Polices (faute de police installée, tkinter utilisera un fallback)
TITLE_FONT = ("Orbitron", 24, "bold")
LARGE_TITLE_FONT = ("Orbitron", 48, "bold")
SUBTITLE_FONT = ("Roboto Condensed", 14)
BODY_FONT = ("Open Sans", 11)

# Boutons
BUTTON_BG = ELECTRIC_BLUE
BUTTON_FG = NEON_VIOLET
DEFAULT_OMDB_KEY = "bb3780f4"
DEFAULT_TMDB_KEY = "05567543c456f676f3852789a096ce75"

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
        # Appliquer style global
        self.apply_style()
        # tenter de récupérer et stocker localement les affiches pour les films existants
        try:
            for f in self.gestion_films.lister_films():
                try:
                    self._fetch_and_store_affiche(f)
                except Exception:
                    pass
        except Exception:
            pass
        self.menu_principal()

    def apply_style(self):
        self.bg_color = BG_COLOR
        self.accent_color = ELECTRIC_BLUE
        self.btn_color = BUTTON_BG
        self.seance_color = SEANCE_COLOR
        self.root.configure(bg=self.bg_color)
        # stockage des références d'images pour éviter le GC
        self._image_refs = {}

    def _fetch_affiche_online(self, titre: str):
        """Tente de récupérer l'URL d'affiche depuis OMDb (si clé OMDB_API_KEY) ou TMDb (TMDB_API_KEY)."""
        omdb_key = os.environ.get('OMDB_API_KEY') or DEFAULT_OMDB_KEY
        tmdb_key = os.environ.get('TMDB_API_KEY') or DEFAULT_TMDB_KEY
        title_q = urllib.parse.quote_plus(titre)
        # OMDb
        if omdb_key:
            try:
                url = f"http://www.omdbapi.com/?t={title_q}&apikey={omdb_key}"
                with urllib.request.urlopen(url, timeout=10) as resp:
                    data = json.load(resp)
                poster = data.get('Poster')
                if poster and poster != 'N/A':
                    return poster
            except Exception:
                pass
        # TMDb
        if tmdb_key:
            try:
                url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_key}&query={title_q}"
                with urllib.request.urlopen(url, timeout=10) as resp:
                    data = json.load(resp)
                results = data.get('results', [])
                if results:
                    poster_path = results[0].get('poster_path')
                    if poster_path:
                        return f"https://image.tmdb.org/t/p/w500{poster_path}"
            except Exception:
                pass
        return None

    def _download_image(self, url: str, dest_path: str):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
                # essayer déterminer extension
                content_type = resp.headers.get('Content-Type')
                ext = None
                if content_type:
                    ext = mimetypes.guess_extension(content_type.split(';')[0].strip())
                if not ext:
                    parsed = urllib.parse.urlparse(url)
                    root, e = os.path.splitext(parsed.path)
                    ext = e or '.jpg'
                if not dest_path.lower().endswith(ext):
                    dest_path = dest_path + ext
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                with open(dest_path, 'wb') as f:
                    f.write(data)
                return dest_path
        except Exception:
            return None

    def _fetch_and_store_affiche(self, film):
        # Si affiche déjà trouvée localement, garder
        existing = self._find_affiche_path(film)
        if existing:
            film.affiche = existing
            return existing
        # tenter récupération en ligne
        url = self._fetch_affiche_online(film.titre)
        if not url:
            return None
        # définir chemin local de sauvegarde
        base_dir = os.path.dirname(__file__)
        posters_dir = os.path.join(base_dir, 'posters')
        safe_name = ''.join(c if c.isalnum() else '_' for c in film.titre)
        dest_base = os.path.join(posters_dir, safe_name)
        saved = self._download_image(url, dest_base)
        if saved:
            film.affiche = saved
            return saved
        return None

    def _find_affiche_path(self, film):
        # Priorité: chemin explicite dans l'objet film
        base_dir = os.path.dirname(__file__)
        candidates = []
        if getattr(film, 'affiche', None):
            candidates.append(os.path.join(base_dir, film.affiche))
            candidates.append(film.affiche)
        # chercher dans dossier posters par titre (espaces remplacés)
        safe_name = ''.join(c if c.isalnum() else '_' for c in film.titre)
        posters_dir = os.path.join(base_dir, 'posters')
        exts = ['.png', '.jpg', '.jpeg', '.gif']
        for ext in exts:
            candidates.append(os.path.join(posters_dir, f"{safe_name}{ext}"))
            candidates.append(os.path.join(posters_dir, f"{film.titre}{ext}"))
            candidates.append(os.path.join(base_dir, f"{safe_name}{ext}"))
            candidates.append(os.path.join(base_dir, f"{film.titre}{ext}"))
        for p in candidates:
            if p and os.path.exists(p):
                return p
        return None
        
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
        header = tk.Label(self.root, text="FABULOUS", font=TITLE_FONT, bg=self.bg_color, fg=NEON_VIOLET)
        header.pack(pady=(10,2))
        tk.Label(self.root, text="Bienvenue au Cinéma!", font=SUBTITLE_FONT, bg=self.bg_color, fg=TEXT_LIGHT).pack(pady=4)
        tk.Button(self.root, text="Client", width=20, command=self.menu_client, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=5)
        tk.Button(self.root, text="Gestionnaire", width=20, command=self.menu_gestionnaire, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=5)
        tk.Button(self.root, text="Quitter", width=20, command=self.root.quit, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=5)

    def menu_client(self):
        # Affiche la page de garde du client puis le menu client
        self.page_garde_client()

    def page_garde_client(self):
        self.clear()
        frame = tk.Frame(self.root, bg=self.bg_color)
        frame.pack(expand=True, fill='both')
        tk.Label(frame, text="Bienvenue au", font=TITLE_FONT, bg=self.bg_color, fg=NEON_VIOLET).pack(pady=(80,0))
        tk.Label(frame, text="FABULOUS", font=LARGE_TITLE_FONT, bg=self.bg_color, fg=NEON_VIOLET).pack(pady=(10,40))
        tk.Button(frame, text="Entrer", width=30, command=self.menu_client_options, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=10)

    def menu_client_options(self):
        self.clear()
        tk.Label(self.root, text="Menu Client", font=SUBTITLE_FONT, bg=self.bg_color, fg=TEXT_LIGHT).pack(pady=10)
        tk.Button(self.root, text="Mes réservations", width=30, command=self.menu_client_reservations, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=5)
        tk.Button(self.root, text="Voir les films à l'affiche", width=30, command=self.afficher_films, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=5)
        tk.Button(self.root, text="Voir les séances", width=30, command=self.afficher_seances, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=5)
        tk.Button(self.root, text="Retour", width=30, command=self.menu_principal, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=5)

    def menu_gestionnaire(self):
        # Affiche le menu gestionnaire
        self.clear()
        tk.Label(self.root, text="Menu Gestionnaire", font=SUBTITLE_FONT, bg=self.bg_color, fg=TEXT_LIGHT).pack(pady=10)
        tk.Button(self.root, text="Ajouter un film", width=30, command=self.ajouter_film, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=5)
        tk.Button(self.root, text="Supprimer un film", width=30, command=self.supprimer_film, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=5)
        tk.Button(self.root, text="Ajouter une salle", width=30, command=self.ajouter_salle, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=5)
        tk.Button(self.root, text="Supprimer une salle", width=30, command=self.supprimer_salle, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=5)
        tk.Button(self.root, text="Affecter un film à une salle", width=30, command=self.affecter_film_salle, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=5)
        tk.Button(self.root, text="Créer une séance", width=30, command=self.creer_seance, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=5)
        tk.Button(self.root, text="Retour", width=30, command=self.menu_principal, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=5)

    def clear(self):
        # Efface tous les widgets de la fenêtre
        for widget in self.root.winfo_children():
            widget.destroy()

    def afficher_films(self):
        # Affiche la liste des films à l'affiche
        self.clear()
        tk.Label(self.root, text="Films à l'affiche", font=SUBTITLE_FONT, bg=self.bg_color, fg=TEXT_LIGHT).pack(pady=10)
        films = self.gestion_films.lister_films()
        if not films:
            tk.Label(self.root, text="Aucun film à l'affiche.", bg=self.bg_color, fg=TEXT_LIGHT, font=BODY_FONT).pack()
            tk.Button(self.root, text="Retour", command=self.menu_client_options, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=10)
            return

        # zone de défilement contenant une grille centrée (4 colonnes)
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(fill='both', expand=True)
        canvas = tk.Canvas(container, bg=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        canvas.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        # wrapper placé dans le canvas; sa largeur sera ajustée pour correspondre au canvas
        wrapper = tk.Frame(canvas, bg=self.bg_color)
        window_id = canvas.create_window((0, 0), window=wrapper, anchor='nw')

        def _on_canvas_config(e):
            canvas.itemconfig(window_id, width=e.width)
        canvas.bind('<Configure>', _on_canvas_config)
        wrapper.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        # Activer le défilement avec la molette / pavé tactile lorsque le curseur
        # survole la zone d'affichage des films. Utilise <MouseWheel> (Windows/Mac)
        # et <Button-4/5> (Linux) comme fallback.
        def _on_mousewheel(event):
            try:
                # X11: Button-4 (up) / Button-5 (down)
                if hasattr(event, 'num') and event.num in (4, 5):
                    delta = -1 if event.num == 4 else 1
                    canvas.yview_scroll(delta, 'units')
                else:
                    # Windows / Mac
                    delta = int(-1 * (event.delta / 120))
                    canvas.yview_scroll(delta, 'units')
            except Exception:
                pass

        def _bind_scroll(_):
            canvas.bind_all('<MouseWheel>', _on_mousewheel)
            canvas.bind_all('<Button-4>', _on_mousewheel)
            canvas.bind_all('<Button-5>', _on_mousewheel)

        def _unbind_scroll(_):
            try:
                canvas.unbind_all('<MouseWheel>')
                canvas.unbind_all('<Button-4>')
                canvas.unbind_all('<Button-5>')
            except Exception:
                pass

        wrapper.bind('<Enter>', _bind_scroll)
        wrapper.bind('<Leave>', _unbind_scroll)

        list_frame = tk.Frame(wrapper, bg=self.bg_color)
        list_frame.pack(anchor='center', pady=10)

        cols = 4
        for idx, f in enumerate(films):
            row = idx // cols
            col = idx % cols
            item = tk.Frame(list_frame, bg=self.bg_color, padx=8, pady=8, relief='flat', bd=0)
            item.grid(row=row, column=col, padx=12, pady=12)
            img_path = self._find_affiche_path(f)
            if img_path:
                try:
                    if HAS_PIL:
                        img = Image.open(img_path)
                        img.thumbnail((160, 240))
                        photo = ImageTk.PhotoImage(img)
                    else:
                        photo = tk.PhotoImage(file=img_path)
                    lbl_img = tk.Label(item, image=photo, bg=self.bg_color)
                    lbl_img.image = photo
                    self._image_refs[f.titre] = photo
                    lbl_img.pack(anchor='center')
                except Exception:
                    tk.Label(item, text="[Affiche non chargée]", bg=self.bg_color, fg=TEXT_LIGHT, font=BODY_FONT).pack()
            else:
                placeholder = tk.Label(item, text="Pas d'affiche", width=20, height=12, bg=self.bg_color, fg=TEXT_LIGHT, relief='ridge')
                placeholder.pack(anchor='center')
            tk.Label(item, text=f.titre, bg=self.bg_color, fg=NEON_VIOLET, wraplength=160, justify='center', font=("Orbitron", 11, "bold")).pack(pady=(6,0), anchor='center')
            if getattr(f, 'genre', None):
                tk.Label(item, text=f.genre, bg=self.bg_color, fg=TEXT_LIGHT, font=BODY_FONT).pack(anchor='center')
            tk.Button(item, text="Voir séances", command=lambda film=f: self.afficher_seances(film), bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=6)

        # for nicer layout, ensure even columns
        for c in range(cols):
            list_frame.grid_columnconfigure(c, weight=1)

        tk.Button(self.root, text="Retour", command=self.menu_client_options, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=10)

    def menu_client_reservations(self):
        # Affiche les réservations d'un client (demande le nom)
        self.clear()
        tk.Label(self.root, text="Mes réservations", font=SUBTITLE_FONT, bg=self.bg_color, fg=TEXT_LIGHT).pack(pady=10)
        client_nom = simpledialog.askstring("Mes réservations", "Votre nom :")
        if not client_nom:
            tk.Button(self.root, text="Retour", command=self.menu_client_options, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=10)
            return

        # Collecter toutes les réservations pour ce client
        seances = self.gestion_seances.lister_seances()
        client_res = []  # list of tuples (seance, [places])
        for s in seances:
            seats = [r.place for r in s.lister_reservations() if r.client_nom == client_nom]
            if seats:
                client_res.append((s, seats))

        if not client_res:
            tk.Label(self.root, text="Aucune séance n'est réservée.", bg=self.bg_color, fg=TEXT_LIGHT, font=BODY_FONT).pack(pady=8)
            tk.Button(self.root, text="Retour", command=self.menu_client_options, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=10)
            return

        # zone scrollable
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(fill='both', expand=True)
        canvas = tk.Canvas(container, bg=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        canvas.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        wrapper = tk.Frame(canvas, bg=self.bg_color)
        win = canvas.create_window((0, 0), window=wrapper, anchor='nw')
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(win, width=e.width))
        wrapper.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

        for (s, seats) in client_res:
            item = tk.Frame(wrapper, bg=self.bg_color, bd=1, relief='solid', padx=8, pady=8)
            item.pack(fill='x', padx=12, pady=8)
            # Afficher nom, film, horaire, sièges
            tk.Label(item, text=f"Nom: {client_nom}", bg=self.bg_color, fg=TEXT_LIGHT, font=BODY_FONT).grid(row=0, column=0, sticky='w')
            tk.Label(item, text=f"Film: {s.film.titre}", bg=self.bg_color, fg=NEON_VIOLET, font=SUBTITLE_FONT).grid(row=1, column=0, sticky='w', pady=(4,0))
            tk.Label(item, text=f"Horaire: {s.horaire}", bg=self.bg_color, fg=TEXT_LIGHT, font=BODY_FONT).grid(row=2, column=0, sticky='w')
            tk.Label(item, text=f"Sièges: {', '.join(seats)}", bg=self.bg_color, fg=TEXT_LIGHT, font=BODY_FONT).grid(row=3, column=0, sticky='w', pady=(4,0))

            def _del_cb(seance=s, seats_list=seats, client=client_nom):
                if messagebox.askyesno("Confirmation", "Voulez-vous supprimer cette réservation ?"):
                    removed_any = False
                    for p in list(seats_list):
                        try:
                            ok = seance.annuler_reservation(client, p)
                            if ok:
                                removed_any = True
                        except Exception:
                            pass
                    if removed_any:
                        messagebox.showinfo("Succès", "Réservation supprimée.")
                    else:
                        messagebox.showerror("Erreur", "Impossible de supprimer la réservation.")
                    # rafraîchir la vue
                    self.menu_client_reservations()

            btn_del = tk.Button(item, text="🗑️", command=_del_cb, bg=self.bg_color, fg=NEON_VIOLET)
            btn_del.grid(row=0, column=1, rowspan=4, sticky='e', padx=8)

        tk.Button(self.root, text="Retour", command=self.menu_client_options, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=10)

    def afficher_seances(self, film=None):
        # Affiche la liste des séances disponibles ; si `film` est fourni, on n'affiche
        # que les séances pour ce film.
        self.clear()
        title_text = f"Séances - {film.titre}" if film else "Séances"
        tk.Label(self.root, text=title_text, font=SUBTITLE_FONT, bg=self.bg_color, fg=TEXT_LIGHT).pack(pady=10)
        # On ne garde que les séances dont le film existe encore
        films_existants = set(f.titre for f in self.gestion_films.lister_films())
        all_seances = [s for s in self.gestion_seances.lister_seances() if s.film.titre in films_existants]

        if film:
            seances = [s for s in all_seances if s.film.titre == film.titre]
        else:
            seances = all_seances

        if not seances:
            if film:
                tk.Label(self.root, text="Aucune séance enregistrée pour ce film.", bg=self.bg_color, fg=TEXT_LIGHT, font=BODY_FONT).pack()
            else:
                tk.Label(self.root, text="Aucune séance disponible.", bg=self.bg_color, fg=TEXT_LIGHT, font=BODY_FONT).pack()
        else:
            if film:
                tk.Label(self.root, text=f"Séances pour {film.titre} :", font=BODY_FONT, bg=self.bg_color, fg=TEXT_LIGHT).pack(pady=5)
            else:
                tk.Label(self.root, text="Cliquez sur une séance pour voir le plan de salle et réserver :", font=BODY_FONT, bg=self.bg_color, fg=TEXT_LIGHT).pack(pady=5)
            for s in seances:
                tk.Button(self.root, text=str(s), wraplength=400, command=lambda seance=s: self.afficher_plan_salle(seance), bg=BUTTON_BG, fg=BUTTON_FG, font=BODY_FONT).pack(pady=2, fill='x')
        tk.Button(self.root, text="Retour", command=self.menu_client_options, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=10)

    def afficher_plan_salle(self, seance):
        # Affiche le plan de la salle pour une séance donnée, avec code couleur
        self.clear()
        tk.Label(self.root, text=f"Plan de la salle {seance.salle.numero} - {seance.film.titre}", font=SUBTITLE_FONT, bg=self.bg_color, fg=NEON_VIOLET).pack(pady=5)
        tk.Label(self.root, text=f"Horaire : {seance.horaire}", font=BODY_FONT, bg=self.bg_color, fg=TEXT_LIGHT).pack(pady=2)
        plan = seance.plan
        frame = tk.Frame(self.root, bg=self.bg_color)
        frame.pack(pady=10)
        colonnes = max(len(row) for row in plan) if plan else 0
        # Affichage de la numérotation des colonnes en haut
        for j in range(colonnes):
            tk.Label(frame, text=str(j+1), width=4, height=2, font=SUBTITLE_FONT, bg=self.bg_color, fg=NEON_VIOLET).grid(row=0, column=j+1)
        # Affichage du plan avec lettres à gauche
        for i, row in enumerate(plan):
            # Lettre de la rangée à gauche
            tk.Label(frame, text=chr(65+i), width=4, height=2, font=SUBTITLE_FONT, bg=self.bg_color, fg=NEON_VIOLET).grid(row=i+1, column=0)
            for j, place in enumerate(row):
                couleur = "green" if seance.est_place_disponible(place) else "red"
                etat = tk.NORMAL if seance.est_place_disponible(place) else tk.DISABLED
                btn = tk.Button(frame, text="", width=4, height=2, bg=couleur, fg=TEXT_LIGHT, state=etat,
                                command=lambda p=place: self.reserver_place_graphique(seance, p))
                btn.grid(row=i+1, column=j+1, padx=2, pady=2)
        # Ajout de la légende du code couleur
        legend_frame = tk.Frame(self.root, bg=self.bg_color)
        legend_frame.pack(pady=5)
        tk.Label(legend_frame, text=" ", width=2, height=1, bg="green").pack(side=tk.LEFT, padx=2)
        tk.Label(legend_frame, text=": disponible", font=BODY_FONT, bg=self.bg_color, fg=TEXT_LIGHT).pack(side=tk.LEFT)
        tk.Label(legend_frame, text=" ", width=2, height=1, bg="red").pack(side=tk.LEFT, padx=10)
        tk.Label(legend_frame, text=": réservée", font=BODY_FONT, bg=self.bg_color, fg=TEXT_LIGHT).pack(side=tk.LEFT)
        tk.Button(self.root, text="Retour", command=self.afficher_seances, bg=BUTTON_BG, fg=BUTTON_FG, font=SUBTITLE_FONT).pack(pady=10)

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
            # tenter de récupérer une affiche en ligne et la stocker localement
            try:
                self._fetch_and_store_affiche(film)
            except Exception:
                pass
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