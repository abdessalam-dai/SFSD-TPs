from sys import getsizeof
from pickle import dumps, loads


b = 2  # taille d'un bloc
u = 1  # maximum 100% par bloc


def chargement_initial(nom_fichier):
    f = open(nom_fichier, "wb")
    i = 0
    j = 0
    buf = [0] * b

    n = int(input("=> Entrez le nombre des etudiants : "))
    for k in range(n):
        print()
        matricule = int(input("\tMatricule : "))
        nom = input("\tNom : ")
        prenom = input("\tPrenom : ")
        affiliation = input("\tAffiliation : ")

        etudiant = [matricule, nom, prenom, affiliation]

        if j < b * u:
            buf[j] = etudiant
            j += 1
        else:
            ecrire_dir(f, i, buf)
            buf = [0] * b
            buf[0] = etudiant
            i += 1
            j = 1
    ecrire_dir(f, i, buf)  # ecriture du dernier bloc

    aff_entete(f, 0, i+1)
    aff_entete(f, 1, n)

    f.close()


def aff_entete(f, ordre, c):
    adress = ordre * getsizeof(bytes(0))
    f.seek(adress, 0)
    f.write(dumps(c))


def entete(f, ordre):
    adress = ordre * getsizeof(bytes(0))
    f.seek(adress, 0)
    c = f.read(getsizeof(bytes(0)))

    return loads(c)


def ecrire_dir(f, i, buf):
    adress = 2 * getsizeof(bytes(0)) + i * getsizeof(buf)
    f.seek(adress, 0)
    f.write(dumps(buf))


def lire_dir(f, i):
    adress = 2 * getsizeof(bytes(0)) + i * getsizeof([0] * b)
    f.seek(adress, 0)
    buf = f.read(getsizeof([0] * b))

    return loads(buf)


def affichage(nom_fichier):
    print("\n--- Affichage des etudiants ---\n")
    f = open(nom_fichier, "rb")

    nb_blocs = entete(f, 0)
    nb_etudiants = entete(f, 1)
    print("\tNombre de blocs: ", nb_blocs)
    print("\tNombre d'etudiants: ", nb_etudiants)

    for i in range(nb_blocs):
        print("\n\t--- Bloc", i+1, " ---")
        etudiants = lire_dir(f, i)
        for etudiant in etudiants:
            print("\t", {
                'Matricule': etudiant[0],
                'Nom': etudiant[1],
                'Prenom': etudiant[2],
                'Affiliation': etudiant[3],
            } if etudiant != 0 else '[vide]')
        print("\t---------------")

    f.close()


chargement_initial(nom_fichier='etudiants.txt')
affichage(nom_fichier='etudiants.txt')
