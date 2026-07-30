# Ne pas oublier la première fois:
# pip install asyncio
import asyncio

async def charger_meteo():
    await asyncio.sleep(2)
    return "22°C"

async def charger_actualite():
    await asyncio.sleep(1)
    return ["Interdiction de fumer/vapoter en terasse en 2027"]

def processus_long():
    print("début du processus")
    texte = ""
    part = "a" *1000
    for i in range(1000_000):
        texte += f"{part}"
    print("fin du processus")

async def main():
    # # attend d'une seule coroutine asynchrone
    # resultat = await charger_meteo()
    # print(resultat)

    # tache1 = asyncio.create_task(charger_meteo())
    # print("action intermédiaire avant l'affichage de tache1")
    # print(await tache1)

    # resultats = await asyncio.gather(charger_meteo(), charger_actualite())
    # print(resultats)

    # taches = {
    #     asyncio.create_task(charger_meteo()),
    #     asyncio.create_task(charger_actualite())
    # }
    # fini, en_cours = await asyncio.wait(taches, return_when=asyncio.FIRST_COMPLETED)
    # print(fini.pop().result())
    # # bonne pratique: annuler des coroutine toujours en cours dans ce cas wait
    # for tache in en_cours:
    #     tache.cancel()


    boucle = asyncio.get_running_loop()
    # None => TreadPoolExecutor par defaut
    boucle.run_in_executor(None, processus_long)

    resultat = await charger_meteo()
    print(resultat)

asyncio.run(main())