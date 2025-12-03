import os
from colorama import Fore, Style, init

from film import films_par_defaut, Film
from salle import GestionSalles, Salle


# Initialisation de colorama
init(autoreset=True)

def effacer_console():
    os.system("cls" if os.name == "nt" else "clear")

def afficher_titre(titre):
    print(Fore.CYAN + Style.BRIGHT + f"\n=== {titre} ===\n" + Style.RESET_ALL)

def pause():
    input(Fore.LIGHTBLACK_EX + "\nAppuyez sur Entrée pour continuer..." + Style.RESET_ALL)

# ---------------------------------------------------------------------
#  MENUS GESTIONNAIRE
# ---------------------------------------------------------------------
def menu_gestionnaire(gestion_films, gestion_salles):
    while True:
        effacer_console()
        afficher_titre("🎬 Gestionnaire - Menu")
        print("1. Gérer les films")
        print("2. Gérer les salles")
        print("3. Affecter un film à une salle")
        print("4. Voir les films projetés")
        print("0. Retour au menu principal")

        choix = input("\nVotre choix : ")

        if choix == "1":
            menu_films(gestion_films)
        elif choix == "2":
            menu_salles(gestion_salles)
        elif choix == "3":
            affecter_film_a_salle(gestion_films, gestion_salles)
        elif choix == "4":
            afficher_films_proj(gestion_salles)
        elif choix == "0":
            break
        else:
            print(Fore.RED + "❌ Choix invalide.")
            pause()

# ---------------------------------------------------------------------
#  MENUS CLIENT
# ---------------------------------------------------------------------
def menu_client(gestion_films, gestion_salles):
    while True:
        effacer_console()
        afficher_titre("🎟️  Client - Menu")
        print("1. Voir les films à l'affiche")
        print("2. Réserver une place")
        print("0. Retour au menu principal")

        choix = input("\nVotre choix : ")

        if choix == "1":
            films = gestion_films.lister_films()
            if not films:
                print(Fore.YELLOW + "Aucun film à l'affiche pour le moment.")
            else:
                print(Fore.CYAN + "🎥 Films actuellement à l'affiche :")
                for f in films:
                    print(" -", f)
            pause()
        elif choix == "2":
            print(Fore.YELLOW + "🔧 La fonction de réservation sera ajoutée prochainement.")
            pause()
        elif choix == "0":
            break
        else:
            print(Fore.RED + "❌ Choix invalide.")
            pause()

# ---------------------------------------------------------------------
#  SOUS-MENUS DU GESTIONNAIRE
# ---------------------------------------------------------------------
def menu_films(gestion_films):
    while True:
        effacer_console()
        afficher_titre("🎞️ Gestion des films")
        print("1. Ajouter un film")
        print("2. Supprimer un film")
        print("3. Lister les films")
        print("0. Retour")
        choix = input("\nVotre choix : ")

        if choix == "1":
            titre = input("Titre : ")
            duree = int(input("Durée (min) : "))
            genre = input("Genre : ") or None
            try:
                gestion_films.ajouter_film(Film(titre, duree, genre))
                print(Fore.GREEN + "✅ Film ajouté avec succès.")
            except Exception as e:
                print(Fore.RED + f"Erreur : {e}")
            pause()
        elif choix == "2":
            titre = input("Titre du film à supprimer : ")
            try:
                gestion_films.supprimer_film(titre)
                print(Fore.GREEN + f"✅ Film '{titre}' supprimé.")
            except Exception as e:
                print(Fore.RED + f"Erreur : {e}")
            pause()
        elif choix == "3":
            films = gestion_films.lister_films()
            if not films:
                print(Fore.YELLOW + "Aucun film enregistré.")
            else:
                print(Fore.CYAN + "🎥 Liste des films :")
                for f in films:
                    print(" -", f)
            pause()
        elif choix == "0":
            break
        else:
            print(Fore.RED + "❌ Choix invalide.")
            pause()

def menu_salles(gestion_salles):
    while True:
        effacer_console()
        afficher_titre("🏛️ Gestion des salles")
        print("1. Ajouter une salle")
        print("2. Lister les salles")
        print("0. Retour")
        choix = input("\nVotre choix : ")

        if choix == "1":
            numero = int(input("Numéro de salle : "))
            capacite = int(input("Capacité : "))
            try:
                gestion_salles.ajouter_salle(Salle(numero, capacite))
                print(Fore.GREEN + "✅ Salle ajoutée avec succès.")
            except Exception as e:
                print(Fore.RED + f"Erreur : {e}")
            pause()
        elif choix == "2":
            salles = gestion_salles.lister_salles()
            if not salles:
                print(Fore.YELLOW + "Aucune salle enregistrée.")
            else:
                print(Fore.CYAN + "🏛️ Salles :")
                for s in salles:
                    print(" -", s)
            pause()
        elif choix == "0":
            break
        else:
            print(Fore.RED + "❌ Choix invalide.")
            pause()

def affecter_film_a_salle(gestion_films, gestion_salles):
    titre = input("Titre du film : ")
    numero = int(input("Numéro de la salle : "))
    try:
        film = gestion_films.get_film(titre)
        gestion_salles.affecter_film_a_salle(numero, film)
        print(Fore.GREEN + f"🎬 Film '{titre}' affecté à la salle {numero}.")
    except Exception as e:
        print(Fore.RED + f"Erreur : {e}")
    pause()

def afficher_films_proj(gestion_salles):
    salles = gestion_salles.lister_salles()
    if not salles:
        print(Fore.YELLOW + "Aucune salle enregistrée.")
    else:
        print(Fore.CYAN + "🎦 Salles et films projetés :")
        for s in salles:
            print(" -", s)
    pause()

# ---------------------------------------------------------------------
#  MENU PRINCIPAL (choix du rôle)
# ---------------------------------------------------------------------
def main():
    gestion_films = films_par_defaut
    gestion_salles = GestionSalles()

    while True:
        effacer_console()
        afficher_titre("🎬 Bienvenu dans votre cinéma !")
        print("1. 👤 Client")
        print("2. 🧑‍💼 Gestionnaire")
        print("0. Quitter")
        choix = input("\nVous êtes : ")

        if choix == "1":
            menu_client(gestion_films, gestion_salles)
        elif choix == "2":
            menu_gestionnaire(gestion_films, gestion_salles)
        elif choix == "0":
            effacer_console()
            print(Fore.GREEN + "👋 Merci d'avoir utilisé notre système !")
            break
        else:
            print(Fore.RED + "❌ Choix invalide.")
            pause()

if __name__ == "__main__":
    main()
