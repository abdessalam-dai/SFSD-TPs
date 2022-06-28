class Node:
    def __init__(self, data, suiv=None):
        self.data = data
        self.suiv = suiv

    def __repr__(self):
        return self.data


class LLC:
    def __init__(self, head=None):
        self.head = head

    def __repr__(self):
        result = ''
        node = self.head
        while node is not None:
            result += str(node.data) + ' => '
            node = node.suiv
        return result + 'NULL'

    def longuer(self):
        node = self.head
        compteur = 0
        while node is not None:
            compteur += 1
            node = node.suiv
        return compteur

    def rechercher(self, data):
        node = self.head
        index = -1
        compteur = 0
        while node is not None:
            if node.data == data:
                index = compteur
            compteur += 1
            node = node.suiv
        if index == -1:
            print(f"L'element {data} est non trouve")
        else:
            print(f"L'element {data} se trouve dans le noeud d'indice {index}")

    def inserer(self, data):
        node = Node(data)
        if self.head is None:
            self.head = node
        else:
            self.head.suiv = node

    def supprimer(self, data):
        if self.head.data == data:
            self.head = self.head.suiv
        else:
            prev = self.head
            curr = self.head.suiv
            while curr is not None:
                if curr.data == data:
                    prev.suiv = curr.suiv
                    break
                prev = curr
                curr = curr.suiv

    def construire(self, n):
        prev = None
        self.head = None
        for i in range(n):
            curr = Node(int(input(f"Entrez la {i+1}eme valeur : ")))
            if self.head is None:
                self.head = curr
            else:
                prev.suiv = curr
            prev = curr


llc = LLC()
print(llc)
llc.construire(2)
print(llc)
