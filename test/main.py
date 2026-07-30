from collections import Counter
#remarque


def min_temp_tache(tasks: list[str], n: int) -> int:

    """
    Calcule le temps minimum pour exécuter toutes les tâches en respectant
    le délai de refroidissement n entre deux occurrences d'une même tâche.

    Args:
        tasks: liste de tâches (ex: ["A", "A", "B"])
        n: délai minimum (en unités de temps) entre deux exécutions
           d'une même tâche

    Returns:
        Le nombre d'unités de temps minimum nécessaires (int).
    """
    if not tasks:
        return 0
    counts = Counter(tasks)
    frequencies = list(counts.values())
    maximum_frequency = max(frequencies)
    count_maximum_frequency = frequencies.count(maximum_frequency)

    #si la tâche la plus fréquente est T, qui apparait F fois :
    #chaque étape doit être séparée par au moins 'n' espaces
    #pour faire les F fois T : chaque bloc jusqu'à l'avant dernier durera 'n+1', donc :
    # (F - 1) * (n + 1)
    #et ensuite on compte le nombre de trucs qui ont la même max fréquence F pour finir les tâches
    #(on s'en fout des blocs de refroidissement ici)
    # donc +count_de_ceux_qui_ont_la_max_frequence_F
    result = (maximum_frequency - 1) * (n + 1) + count_maximum_frequency
    return max(result, len(tasks))

print(min_temp_tache([], 3)) # == 0, "Échec Test 1" f