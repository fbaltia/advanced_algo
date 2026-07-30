values = [1,2,3]

def permutation(tab: list[int]):
    result = []
    path = []
    used = [False] * len(tab)

    def backtrack():
        #pour sortir de la récursion
        if len(path) == len(tab):
            result.append(tuple(path.copy()))
            return

        for i in range(len(tab)):
            #passer les éléments déjà visités
            if used[i]:
                continue

            # faire un choix
            path.append(tab[i])
            used[i] = True

            #explorer les autres possibilités
            backtrack()

            #annuler le choix en cours
            path.pop()
            used[i] = False
    backtrack()
    return result

print(permutation(values))