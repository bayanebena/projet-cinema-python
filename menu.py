from film import Film, GestionFilms
from salle import Salle, GestionSalles


def afficher_menu():
    print("\n===== MENU : GESTION DU CINÉMA (Personne 1) =====")
    print("1 - Ajouter un film")
    print("2 - Ajouter une salle")
    print("3 - Lister les films")
    print("4 - Lister les salles")
    print("5 - Affecter un film à une salle")
    print("6 - Afficher salles + films projetés")
    print("0 - Quitter")


def main():
    gestion_films = GestionFilms()
    gestion_salles = GestionSalles()

    while True:
        afficher_menu()
        choix = input("Votre choix : ").strip()

        try:
            # Ajouter un film
            if choix == "1":
                titre = input("Titre du film : ")
                duree = int(input("Durée en minutes : "))
                genre = input("Genre (optionnel) : ") or None

                film = Film(titre, duree, genre)
                gestion_films.ajouter_film(film)
                print("Film ajouté avec succès.")

            # Ajouter une salle
            elif choix == "2":
                numero = int(input("Numéro de la salle : "))
                capacite = int(input("Capacité de la salle : "))
                salle = Salle(numero, capacite)

                gestion_salles.ajouter_salle(salle)
                print("Salle ajoutée avec succès.")

            # Lister les films
            elif choix == "3":
                films = gestion_films.lister_films()
                if not films:
                    print("Aucun film enregistré.")
                else:
                    print("\nListe des films :")
                    for f in films:
                        print(" -", f)

            # Lister les salles
            elif choix == "4":
                salles = gestion_salles.lister_salles()
                if not salles:
                    print("Aucune salle enregistrée.")
                else:
                    print("\nListe des salles :")
                    for s in salles:
                        print(" -", s)

            # Affecter film → salle
            elif choix == "5":
                titre = input("Titre du film : ")
                numero_salle = int(input("Numéro de la salle : "))

                film = gestion_films.get_film(titre)
                gestion_salles.affecter_film_a_salle(numero_salle, film)

                print(f"Le film '{titre}' a été affecté à la salle {numero_salle}.")

            # Afficher salles + film projeté
            elif choix == "6":
                salles = gestion_salles.lister_salles()
                if not salles:
                    print("Aucune salle enregistrée.")
                else:
                    print("\nSalles et films projetés :")
                    for s in salles:
                        print(" -", s)

            # Quitter
            elif choix == "0":
                print("Fin du programme.")
                break

            else:
                print("Choix invalide. Merci de réessayer.")

        except Exception as e:
            print(f"Erreur : {e}")


if __name__ == "__main__":
    main()
