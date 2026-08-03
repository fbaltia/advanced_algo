#il faut 
#                       pip install windows-curses

import curses



def main(screen: curses.window):
    SIZE = 6
    def print_area():
        screen.addstr(0,0, "Bonjour à tous!")
        screen.addstr(1,0, f"{'1'* SIZE}")
        for i in range(2, SIZE):
            screen.addstr(i, 0, f'1{'0' * (SIZE - 2)}1')
        screen.addstr(SIZE,0, f"{'1'* SIZE}")

    # cache le curseur du terminal
    
    curses.curs_set(False)
    # nettoyer l'écran
    screen.clear()
    # remplir le buffer avec un texte qu'on construit
    print_area()
    # rafraichir la page avec le contenu du buffer
    screen.refresh()

    # attend l'input de l'utilisateur
    key = screen.getch()
    if key in (10, 13, curses.KEY_ENTER):
        print("l'utilisateur a bien appuyé sur enter")

curses.wrapper(main)