import os
from pickle import dumps, loads
from sys import getsizeof

# CONSTANTS --------------------------------------------
B = 3  # taille d'un bloc
U = 1  # maximum % d'enregistrement dans un bloc
TAILLE_SUPPRIME = 1
TAILLE_MATRICULE = 5
TAILLE_NOM = 25
TAILLE_PRENOM = 25
TAILLE_AFFILIATION = 25
TAILLE_ETUDIANT = TAILLE_SUPPRIME + TAILLE_MATRICULE + TAILLE_NOM + TAILLE_PRENOM + TAILLE_AFFILIATION

TAIILES = [TAILLE_SUPPRIME, TAILLE_MATRICULE, TAILLE_NOM, TAILLE_PRENOM, TAILLE_AFFILIATION]

ENREG = '#' * TAILLE_ETUDIANT

BLOC = [0, [ENREG] * B]
BLOC_SIZE = getsizeof(dumps(BLOC)) + len(ENREG) * (B - 1) + (B - 1)

# -------------------------------------------------------


def resize_chaine(chaine, taille_max):
    """ Completer une chaine avec des '#' """
    return chaine + '#' * (taille_max - len(chaine))


class BUFFER:  # buffer de memoire centrale
    def __init__(self, nb=0, tab=None):
        self.nb = nb
        self.tab = [ENREG] * B if tab is None else tab


def ecrire_dir(f, i, buff):
    adresse = 2 * getsizeof(dumps(0)) + i * BLOC_SIZE
    f.seek(adresse, 0)
    f.write(dumps([buff.nb, buff.tab]))


def lire_dir(f, i):
    adresse = 2 * getsizeof(dumps(0)) + i * BLOC_SIZE
    f.seek(adresse, 0)
    buff = f.read(BLOC_SIZE)
    buff_final = loads(buff)
    return BUFFER(nb=buff_final[0], tab=buff_final[1])


def entete(f, offset):
    adresse = offset * getsizeof(dumps(0))
    f.seek(adresse, 0)
    c = f.read(getsizeof(dumps(0)))
    return loads(c)


def affecter_entete(f, offset, c):
    adresse = offset * getsizeof(dumps(0))
    f.seek(adresse, 0)
    f.write(dumps(c))


def afficher_enreg(enreg):
    """ cette fonction affiche un enregistrement (enreg) """
    supprime, matricule, nom, prenom, affiliation = split_enreg(enreg)
    print(f"\tMatricule : {matricule}\n"
          f"\tNom : {nom}\n"
          f"\tPrenom : {prenom}\n"
          f"\tAffiliation : {affiliation}\n")


def split_enreg(enreg):
    """ cette fonction divise la chaîne (enreg) en chaînes
        séparées (champs) d'une maniere lisibile (sans '#') """
    champs = []
    inf, sup = 0, TAIILES[0]
    for k in range(1, len(TAIILES)):
        champs.append(enreg[inf:sup])
        inf = sup
        sup += TAIILES[k]
    champs.append(enreg[inf:len(enreg)])  # ajoute le dernier champ
    return list(map(lambda champ: champ.replace('#', ''), champs))


