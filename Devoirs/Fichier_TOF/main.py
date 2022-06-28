import operator
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


def entete(f, offset):
    adresse = offset * getsizeof(dumps(0))
    f.seek(adresse, 0)
    c = f.read(getsizeof(dumps(0)))
    return loads(c)


def affecter_entete(f, offset, c):
    adresse = offset * getsizeof(dumps(0))
    f.seek(adresse, 0)
    f.write(dumps(c))


def lire_dir(f, i):
    adresse = 2 * getsizeof(dumps(0)) + i * BLOC_SIZE
    f.seek(adresse, 0)
    buff = f.read(BLOC_SIZE)
    buff_final = loads(buff)
    return BUFFER(nb=buff_final[0], tab=buff_final[1])


def ecrire_dir(f, i, buff):
    adresse = 2 * getsizeof(dumps(0)) + i * BLOC_SIZE
    f.seek(adresse, 0)
    f.write(dumps([buff.nb, buff.tab]))


def afficher_enreg(enreg, db=''):
    """ cette fonction affiche un enregistrement (enreg) """
    supprime, matricule, nom, prenom, affiliation = split_enreg(enreg)
    supprime = bool(int(supprime))
    print(f"{db}| Cle : {matricule}\t| "
          f"Efface :  {'Oui' if supprime else 'Non'}\t\t|")
    print(f"{db}-----------------------------------------")


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


class TOF:  # type de fichier T~OF
    def __init__(self, nom_fichier, b=B):
        self.nom_fichier = nom_fichier
        self.b = b

    def chargement_initial(self):
        n = 0
        i, j = 0, 0
        buff = BUFFER()
        etudiants_dict = {}

        try:
            f = open(self.nom_fichier, 'wb')
        except:
            print("\tImpossible d'ouvrir le fichier")
        else:
            ajouter_autre = 'o'
            while ajouter_autre == 'o':
                print(f"\n\t--- Etudiant {n + 1} :")

                supprime = '0'  # '0' <=> non supprime (logique), 1 sinon
                matricule_original = input("\t=> Matricule : ")
                matricule = resize_chaine(matricule_original, TAILLE_MATRICULE)
                nom = resize_chaine(input("\t=> Nom : ").strip(), TAILLE_NOM)
                prenom = resize_chaine(input("\t=> Prenom : ").strip(), TAILLE_PRENOM)
                affiliation = resize_chaine(input("\t=> Affiliation : ").strip(), TAILLE_AFFILIATION)
                etudiant = supprime + matricule + nom + prenom + affiliation

                etudiants_dict[int(matricule_original)] = etudiant

                n += 1
                ajouter_autre = input("\n\t=> Avez vous un autre etudiant a ajouter [O/N] : ").strip().lower()

            # ordoner le tableau d'etudiants
            etudiants_ordonee = sorted(etudiants_dict.items(), key=operator.itemgetter(1))
            etudiants = [e[1] for e in etudiants_ordonee]

            for k in range(n):
                etudiant = etudiants[k]
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

            ecrire_dir(f, i, buff)
            affecter_entete(f, 0, n)  # entete 1 : nombre d'etudiants
            affecter_entete(f, 1, i + 1)  # entete 2 : nombre de blocs

            f.close()

    def afficher(self):
        print("\n----- Affichage des etudiants -----\n")

        f = open(self.nom_fichier, "rb")
        nb_etudiants = entete(f, 0)
        nb_blocs = entete(f, 1)
        print("\t# Nombre de blocs : ", nb_blocs)
        print("\t# Nombre des etudiants : ", nb_etudiants)

        for i in range(nb_blocs):
            buff = lire_dir(f, i)
            print("\n-----------------------------------------")
            print(f"| BLOC {i}\t| NB: {buff.nb}\t\t\t|")
            print("-----------------------------------------")
            for j in range(buff.nb):
                afficher_enreg(buff.tab[j])
        f.close()

    def rechercher(self, matricule):
        """ Recherche d'un etudiant avec matricule
            retourner (trouve: boolean, (x: int, y: int)) """
        f = open(self.nom_fichier, 'rb')

        bloc_inf, bloc_sup = 0, entete(f, 1) - 1
        trouve = False
        stop = False
        i, j = 0, 0
        matricule = int(matricule)

        # recherche externe
        while bloc_inf <= bloc_sup and not trouve and not stop:
            i = (bloc_inf + bloc_sup) // 2
            buff = lire_dir(f, i)  # lire le bloc du milieu dans le Buffer

            liste_matricules = tuple(map(lambda e: int(split_enreg(e)[1]), buff.tab[0:buff.nb]))
            premier_matricule, dernier_matricule = liste_matricules[0], liste_matricules[-1]

            if premier_matricule <= matricule <= dernier_matricule:
                e_inf, e_sup = 0, buff.nb - 1

                # recherche interne
                while e_inf <= e_sup and not trouve:
                    j = (e_inf + e_sup) // 2
                    matricule_courant = int(split_enreg(buff.tab[j])[1])
                    if matricule == matricule_courant:
                        trouve = True
                    elif matricule < matricule_courant:
                        e_sup = j - 1
                    else:  # matricule > matricule_courant
                        e_inf = j + 1

                if e_inf > e_sup:
                    j = e_inf
                stop = True
            elif matricule < premier_matricule:
                bloc_sup = i - 1
            else:
                bloc_inf = i + 1

        if bloc_inf > bloc_sup:
            i = bloc_inf
            j = 0

        f.close()
        return trouve, (i, j)

    def inserer(self, etudiant):
        """ Insertion d'un etudiant """
        matricule = split_enreg(etudiant)[1]
        recherche_etudiant = self.rechercher(matricule)
        trouve = recherche_etudiant[0]
        i, j = recherche_etudiant[1]

        if not trouve:
            f = open(self.nom_fichier, 'rb+')

            continu = True
            buff = BUFFER()

            while continu and i < entete(f, 1):
                buff = lire_dir(f, i)
                dernier_etudiant = buff.tab[buff.nb - 1]  # sauvgarder le dernier enregistrement

                k = buff.nb - 1  # faire les decalages a l'interieur de Buffer
                while k > j:
                    buff.tab[k] = buff.tab[k - 1]
                    k -= 1

                buff.tab[j] = etudiant  # insertion d'etudiant dans la position j

                if buff.nb < B:  # si le Buffer n'est pas plein, alors inserer le dernier enreg
                    buff.nb += 1
                    buff.tab[buff.nb - 1] = dernier_etudiant
                    ecrire_dir(f, i, buff)
                    continu = False
                else:  # si le Buffer est plein, alors inserer dans le BLOC i+1
                    ecrire_dir(f, i, buff)
                    i += 1
                    j = 0
                    etudiant = dernier_etudiant

            if i > entete(f, 1) - 1:  # si on depasse la fin du fichier, creer un nouveau BLOC
                buff.__init__()
                buff.tab[0] = etudiant
                buff.nb = 1
                ecrire_dir(f, i, buff)
                affecter_entete(f, 1, i + 1)  # mise a jour d'entete (nombre de blocs)

            affecter_entete(f, 0, entete(f, 0) + 1)  # mise a jour d'entete (nombre d'etudiants)

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
            supprime = etudiant[0]

            if supprime == '1':  # si l'etudiant est deja supprime
                print("\n\tCet etudiant est deja supprime (logiquement)\n")
            else:
                etudiant_enreg = '1' + etudiant_enreg[TAILLE_SUPPRIME:]
                buff.tab[j] = etudiant_enreg
                ecrire_dir(f, i, buff)

            f.close()


