import operator
import os
from pickle import dumps, loads, dump, load
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

BLOC = [0, [ENREG] * B, -1]
BLOC_SIZE = getsizeof(dumps(BLOC)) + len(ENREG) * (B - 1) + (B - 1)

# -------------------------------------------------------


def resize_chaine(chaine, taille_max):
    """ Completer une chaine avec des '#' """
    return chaine + '#' * (taille_max - len(chaine))


class BUFFER:  # buffer de memoire centrale
    def __init__(self, nb=0, suiv=-1, tab=None):
        self.nb = nb
        self.suiv = suiv
        self.tab = [ENREG] * B if tab is None else tab


def lire_dir(f, i):
    adresse = 2 * getsizeof(dumps(0)) + i * BLOC_SIZE
    f.seek(adresse, 0)
    buff = f.read(BLOC_SIZE)
    buff_final = loads(buff)
    return BUFFER(nb=buff_final[0], tab=buff_final[1], suiv=buff_final[2])


def affecter_entete(f, offset, c):
    adresse = offset * getsizeof(dumps(0))
    f.seek(adresse, 0)
    f.write(dumps(c))


def ecrire_dir(f, i, buff):
    adresse = 2 * getsizeof(dumps(0)) + i * BLOC_SIZE
    f.seek(adresse, 0)
    f.write(dumps([buff.nb, buff.tab, buff.suiv]))


def entete(f, offset):
    adresse = offset * getsizeof(dumps(0))
    f.seek(adresse, 0)
    c = f.read(getsizeof(dumps(0)))
    return loads(c)


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


def save_tab_index(nom_fichier, tab_index):
    f_ti = open(f"{nom_fichier}_tab_index.pkl", "wb")
    dump(tab_index, f_ti)
    f_ti.close()


def load_tab_index(nom_fichier):
    f_ti = open(f"{nom_fichier}_tab_index.pkl", "rb")
    tab_index = load(f_ti)
    f_ti.close()
    return tab_index


def recherche_tab_index(nom_fichier, matricule):
    tab_index = load_tab_index(nom_fichier)
    trouve = False
    j = 0
    inf, sup = 0, len(tab_index) - 1
    matricule = int(matricule)
    while inf <= sup and not trouve:
        j = (inf + sup) // 2
        matricule_courant = list(tab_index.keys())[j]
        if matricule == matricule_courant:
            trouve = True
        elif matricule < matricule_courant:
            sup = j - 1
        else:
            inf = j + 1
    if inf > sup:
        j = inf

    i, j = tab_index[list(tab_index.keys())[j]]  # adresse dans le fichier F1

    return trouve, (i, j)


def afficher_enreg(enreg, db=''):
    """ cette fonction affiche un enregistrement (enreg) """
    supprime, matricule, nom, prenom, affiliation = split_enreg(enreg)
    supprime = bool(int(supprime))
    print(f"{db}| Cle : {matricule}\t| "
          f"Efface : {pr_red('Oui') if supprime else ' Non'}\t\t|")
    print(f"{db}-----------------------------------------")


def pr_red(s): return "\033[91m {}\033[00m".format(s)
def pr_green(s): return "\033[92m {}\033[00m" .format(s)
def pr_cyan(s): return "\033[96m {}\033[00m" .format(s)