class TnOF:  # type de fichier T~OF
    def __init__(self, nom_fichier, b=B):
        self.nom_fichier = nom_fichier
        self.b = b

    def chargement_initial(self):
        n = 0
        i, j = 0, 0
        buff = BUFFER()

        try:
            f = open(self.nom_fichier, 'wb')
        except:
            print("\tImpossible d'ouvrir le fichier")
        else:
            ajouter_autre = 'o'
            while ajouter_autre == 'o':
                print(f"\n\t--- Etudiant {n + 1} :")

                supprime = '0'  # '0' <=> non supprime (logique), 1 sinon
                matricule = resize_chaine(input("\t=> Matricule : "), TAILLE_MATRICULE)
                nom = resize_chaine(input("\t=> Nom : ").strip(), TAILLE_NOM)
                prenom = resize_chaine(input("\t=> Prenom : ").strip(), TAILLE_PRENOM)
                affiliation = resize_chaine(input("\t=> Affiliation : ").strip(), TAILLE_AFFILIATION)
                etudiant = supprime + matricule + nom + prenom + affiliation

                if j < B * U:
                    buff.tab[j] = etudiant
                    buff.nb += 1
                    j += 1
                else:
                    ecrire_dir(f, i, buff)
                    buff.__init__()  # reinitialiser le buffer
                    buff.tab[0] = etudiant
                    buff.nb = 1
                    j = 1
                    i += 1

                n += 1
                ajouter_autre = input("\n\t=> Avez vous un autre etudiant a ajouter [O/N] : ").strip().lower()

            ecrire_dir(f, i, buff)
            affecter_entete(f, 0, n)  # entete 1 : nombre d'etudiants
            affecter_entete(f, 1, i + 1)  # entete 2 : nombre de blocs

            f.close()

    def afficher(self):
        def afficher_enreg(enreg):
            """ cette fonction affiche un enregistrement (enreg) """
            supprime, matricule, nom, prenom, affiliation = split_enreg(enreg)
            print(f"\tMatricule : {matricule}\n"
                  f"\tNom : {nom}\n"
                  f"\tPrenom : {prenom}\n"
                  f"\tAffiliation : {affiliation}\n")

        print("\n----- Affichage des etudiants -----\n")

        f = open(self.nom_fichier, "rb")
        nb_etudiants = entete(f, 0)
        nb_blocs = entete(f, 1)
        print("\t# Nombre de blocs : ", nb_blocs)
        print("\t# Nombre des etudiants : ", nb_etudiants)

        n = 1  # compteur
        for i in range(nb_blocs):
            buff = lire_dir(f, i)
            print("\n---------------------------------------")
            print(f"\t\tBLOC {i + 1}")
            print("---------------------------------------")
            for j in range(buff.nb):
                supprime_courant = split_enreg(buff.tab[j])[0]
                # afficher l'etudiant courant si il n'est pas logiquement supprime
                if supprime_courant == '0':
                    print(f"- Etudiant {n} :")
                    afficher_enreg(buff.tab[j])
                    n += 1
        f.close()

    def rechercher(self, matricule):
        """ Recherche d'un etudiant avec matricule
            retourner (trouve: boolean, (x: int, y: int)) """
        f = open(self.nom_fichier, 'rb')
        trouve = False
        x, y = 0, 0

        for i in range(entete(f, 1)):
            buff = lire_dir(f, i)
            for j in range(buff.nb):
                supprime_courant = split_enreg(buff.tab[j])[0]
                matricule_courant = split_enreg(buff.tab[j])[1]
                if supprime_courant != '1' and matricule == matricule_courant:
                    x, y = i, j
                    trouve = True
                    break
        f.close()
        return trouve, (x, y)

    def inserer(self, etudiant):
        """ Insertion d'un etudiant """
        matricule = split_enreg(etudiant)[1]
        trouve = self.rechercher(matricule)[0]
        if not trouve:
            f = open(self.nom_fichier, 'rb+')

            nb_blocs = entete(f, 1)
            buff = lire_dir(f, nb_blocs - 1)  # dernier bloc

            if buff.nb == B:  # si le dernier bloc est plein
                buff.__init__()  # nouveau bloc
                buff.nb = 1
                buff.tab[0] = etudiant
                ecrire_dir(f, nb_blocs, buff)
                affecter_entete(f, 1, nb_blocs + 1)  # mise a jour d'entete
            else:  # si le bloc n'est pas plein
                buff.tab[buff.nb] = etudiant
                buff.nb += 1
                ecrire_dir(f, nb_blocs - 1, buff)

            affecter_entete(f, 0, entete(f, 0) + 1)  # mise a jour d'entete
            f.close()
        else:
            print("\n\tUn etudiant avec ce matricule exist deja !\n")

    def supprimer(self, matricule):
        """ Suppression d'un etudiant avec le matricule (matricule)"""
        recherche_etudiant = self.rechercher(matricule)
        trouve = recherche_etudiant[0]
        i, j = recherche_etudiant[1]

        if not trouve:
            print("\n\tIl n'existe pas d'etudiant avec ce matricule !\n")
        else:
            f = open(self.nom_fichier, 'rb+')

            buff = lire_dir(f, i)
            etudiant_enreg = buff.tab[j]
            etudiant = split_enreg(etudiant_enreg)

            if etudiant[0] == '1':  # si l'etudiant est deja supprime
                print("\n\tCet etudiant est deja supprime (logiquement)\n")
            else:
                etudiant_enreg = '1' + etudiant_enreg[TAILLE_SUPPRIME:]
                buff.tab[j] = etudiant_enreg
                ecrire_dir(f, i, buff)
                affecter_entete(f, 0, entete(f, 0) - 1)  # m-a-j l'entete

            f.close()

    def apres_premiere_occurence(self, i, j):
        f = open(self.nom_fichier, 'rb+')

        buff = lire_dir(f, i)
        m = int(split_enreg(buff.tab[j])[1])
        print(f"Rechercher le matricule : {m}\n")

        for j2 in range(j+1, buff.nb):
            matricule = int(split_enreg(buff.tab[j2])[1])
            if m == matricule:
                print(i, j2)
                afficher_enreg(buff.tab[j2])

        for i2 in range(i+1, entete(f, 1)):
            buff = lire_dir(f, i2)
            for j2 in range(buff.nb):
                matricule = int(split_enreg(buff.tab[j2])[1])
                if m == matricule:
                    print(i2, j2)
                    afficher_enreg(buff.tab[j2])

        f.close()


