"""Exercice : Système producteur-consommateur
Tu dois simuler une chaîne de traitement de commandes dans un petit e-commerce, 
où des "producteurs" génèrent des commandes et des "consommateurs" les traitent, 
le tout en parallèle via une file d'attente asynchrone.

Consignes :

Écris une coroutine producteur(nom: str, queue: asyncio.Queue, nb_commandes: int) qui :

Génère nb_commandes commandes (par exemple des dictionnaires {"id": ..., "produit": ...}).
Attend un délai aléatoire (asyncio.sleep) entre chaque commande, pour simuler un flux irrégulier.
Met chaque commande dans la queue avec await queue.put(commande).
Affiche un message à chaque commande ajoutée.
Écris une coroutine consommateur(nom: str, queue: asyncio.Queue) qui :

Tourne en boucle infinie.
Récupère une commande avec await queue.get().
Simule un temps de traitement avec asyncio.sleep.
Affiche un message de traitement terminé.
Appelle queue.task_done() après chaque commande traitée.
Écris une coroutine main() qui :

Crée une asyncio.Queue().
Lance 2 producteurs et 3 consommateurs en parallèle.
Attend que tous les producteurs aient fini avec asyncio.gather.
Attend que la queue soit entièrement vidée avec await queue.join().
Annule proprement les tâches consommateurs restantes (elles tournent en boucle infinie, donc il faut les cancel() à la fin).
Ce que ça doit démontrer :

La coordination entre plusieurs coroutines via une Queue partagée.
La différence entre attendre la fin des producteurs (gather) et attendre que tout le travail soit traité (queue.join()).
L'annulation propre de tâches (task.cancel() + gestion de asyncio.CancelledError).
exemple de résultat
[Producteur-1] a ajouté la commande {'id': 'Producteur-1-1', 'produit': 'Casque'}
[Producteur-1] a ajouté la commande {'id': 'Producteur-1-2', 'produit': 'Clavier'}
[Producteur-2] a ajouté la commande {'id': 'Producteur-2-1', 'produit': 'Souris'}
[Producteur-1] a ajouté la commande {'id': 'Producteur-1-3', 'produit': 'Souris'}
  -> [Consommateur-2] a traité la commande {'id': 'Producteur-1-2', 'produit': 'Clavier'}
[Producteur-1] a ajouté la commande {'id': 'Producteur-1-4', 'produit': 'Casque'}
[Producteur-1] a terminé de produire 4 commandes.
  -> [Consommateur-3] a traité la commande {'id': 'Producteur-2-1', 'produit': 'Souris'}
[Producteur-2] a ajouté la commande {'id': 'Producteur-2-2', 'produit': 'Casque'}
  -> [Consommateur-1] a traité la commande {'id': 'Producteur-1-1', 'produit': 'Casque'}
[Producteur-2] a ajouté la commande {'id': 'Producteur-2-3', 'produit': 'Clavier'}
[Producteur-2] a terminé de produire 3 commandes.
>>> Tous les producteurs ont fini de produire.
  -> [Consommateur-1] a traité la commande {'id': 'Producteur-2-2', 'produit': 'Casque'}
  -> [Consommateur-3] a traité la commande {'id': 'Producteur-1-4', 'produit': 'Casque'}
  -> [Consommateur-2] a traité la commande {'id': 'Producteur-1-3', 'produit': 'Souris'}
  -> [Consommateur-1] a traité la commande {'id': 'Producteur-2-3', 'produit': 'Clavier'}
>>> Toutes les commandes ont été traitées (queue vide).
"""

import asyncio
import queue
import random

async def producteur(nom: str, queue: asyncio.Queue, nb_commandes: int):
    produits = ["Casque", "Clavier", "Souris", "Écran", "Tapis"]
    for i in range(1, nb_commandes + 1):
        await asyncio.sleep(random.uniform(0.1, 1))
        commande = {"id": f"{nom}-{i}", "produit": random.choice(produits)}
        await queue.put(commande)
        print(f"[{nom}] a ajouté la commande {commande}")
    print(f"[{nom}] a terminé de produire {nb_commandes} commandes.")

async def consommateur(nom: str, queue: asyncio.Queue):
    try:
        while True:
            commande = await queue.get()
            await asyncio.sleep(random.uniform(0.3, 1))
            print(f"  -> [{nom}] a traité la commande {commande}")
            queue.task_done()
    except asyncio.CancelledError:
        print(f"  -> [{nom}] a été arrêté proprement.")

async def main():
    queue = asyncio.Queue()
    # Démarrage des 3 consommateurs (ils attendent des données en arrière-plan)
    consommateurs = [
        asyncio.create_task(consommateur(f"Consommateur-{i}", queue))
        for i in range(1, 4)
    ]
    # Déclaration des tâches producteurs
    producteurs_tasks = [
        producteur("Producteur-1", queue, nb_commandes=4),
        producteur("Producteur-2", queue, nb_commandes=3),
    ]

    # on attend que tous les producteurs terminent leur boucle
    await asyncio.gather(*producteurs_tasks)
    print(">>> Tous les producteurs ont fini de produire.")

    # On attend que TOUTES les tâches de la queue soient marquées 'task_done()'
    await queue.join()
    print(">>> Toutes les commandes ont été traitées (queue vide).")

    # Annulation propre des consommateurs (boucles infinies)
    for task in consommateurs:
        task.cancel()

    # On attend la confirmation de leur annulation pour clore proprement le script
    await asyncio.gather(*consommateurs, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())