def main():
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    def appuyez_sur_entrer():
        continuer = input("\n=> Appuyez sur ENTRER pour continuer\n")

    while True:
        clear()
        print("--------- Fichier TOF ---------\n")
        print("\t[1]. Chargement initial")
        print("\t[2]. Affichage")
        print("\t[3]. Recherche")
        print("\t[4]. Insertion")
        print("\t[5]. Suppression")
        print("\n\t[q]. Quitter")

        choice = input("\n\t=> ").strip().lower()

        if choice == "1":
            clear()
            print("--------- Fichier TOF / Chargement initial ---------\n")
            nom_fichier = input("\t=> Entrez le nom du fichier : ").strip()
            fichier = TOF(nom_fichier=nom_fichier)
            fichier.chargement_initial()
            appuyez_sur_entrer()
        elif choice == "2":
            clear()
            print("--------- Fichier TOF / Affichage ---------\n")
            nom_fichier = input("\t=> Entrez le nom du fichier : ").strip()
            if os.path.exists(nom_fichier):
                fichier = TOF(nom_fichier=nom_fichier)
                fichier.afficher()
            else:
                print("\tCe fichier n'existe pas !")
            appuyez_sur_entrer()
        elif choice == "3":
            clear()
            print("--------- Fichier TOF / Recherche ---------\n")
            nom_fichier = input("\t=> Entrez le nom du fichier : ").strip()
            if os.path.exists(nom_fichier):
                fichier = TOF(nom_fichier=nom_fichier)

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
            print("--------- Fichier TOF / Insertion ---------\n")
            nom_fichier = input("\t=> Entrez le nom du fichier : ").strip()
            if os.path.exists(nom_fichier):
                fichier = TOF(nom_fichier=nom_fichier)

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
            print("--------- Fichier TOF / Suppression ---------\n")
            nom_fichier = input("\t=> Entrez le nom du fichier : ").strip()
            if os.path.exists(nom_fichier):
                fichier = TOF(nom_fichier=nom_fichier)

                matricule = input("\t=> Entrez le matricule de l'etudiant a supprimer : ").strip()
                fichier.supprimer(matricule)
            else:
                print("\t Ce fichier n'existe pas !")
            appuyez_sur_entrer()
        elif choice == "q":
            break
        print()


main()
