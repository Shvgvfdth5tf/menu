# engine.py
import flet as ft
from menu import MenuMixin


class GameEngine(MenuMixin):
    def __init__(self):
        self.page = None

    def start(self):
        try:
            self.show_main_menu()
        except Exception as e:
            print("start err:", e)

    def _reset_page(self):
        try:
            self.page.controls.clear()
            self.page.overlay.clear()
        except Exception as e:
            print("reset err:", e)

    def show_message(self, text):
        try:
            sb = ft.SnackBar(content=ft.Text(text))
            self.page.open(sb)
        except Exception as e:
            print("snack err:", e)