import pygame as py
import sys
from menu import MainMenu
import map

WIDTH=map.WIDTH
HEIGHT=map.HEIGHT

def main():
    py.init()
    screen=py.display.set_mode((WIDTH,HEIGHT))

    state="MENU"
    while state!="QUIT":
        if state=="MENU":
            menu=MainMenu(screen)
            state=menu.run()          
        elif state=="PLAYING":
            result=map.run_game(screen)
            state=result if result else "QUIT"

    py.quit()
    sys.exit()

if __name__=="__main__":
    main()