#back tracking exo 2

"""
Exercice : Le problème des N-Reines (Backtracking)
Énoncé
Le problème des N-Reines consiste à placer N reines sur un échiquier de taille N × N de telle sorte qu'aucune reine n'en menace une autre. Cela signifie qu'il ne doit y avoir :

aucune deux reines sur la même ligne,
aucune deux reines sur la même colonne,
aucune deux reines sur la même diagonale.
Objectif
Implémenter une fonction :

def solve_n_queens(n: int) -> list[list[int]]:
    ...
qui retourne toutes les solutions possibles pour un échiquier n × n.

Représentation d'une solution
Chaque solution est une liste board de taille n, où board[i] représente la colonne occupée par la reine sur la ligne i.

Exemple pour n = 4, une solution valide est [1, 3, 0, 2], ce qui signifie :

Reine ligne 0 → colonne 1
Reine ligne 1 → colonne 3
Reine ligne 2 → colonne 0
Reine ligne 3 → colonne 2
Contraintes
1 <= n <= 12 (au-delà, le nombre de solutions explose et le calcul devient long)
La fonction doit retourner une liste de listes (une liste par solution)
L'ordre des solutions dans la liste retournée n'a pas d'importance
Indications
Le squelette ci-dessous illustre le schéma classique du backtracking : choisir → explorer → annuler.

def solve_n_queens(n):
    solutions = []
    board = [-1] * n  # board[i] = colonne de la reine à la ligne i

    def is_safe(row, col):
        pass

    def backtrack(row):
        pass

    backtrack(0)
    return solutions
Résultats attendus (nombre de solutions)
n	nombre de solutions
1	1
2	0
3	0
4	2
5	10
6	4
8	92
Pour aller plus loin (bonus)
Écrire une fonction print_board(board) qui affiche l'échiquier avec des Q et des ..
Écrire une fonction count_n_queens(n) qui compte uniquement le nombre de solutions sans les stocker en mémoire.
Optimiser is_safe en utilisant des set() pour suivre en O(1) les colonnes, diagonales / et diagonales \ déjà occupées,
au lieu de parcourir board à chaque appel.
"""

def solve_n_queens(n: int) -> list[list[int]]:
    #number_of_solutions = 0 #décommenter pour la variante count_n_queens(n)
    solutions = []
    board = [-1] * n  # board[i] = la valeur est la colonne de la reine à la ligne i

    def is_safe(row, col):
        """Vérifie si on peut placer une reine à la position (row, col)."""
        for previous_row in range(row):
            previous_col = board[previous_row]
            # Même colonne ?
            if previous_col == col:
                return False
            # Même diagonale ? 
            if abs(previous_row - row) == abs(previous_col - col):
                return False
        return True

    def backtrack(row):
        #nonlocal number_of_solutions
        """Explore les placements de reines ligne par ligne."""
        # Cas-base : toutes les reines sont bien mises
        if row == n:#décommenter pour la variante count_n_queens(n)
            # Copier l'état courant de l'échiquier et l'ajouter aux solutions
            solutions.append(board.copy())
            #number_of_solutions += 1
            return
        # Essayer de placer une reine dans chaque colonne de la ligne actuelle
        for col in range(n):
            if is_safe(row, col):
                # CHOISIR
                board[row] = col
                # EXPLORER
                backtrack(row + 1)
                # ANNULER (Backtracking)
                board[row] = -1

    # Lancement du backtracking à partir de la ligne 0
    backtrack(0)
    return solutions #, number_of_solutions


def print_board(solutions:list[list[int]]):
    from io import StringIO

    if not solutions or not solutions[0]:
        return None
    n = len(solutions[0])
    for index, solution in enumerate(solutions):
        output = StringIO()

        for row in range(0,n):
            for col in range(0,n):
                if solution[row] == col:
                    output.write("Q ")
                else:
                    output.write(". ")  
            output.write("\n")          
        print("board:",index+1)
        print(output.getvalue())
        print("----")

#TESTS



print("Démarrage des tests pour N-Reines...")

def is_valid_solution(board):
    """Vérifie qu'une solution ne contient pas de conflits."""
    n = len(board)
    for row1 in range(n):
        for row2 in range(row1 + 1, n):
            col1, col2 = board[row1], board[row2]
            if col1 == col2:
                return False
            if abs(col1 - col2) == abs(row1 - row2):
                return False
    return True

# Test 1 : n = 1, une seule solution triviale
print("Test 1...", len(solve_n_queens(1)))
assert len(solve_n_queens(1)) == 1, "Échec Test 1 : n=1 doit avoir 1 solution"
assert solve_n_queens(1) == [[0]], "Échec Test 1 : la solution doit être [0]"

# Test 2 : n = 2, aucune solution possible
print("Test 2...", len(solve_n_queens(2)))
assert len(solve_n_queens(2)) == 0, "Échec Test 2 : n=2 ne doit avoir aucune solution"

# Test 3 : n = 3, aucune solution possible
print("Test 3...", len(solve_n_queens(3)))
assert len(solve_n_queens(3)) == 0, "Échec Test 3 : n=3 ne doit avoir aucune solution"

# Test 4 : n = 4, exactement 2 solutions
print("Test 4...", len(solve_n_queens(4)))
assert len(solve_n_queens(4)) == 2, "Échec Test 4 : n=4 doit avoir 2 solutions"


# Test 5 : n = 5, exactement 10 solutions
soluce = solve_n_queens(5)
print("Test 5...", len(soluce))
print(soluce)
#print("number of solutions", number_of_solutions)
assert len(soluce) == 10, "Échec Test 5 : n=5 doit avoir 10 solutions"
#print(print_board(soluce))


"""
# Test 6 : n = 6, exactement 4 solutions
print("Test 6...", len(solve_n_queens(6)))
assert len(solve_n_queens(6)) == 4, "Échec Test 6 : n=6 doit avoir 4 solutions"

# Test 7 : n = 8, exactement 92 solutions
print("Test 7...", len(solve_n_queens(8)))
assert len(solve_n_queens(8)) == 92, "Échec Test 7 : n=8 doit avoir 92 solutions"

# Test 8 : toutes les solutions retournées sont valides (pas de conflits)
print("Test 8...", all(is_valid_solution(b) for b in solve_n_queens(6)))
assert all(is_valid_solution(b) for b in solve_n_queens(6)), \
    "Échec Test 8 : certaines solutions contiennent des conflits"

# Test 9 : pas de doublons parmi les solutions
solutions_8 = solve_n_queens(8)
print("Test 9...", len(solutions_8) == len({tuple(b) for b in solutions_8}))
assert len(solutions_8) == len({tuple(b) for b in solutions_8}), \
    "Échec Test 9 : des solutions en double ont été trouvées"

# Test 10 : chaque solution a une longueur égale à n, avec des colonnes valides
n = 6
solutions_6 = solve_n_queens(n)
ok = all(len(b) == n and all(0 <= col < n for col in b) for b in solutions_6)
print("Test 10...", ok)
assert ok, "Échec Test 10 : longueur ou colonnes hors bornes"

print("\nTous les tests sont passés avec succès ✅")
"""