class TOFavecZD:  # type de fichier TOF
    def __init__(self, nom_fichier, b=B):
        self.nom_fichier = nom_fichier
        self.b = b

    def chargement_initial(self, etudiants_dict):
        n = len(etudiants_dict)
        i, j = 0, 0
        buff = BUFFER()

        try:
            f = open(self.nom_fichier, 'wb')
        except:
            print("\tImpossible d'ouvrir le fichier")
        else:
            if n == 0:
                etudiants_dict = {}
                ajouter_autre = 'o'
                while ajouter_autre == 'o':
                    print(f"\n\t--- Etudiant {n + 1} :")

                    supprime = '0'  # '0' <=> non supprime (logique), 1 sinon
                    matricule_original = input("\t=> Matricule : ")
                    matricule = resize_chaine(matricule_original, TAILLE_MATRICULE)
                    nom = resize_chaine('', TAILLE_NOM)
                    prenom = resize_chaine('', TAILLE_PRENOM)
                    affiliation = resize_chaine('', TAILLE_AFFILIATION)
                    etudiant = supprime + matricule + nom + prenom + affiliation

                    etudiants_dict[int(matricule_original)] = etudiant

                    n += 1
                    ajouter_autre = input("\n\t=> Avez vous un autre etudiant a ajouter [O/N] : ").strip().lower()

            # ordoner le tableau d'etudiants
            etudiants_ordonee = sorted(etudiants_dict.items(), key=operator.itemgetter(0))
            etudiants = [e[1] for e in etudiants_ordonee]

            tab_index = {}

            f2 = open(f"{self.nom_fichier}_zone_secondaire", "wb")
            affecter_entete(f2, 0, 0)
            affecter_entete(f2, 1, 0)
            f2.close()

            for k in range(n):
                etudiant = etudiants[k]
                if j < B * U:
                    buff.tab[j] = etudiant
                    if k + 1 == n:  # ajouter le max du bloc a la table d'index
                        etudiant_max = buff.tab[j]
                        matricule_max = int(split_enreg(etudiant_max)[1])
                        tab_index[matricule_max] = (i, j)
                    buff.nb += 1
                    j += 1
                else:
                    etudiant_max = buff.tab[buff.nb - 1]  # ajouter le max du bloc a la table d'index
                    matricule_max = int(split_enreg(etudiant_max)[1])
                    tab_index[matricule_max] = (i, buff.nb-1)

                    ecrire_dir(f, i, buff)
                    buff.__init__()  # reinitialiser le buffer
                    buff.tab[0] = etudiant
                    buff.nb = 1
                    j = 1
                    i += 1

                    if k + 1 == n:  # ajouter le max du bloc a la table d'index
                        etudiant_max = buff.tab[0]
                        matricule_max = int(split_enreg(etudiant_max)[1])
                        tab_index[matricule_max] = (i, 0)

            ecrire_dir(f, i, buff)
            affecter_entete(f, 0, n)  # entete 0 : nombre d'etudiants
            affecter_entete(f, 1, i + 1)  # entete 1 : nombre de blocs

            f.close()

            save_tab_index(self.nom_fichier, tab_index)

    def reorganisation(self):
        tab_index = load_tab_index(self.nom_fichier)
        max_cle = list(tab_index.keys())[-1]
        result = self.requete_intervalle(0, max_cle)

        etudiants_dict = {}
        for etudiant in result:
            matricule = int(split_enreg(etudiant)[1])
            etudiants_dict[int(matricule)] = etudiant

        self.chargement_initial(etudiants_dict=etudiants_dict)

    def afficher(self):
        f = open(self.nom_fichier, "rb")
        f2 = open(f"{self.nom_fichier}_zone_secondaire", "rb")

        nb_blocs = entete(f, 1)

        tab_index = load_tab_index(self.nom_fichier)
        print("\n\tTable d'index en MC :\n")
        for matricule in tab_index:
            print("\t-------------------------")
            print(f"\t| {matricule}\t| <{tab_index[matricule][0]}, {tab_index[matricule][1]}>\t|")
        print("\t-------------------------")

        print("\n\tZone Primaire :")
        for i in range(nb_blocs):
            buff = lire_dir(f, i)
            print("\n----------------------------------------------------")
            print(f"| BLOC {i}\t| NB: {buff.nb}\t\t\t| Suiv: {pr_cyan(buff.suiv)} |")
            print("----------------------------------------------------")
            for j in range(buff.nb):
                afficher_enreg(buff.tab[j])

            print("\n\tZone de debordement :")
            if buff.suiv == -1:
                print("\t--------")
                print("\t| VIDE |")
                print("\t--------")
            else:
                bloc_suiv = buff.suiv
                while bloc_suiv != -1:
                    buff2 = lire_dir(f2, bloc_suiv)
                    print("\t----------------------------------------------------")
                    print(f"\t| BLOC {pr_cyan(bloc_suiv)}\t| NB: {buff2.nb}\t\t\t| Suiv: {pr_cyan(buff2.suiv)} |")
                    print("\t----------------------------------------------------")
                    for j in range(buff2.nb):
                        afficher_enreg(buff2.tab[j], db='\t')
                    bloc_suiv = buff2.suiv
                    print()

        f2.close()
        f.close()

    def afficher_zone_secondaire(self):
        f2 = open(f"{self.nom_fichier}_zone_secondaire", "rb")
        nb_blocs = entete(f2, 1)

        print("\n\tZone Secondaire :")
        if nb_blocs == 0:
            print("\t--------")
            print("\t| VIDE |")
            print("\t--------")

        for i in range(nb_blocs):
            buff = lire_dir(f2, i)
            print("\n----------------------------------------------------")
            print(f"| BLOC {i}\t| NB: {buff.nb}\t\t\t| Suiv: {pr_cyan(buff.suiv)} |")
            print("----------------------------------------------------")
            for j in range(buff.nb):
                afficher_enreg(buff.tab[j])

        f2.close()

    def rechercher(self, matricule):
        """ Recherche d'un etudiant avec matricule
            retourner (trouve: boolean, debordement: boolean (i: int, j: int)) """
        f = open(self.nom_fichier, 'rb')

        # 1. Recherche dans la table d'index
        tab_index = load_tab_index(self.nom_fichier)
        trouve = False
        debordement = False
        i_prec = -1
        j = 0
        inf, sup = 0, len(tab_index) - 1
        matricule = int(matricule)
        while inf <= sup and not trouve:
            j = (inf + sup) // 2
            matricule_courant = list(tab_index.keys())[j]
            if matricule == matricule_courant:
                trouve = True
            elif matricule < matricule_courant:
                sup = j - 1
            else:
                inf = j + 1
        if inf > sup:
            j = inf

        if j <= len(tab_index) - 1:
            i, j = tab_index[list(tab_index.keys())[j]]  # adresse dans le fichier F1

            # 2. Recherche dans la zone primaire (F1)
            buff = lire_dir(f, i)
            inf, sup = 0, buff.nb - 1
            trouve = False
            while inf <= sup and not trouve:
                j = (inf + sup) // 2
                matricule_courant = int(split_enreg(buff.tab[j])[1])
                if matricule == matricule_courant:
                    trouve = True
                elif matricule < matricule_courant:
                    sup = j - 1
                else:
                    inf = j + 1
            if inf > sup:
                j = inf

            # 3. Recherche dans la zone secondaire (F2)
            if j > B - 1:  # rechercher la postition dans la zone de debordement
                f2 = open(f"{self.nom_fichier}_zone_secondaire", 'rb')

                debordement = True
                trouve = False
                i, j = buff.suiv, 0
                while i != -1 and not trouve:
                    buff = lire_dir(f2, i)
                    j = 0
                    while j < buff.nb and not trouve:
                        matricule_courant = int(split_enreg(buff.tab[j])[1])
                        if matricule == matricule_courant:
                            trouve = True
                        else:
                            j += 1
                    if not trouve:
                        i_prec = i
                        i = buff.suiv
                if i == -1:
                    if j > B - 1:
                        i = entete(f2, 1)
                        j = 0
                    else:
                        i = i_prec
                        i_prec = -1

                f2.close()

            f.close()
            return debordement, trouve, (i, j), i_prec, False
        else:
            return False, False, (len(tab_index), 0), -1, True

    def requete_intervalle(self, c1, c2):
        c1, c2 = int(c1), int(c2)
        if c1 > c2:
            c1, c2 = c2, c1

        recherche1 = recherche_tab_index(self.nom_fichier, c1)
        i1, j1 = recherche1[1]

        recherche2 = recherche_tab_index(self.nom_fichier, c2)
        i2, j2 = recherche2[1]

        f = open(self.nom_fichier, 'rb')
        f2 = open(f"{self.nom_fichier}_zone_secondaire", 'rb')
        result = []

        for i in range(i1, i2 + 1):
            buff = lire_dir(f, i)
            for j in range(buff.nb):
                cle = int(split_enreg(buff.tab[j])[1])
                if c1 <= cle <= c2:
                    result.append(buff.tab[j])
            if buff.suiv != -1:
                bloc_suiv = buff.suiv
                while bloc_suiv != -1:
                    buff2 = lire_dir(f2, bloc_suiv)
                    for j in range(buff2.nb):
                        cle = int(split_enreg(buff2.tab[j])[1])
                        if c1 <= cle <= c2:
                            result.append(buff2.tab[j])
                    bloc_suiv = buff2.suiv

        f.close()
        f2.close()

        return result

    def inserer(self, etudiant):
        """ Insertion d'un etudiant """
        matricule = split_enreg(etudiant)[1]
        recherche_etudiant = self.rechercher(matricule)
        debordement = recherche_etudiant[0]
        trouve = recherche_etudiant[1]
        i, j = recherche_etudiant[2]
        i_prec = recherche_etudiant[3]
        depass_max = recherche_etudiant[4]

        if not trouve:
            f = open(self.nom_fichier, 'rb+')

            if depass_max:
                tab_index = load_tab_index(self.nom_fichier)
                tab_index[int(matricule)] = (i, 0)
                save_tab_index(self.nom_fichier, tab_index)
                buff = BUFFER(tab=[etudiant], nb=1)
                ecrire_dir(f, entete(f, 1), buff)
                affecter_entete(f, 1, entete(f, 1) + 1)

            elif not debordement:
                buff = lire_dir(f, i)
                dernier_etudiant = buff.tab[buff.nb - 1]  # sauvgarder le dernier enregistrement

                k = buff.nb - 1  # faire les decalages a l'interieur du Buffer
                while k > j:
                    buff.tab[k] = buff.tab[k - 1]
                    k -= 1

                buff.tab[j] = etudiant  # inserer l'enreg dans la position j

                if buff.nb < B:  # si le Buffer n'est pas plein, inserer le dernier enreg a la fin
                    buff.nb += 1
                    buff.tab.append(dernier_etudiant)
                    ecrire_dir(f, i, buff)
                else:  # si le Buffer est plein, alors inserer le dernier enreg dans la zone de debordement
                    ecrire_dir(f, i, buff)

                    f2 = open(f"{self.nom_fichier}_zone_secondaire", 'rb+')
                    bloc_suivant = buff.suiv

                    if bloc_suivant == -1:  # s'il n'y a pas de zone de debordement
                        bloc_suivant = entete(f2, 1)  # nombre de blocs dans F2
                        buff.suiv = bloc_suivant  # m-a-j le suivant de bloc primaire
                        ecrire_dir(f, i, buff)

                        buff = BUFFER(tab=[dernier_etudiant], nb=1)  # creer un nouveau bloc secondaire
                        ecrire_dir(f2, bloc_suivant, buff)
                        affecter_entete(f2, 1, entete(f2, 1) + 1)  # m-a-j le nombre de blocs dans F2
                    else:  # s'il y a deja une zone de debordement
                        num_bloc = bloc_suivant
                        buff = lire_dir(f2, num_bloc)
                        while buff.suiv != -1:  # trouver le num du dernier bloc
                            num_bloc = buff.suiv
                            buff = lire_dir(f2, num_bloc)

                        if buff.nb < B:  # s'il y'a d'espace dans le dernier bloc
                            buff.nb += 1
                            buff.tab.append(dernier_etudiant)
                            ecrire_dir(f2, num_bloc, buff)
                        else:
                            bloc_suivant = entete(f2, 1)  # nombre de blocs dans F2
                            buff.suiv = bloc_suivant  # m-a-j le suivant du bloc precedent
                            ecrire_dir(f2, num_bloc, buff)

                            buff = BUFFER(tab=[dernier_etudiant], nb=1)  # creer un nouveau bloc secondaire
                            ecrire_dir(f2, bloc_suivant, buff)
                            affecter_entete(f2, 1, entete(f2, 1) + 1)  # m-a-j le nombre de blocs dans F2

                    f2.close()
            else:  # si l'indicateur debordement = True
                f2 = open(f"{self.nom_fichier}_zone_secondaire", 'rb+')

                if i_prec != -1:
                    buff = lire_dir(f2, i_prec)
                    buff.suiv = i
                    ecrire_dir(f2, i_prec, buff)

                    buff = BUFFER(tab=[etudiant], nb=1)
                    affecter_entete(f2, 1, entete(f2, 1) + 1)
                else:
                    buff = lire_dir(f2, i)
                    buff.tab.append(etudiant)
                    buff.nb += 1

                ecrire_dir(f2, i, buff)
                f2.close()

            f.close()
            self.afficher()
        else:
            print("\n\tUn etudiant avec ce matricule exist deja !\n")

    def supprimer(self, matricule):
        """ Suppression d'un etudiant avec le matricule (matricule)"""
        recherche_etudiant = self.rechercher(matricule)
        debordement = recherche_etudiant[0]
        trouve = recherche_etudiant[1]
        i, j = recherche_etudiant[2]

        if not trouve:
            print("\n\tIl n'existe pas d'etudiant avec ce matricule !\n")
        else:
            f = open(f"{self.nom_fichier}{'_zone_secondaire' if debordement else ''}", 'rb+')
            buff = lire_dir(f, i)
            enreg = buff.tab[j]
            enreg = '1' + enreg[TAILLE_SUPPRIME:]
            buff.tab[j] = enreg
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
        print("\t[2]. Affichage (tous)")
        print("\t[3]. Recherche")
        print("\t[4]. Insertion")
        print("\t[5]. Suppression")
        print("\t[6]. Requete a intervalle")
        print("\t[7]. Reorganisation")
        print("\t[8]. Afficher la zone secondaire (de debordement)")
        print("\n\t[q]. Quitter")

        choice = input("\n\t=> ").strip().lower()

        if choice == "1":
            clear()
            print("--------- Fichier TOF / Chargement initial ---------\n")
            nom_fichier = input("\t=> Entrez le nom du fichier : ").strip()
            fichier = TOFavecZD(nom_fichier=nom_fichier)
            fichier.chargement_initial(etudiants_dict={})
            appuyez_sur_entrer()
        elif choice == "2":
            clear()
            print("--------- Fichier TOF / Affichage ---------\n")
            nom_fichier = input("\t=> Entrez le nom du fichier : ").strip()
            if os.path.exists(nom_fichier):
                fichier = TOFavecZD(nom_fichier=nom_fichier)
                fichier.afficher()
            else:
                print("\tCe fichier n'existe pas !")
            appuyez_sur_entrer()
        elif choice == "3":
            clear()
            print("--------- Fichier TOF / Recherche ---------\n")
            nom_fichier = input("\t=> Entrez le nom du fichier : ").strip()
            if os.path.exists(nom_fichier):
                fichier = TOFavecZD(nom_fichier=nom_fichier)

                matricule = input("\t=> Entrez le matricule a rechercher : ").strip()
                recherche_etudiant = fichier.rechercher(matricule)
                debordement = recherche_etudiant[0]
                trouve = recherche_etudiant[1]
                i, j = recherche_etudiant[2]
                if trouve:
                    print("\n\t", f"L'etudiant se trouve dans le bloc {i}, enregistrement {j}, "
                                  f"dans la zone {'de debordement' if debordement else 'primaire'}")
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
                fichier = TOFavecZD(nom_fichier=nom_fichier)

                supprime = '0'
                cle = input("\t=> Matricule : ")
                matricule = resize_chaine(cle, TAILLE_MATRICULE)
                nom = resize_chaine('', TAILLE_NOM)
                prenom = resize_chaine('', TAILLE_PRENOM)
                affiliation = resize_chaine('', TAILLE_AFFILIATION)
                etudiant = supprime + matricule + nom + prenom + affiliation

                if cle.isdigit():
                    fichier.inserer(etudiant)
                else:
                    print("\n\tCle invalide !")
            else:
                print("\t Ce fichier n'existe pas !")
            appuyez_sur_entrer()
        elif choice == "5":
            clear()
            print("--------- Fichier TOF / Suppression ---------\n")
            nom_fichier = input("\t=> Entrez le nom du fichier : ").strip()
            if os.path.exists(nom_fichier):
                fichier = TOFavecZD(nom_fichier=nom_fichier)

                matricule = input("\t=> Entrez le matricule de l'etudiant a supprimer : ").strip()
                fichier.supprimer(matricule)
            else:
                print("\t Ce fichier n'existe pas !")
            appuyez_sur_entrer()
        elif choice == "6":
            clear()
            print("--------- Fichier TOF / Requete a Intervalle ---------\n")
            nom_fichier = input("\t=> Entrez le nom du fichier : ").strip()
            if os.path.exists(nom_fichier):
                fichier = TOFavecZD(nom_fichier=nom_fichier)

                c1 = input("\t=> Entrez la cle 1 : ").strip()
                c2 = input("\t=> Entrez la cle 2 : ").strip()
                result = fichier.requete_intervalle(c1, c2)
                print("\n\tResultats :\n")
                print("-----------------------------------------")
                for enreg in result:
                    afficher_enreg(enreg)
            else:
                print("\t Ce fichier n'existe pas !")
            appuyez_sur_entrer()
        elif choice == "7":
            clear()
            print("--------- Fichier TOF / Reorganisation ---------\n")
            nom_fichier = input("\t=> Entrez le nom du fichier : ").strip()
            if os.path.exists(nom_fichier):
                fichier = TOFavecZD(nom_fichier=nom_fichier)
                fichier.reorganisation()
            else:
                print("\t Ce fichier n'existe pas !")
            appuyez_sur_entrer()
        elif choice == "8":
            clear()
            print("--------- Fichier TOF / Affichage de la zone secondaire ---------\n")
            nom_fichier = input("\t=> Entrez le nom du fichier : ").strip()
            if os.path.exists(nom_fichier):
                fichier = TOFavecZD(nom_fichier=nom_fichier)
                fichier.afficher_zone_secondaire()
            else:
                print("\tCe fichier n'existe pas !")
            appuyez_sur_entrer()
        elif choice == "q":
            break
        print()


main()