def main():
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    def appuyez_sur_entrer():
        continuer = input("\n=> Appuyez sur ENTRER pour continuer\n")

    while True:
        clear()
        print("--------- Fichier T~OF ---------\n")
        print("\t[1]. Chargement initial")
        print("\t[2]. Affichage")
        print("\t[3]. Recherche")
        print("\t[4]. Insertion")
        print("\t[5]. Suppression")
        print("\t[6]. Premiere occurence")
        print("\n\t[q]. Quitter")

        choice = input("\n\t=> ").strip().lower()

        if choice == "1":
            clear()
            print("--------- Fichier T~OF / Chargement initial ---------\n")
            nom_fichier = input("\t=> Entrez le nom du fichier : ").strip()
            fichier = TnOF(nom_fichier=nom_fichier)
            fichier.chargement_initial()
            appuyez_sur_entrer()
        elif choice == "2":
            clear()
            print("--------- Fichier T~OF / Affichage ---------\n")
            nom_fichier = input("\t=> Entrez le nom du fichier : ").strip()
            if os.path.exists(nom_fichier):
                fichier = TnOF(nom_fichier=nom_fichier)
                fichier.afficher()
            else:
                print("\tCe fichier n'existe pas !")
            appuyez_sur_entrer()
        elif choice == "3":
            clear()
            print("--------- Fichier T~OF / Recherche ---------\n")
            nom_fichier = input("\t=> Entrez le nom du fichier : ").strip()
            if os.path.exists(nom_fichier):
                fichier = TnOF(nom_fichier=nom_fichier)

                matricule = input("\t=> Entrez le matricule a rechercher : ").strip()
                recherche_etudiant = fichier.rechercher(matricule)
                trouve = recherche_etudiant[0]
                i, j = recherche_etudiant[1]
                if trouve:
                    print("\n\t", f"L'etudiant se trouve dans le bloc {i}, enregistrement {j}")
                else:
                    print("\n\t", "Etudiant non trouve")
            else:
                print("\t Ce fichier n'existe pas !")
            appuyez_sur_entrer()
        elif choice == "4":
            clear()
            print("--------- Fichier T~OF / Insertion ---------\n")
            nom_fichier = input("\t=> Entrez le nom du fichier : ").strip()
            if os.path.exists(nom_fichier):
                fichier = TnOF(nom_fichier=nom_fichier)

                supprime = '0'
                matricule = resize_chaine(input("\t=> Matricule : "), TAILLE_MATRICULE)
                nom = resize_chaine(input("\t=> Nom : ").strip(), TAILLE_NOM)
                prenom = resize_chaine(input("\t=> Prenom : ").strip(), TAILLE_PRENOM)
                affiliation = resize_chaine(input("\t=> Affiliation : ").strip(), TAILLE_AFFILIATION)
                etudiant = supprime + matricule + nom + prenom + affiliation

                fichier.inserer(etudiant)
            else:
                print("\t Ce fichier n'existe pas !")
            appuyez_sur_entrer()
        elif choice == "5":
            clear()
            print("--------- Fichier T~OF / Suppression ---------\n")
            nom_fichier = input("\t=> Entrez le nom du fichier : ").strip()
            if os.path.exists(nom_fichier):
                fichier = TnOF(nom_fichier=nom_fichier)

                matricule = input("\t=> Entrez le matricule de l'etudiant a supprimer : ").strip()
                fichier.supprimer(matricule)
            else:
                print("\t Ce fichier n'existe pas !")
            appuyez_sur_entrer()
        elif choice == "6":
            clear()
            print("--------- Fichier T~OF / Premire occurence ---------\n")
            nom_fichier = input("\t=> Entrez le nom du fichier : ").strip()
            if os.path.exists(nom_fichier):
                fichier = TnOF(nom_fichier=nom_fichier)

                # matricule = input("\t=> Entrez le matricule de l'etudiant : ").strip()
                i = int(input("\t=> i = "))
                j = int(input("\t=> j = "))
                fichier.apres_premiere_occurence(i, j)
            else:
                print("\t Ce fichier n'existe pas !")
            appuyez_sur_entrer()
        elif choice == "q":
            break
        print()


main()
