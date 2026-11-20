# menu.py
import flet as ft
from screen import info_text


class MenuMixin:
    def show_main_menu(self):
        try:
            self._reset_page()

            # قاب راهنمای طلایی دور کل صحنه
            guide = ft.Container(
                left=0,
                top=0,
                width=1280,
                height=720,
                border=ft.border.all(2, "#C9A227"),
            )

            # چهار مربع رنگی در گوشه‌های صحنه
            corners = [
                ft.Container(width=40, height=40, bgcolor="#E74C3C", left=0, top=0),
                ft.Container(width=40, height=40, bgcolor="#2ECC71", left=1240, top=0),
                ft.Container(width=40, height=40, bgcolor="#3498DB", left=0, top=680),
                ft.Container(width=40, height=40, bgcolor="#F1C40F", left=1240, top=680),
            ]

            # متن عیب‌یابی گوشه‌ی بالا
            debug = ft.Container(
                left=50,
                top=6,
                content=ft.Text(info_text(), size=11, color="#88AACC"),
            )

            # عنوان و زیرعنوان
            title = ft.Text(
                "برج ابدیت", size=58, color="#E8D28A",
                weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,
            )
            subtitle = ft.Text(
                "آزمایش صحنه‌ی ۱۶:۹ روی موبایل افقی",
                size=18, color="#8AA0C0",
            )

            # سازنده‌ی دکمه‌ی ثابت
            def make_button(text, on_click):
                return ft.Container(
                    width=340,
                    height=54,
                    bgcolor="#1E2638",
                    border=ft.border.all(1, "#3A4A68"),
                    border_radius=8,
                    alignment=ft.alignment.center,
                    ink=True,
                    on_click=on_click,
                    content=ft.Text(text, size=16, color="#E0E8F0"),
                )

            buttons = ft.Column(
                [
                    make_button("پنجره‌ی روکش", self._open_overlay_window),
                    make_button("AlertDialog", self._open_alert_dialog),
                    make_button("SnackBar", self._open_snackbar),
                    make_button("خروج", self._exit_app),
                ],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )

            # ستون وسط صحنه
            center_col = ft.Column(
                [
                    title,
                    ft.Container(height=8),
                    subtitle,
                    ft.Container(height=36),
                    buttons,
                ],
                spacing=0,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )

            # لایه‌ی وسط‌چین روی کل صحنه
            center_layer = ft.Container(
                left=0,
                top=0,
                width=1280,
                height=720,
                alignment=ft.alignment.center,
                content=center_col,
            )

            # ریشه: یک استک پرحجم روی صحنه
            root = ft.Container(
                expand=True,
                bgcolor="#0A0F1F",
                content=ft.Stack(
                    expand=True,
                    controls=[
                        guide,
                        *corners,
                        debug,
                        center_layer,
                    ],
                ),
            )

            self.page.controls.append(root)
            self.page.update()
        except Exception as e:
            print("show_main_menu err:", e)

    # دکمه‌ی پنجره‌ی روکش
    def _open_overlay_window(self, e):
        try:
            def close_overlay(ev):
                try:
                    self.page.overlay.remove(overlay_window)
                    self.page.update()
                except Exception as ex:
                    print("close overlay err:", ex)

            card = ft.Container(
                width=420,
                height=300,
                bgcolor="#1E2638",
                border=ft.border.all(2, "#C9A227"),
                border_radius=12,
                alignment=ft.alignment.center,
                content=ft.Column(
                    [
                        ft.Text("پنجره‌ی روکش", size=24, color="#E8D28A"),
                        ft.Container(height=16),
                        ft.Text("این یک روکش ساده روی صحنه است.", size=15, color="#C8D4E4"),
                        ft.Container(height=24),
                        ft.Container(
                            width=140,
                            height=44,
                            bgcolor="#3A4A68",
                            border_radius=8,
                            alignment=ft.alignment.center,
                            ink=True,
                            on_click=close_overlay,
                            content=ft.Text("بستن", size=15, color="#FFFFFF"),
                        ),
                    ],
                    spacing=0,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )

            overlay_window = ft.Container(
                left=0,
                top=0,
                width=1280,
                height=720,
                bgcolor="#000000AA",
                alignment=ft.alignment.center,
                content=card,
            )

            self.page.overlay.append(overlay_window)
            self.page.update()
        except as_ex:
            print("open overlay err:", as_ex)

    # دکمه‌ی AlertDialog
    def _open_alert_dialog(self, e):
        try:
            def close_alert(ev):
                try:
                    self.page.close(dlg)
                except Exception as ex:
                    print("close alert err:", ex)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("AlertDialog"),
                content=ft.Text("این یک دیالوگ هشدار ساده است."),
                actions=[
                    ft.TextButton("بستن", on_click=close_alert),
                ],
            )
            self.page.open(dlg)
        except Exception as ex:
            print("alert err:", ex)

    # دکمه‌ی SnackBar
    def _open_snackbar(self, e):
        try:
            self.show_message("سلام از SnackBar")
        except Exception as ex:
            print("snack err:", ex)

    # دکمه‌ی خروج
    def _exit_app(self, e):
        try:
            self.page.window.destroy()
        except Exception as ex:
            print("exit err:", ex)