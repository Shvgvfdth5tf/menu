# main.py
import flet as ft
from screen import stage_install
from engine import GameEngine


def main(page: ft.Page):
    try:
        page.rtl = True
        page.title = "برج ابدیت"
        page.padding = 0
        page.spacing = 0
        page.bgcolor = ft.Colors.BLACK
    except Exception as e:
        print("page setup err:", e)

    try:
        ok = stage_install(page)
        print("stage_install:", ok)
    except Exception as e:
        print("stage_install err:", e)

    try:
        game = GameEngine()
        game.page = page
        game.start()
    except Exception as e:
        print("game start err:", e)


ft.app(target=main)