# screen.py
import sys
import flet as ft

STAGE_W = 1280
STAGE_H = 720
FORCE_STAGE = False

_state = {
    "active": False,
    "scale": 1.0,
    "page": None,
    "root": None,
    "outer": None,
    "stage_stack": None,
    "stage_box": None,
    "game_layer": None,
    "overlay_layer": None,
}

_orig = {}


def stage_active():
    return bool(_state.get("active"))


def stage_scale():
    return float(_state.get("scale", 1.0))


def _platform_str(page):
    try:
        p = getattr(page, "platform", "")
        return str(p) if p is not None else ""
    except Exception:
        return ""


def _is_mobile(page):
    s = _platform_str(page).lower()
    return ("android" in s) or ("ios" in s)


def _get_bars(page):
    # نوارهای سیستم را از page.media می‌خوانیم
    left = top = right = bottom = 0
    try:
        m = getattr(page, "media", None)
        if m is not None:
            pad = getattr(m, "padding", None)
            if pad is not None:
                left = int(getattr(pad, "left", 0) or 0)
                top = int(getattr(pad, "top", 0) or 0)
                right = int(getattr(pad, "right", 0) or 0)
                bottom = int(getattr(pad, "bottom", 0) or 0)
    except Exception as e:
        print("bars err:", e)
    if top == 0 and _is_mobile(page):
        top = 24
    return left, top, right, bottom


def _usable_area(page):
    w = h = 0
    try:
        w = int(getattr(page.window, "width", 0) or 0)
    except Exception:
        w = 0
    try:
        h = int(getattr(page.window, "height", 0) or 0)
    except Exception:
        h = 0
    left, top, right, bottom = _get_bars(page)
    if w <= 0:
        w = STAGE_W
    if h <= 0:
        h = STAGE_H
    uw = max(1, w - left - right)
    uh = max(1, h - top - bottom)
    return w, h, uw, uh


def _save_originals():
    if _orig:
        return
    try:
        p = ft.Page.__dict__.get("controls")
        if isinstance(p, property):
            _orig["controls_get"] = p.fget
            _orig["controls_set"] = p.fset
    except Exception as e:
        print("save controls err:", e)
    try:
        p = ft.Page.__dict__.get("overlay")
        if isinstance(p, property):
            _orig["overlay_get"] = p.fget
            _orig["overlay_set"] = p.fset
    except Exception as e:
        print("save overlay err:", e)


def _apply_patch():
    # getter/setter اصلی را حفظ، ولی برای کد کاربر لایه‌ها را برمی‌گردانیم
    try:
        gc = _orig.get("controls_get")
        sc = _orig.get("controls_set")
        go = _orig.get("overlay_get")
        so = _orig.get("overlay_set")
        if not (gc and sc and go and so):
            print("patch skip: originals missing")
            return

        def cget(self):
            if _state.get("active"):
                try:
                    name = sys._getframe(1).f_globals.get("__name__", "")
                    if not name.startswith("flet"):
                        layer = _state.get("game_layer")
                        if layer is not None:
                            return layer.controls
                except Exception:
                    pass
            return gc(self)

        def cset(self, value):
            if _state.get("active"):
                try:
                    name = sys._getframe(1).f_globals.get("__name__", "")
                    if not name.startswith("flet"):
                        layer = _state.get("game_layer")
                        if layer is not None:
                            layer.controls = list(value)
                            return
                except Exception:
                    pass
            return sc(self, value)

        def oget(self):
            if _state.get("active"):
                try:
                    name = sys._getframe(1).f_globals.get("__name__", "")
                    if not name.startswith("flet"):
                        layer = _state.get("overlay_layer")
                        if layer is not None:
                            return layer.controls
                except Exception:
                    pass
            return go(self)

        def oset(self, value):
            if _state.get("active"):
                try:
                    name = sys._getframe(1).f_globals.get("__name__", "")
                    if not name.startswith("flet"):
                        layer = _state.get("overlay_layer")
                        if layer is not None:
                            layer.controls = list(value)
                            return
                except Exception:
                    pass
            return so(self, value)

        ft.Page.controls = property(cget, cset)
        ft.Page.overlay = property(oget, oset)
    except Exception as e:
        print("patch err:", e)


def _relayout(page):
    try:
        w, h, uw, uh = _usable_area(page)
        scale = min(uw / float(STAGE_W), uh / float(STAGE_H), 1.0)
        if scale <= 0:
            scale = 1.0
        _state["scale"] = scale

        box = _state.get("stage_box")
        if box is not None:
            try:
                box.scale = ft.Scale(scale=scale, alignment=ft.alignment.top_left)
            except Exception as e:
                print("box scale err:", e)

        stack = _state.get("stage_stack")
        if stack is not None:
            try:
                stack.width = max(1.0, STAGE_W * scale)
                stack.height = max(1.0, STAGE_H * scale)
            except Exception as e:
                print("stack size err:", e)

        outer = _state.get("outer")
        if outer is not None:
            try:
                left, top, right, bottom = _get_bars(page)
                outer.padding = ft.padding.only(
                    left=left, top=top, right=right, bottom=bottom
                )
            except Exception as e:
                print("outer pad err:", e)

        try:
            page.update()
        except Exception as e:
            print("update err:", e)
    except Exception as e:
        print("relayout err:", e)


def _install_hooks(page):
    prev_resized = getattr(page, "on_resized", None)

    def on_resized(e):
        try:
            _relayout(page)
        except Exception as ex:
            print("on_resized err:", ex)
        if prev_resized is not None:
            try:
                prev_resized(e)
            except Exception as ex:
                print("prev on_resized err:", ex)

    try:
        page.on_resized = on_resized
    except Exception as e:
        print("set on_resized err:", e)

    prev_media = getattr(page, "on_media_change", None)

    def on_media(e):
        try:
            _relayout(page)
        except Exception as ex:
            print("on_media err:", ex)
        if prev_media is not None:
            try:
                prev_media(e)
            except Exception as ex:
                print("prev on_media err:", ex)

    try:
        page.on_media_change = on_media
    except Exception as e:
        print("set on_media_change err:", e)


def stage_install(page):
    try:
        if not (FORCE_STAGE or _is_mobile(page)):
            return False

        _save_originals()
        if not _orig:
            print("stage_install: originals missing, abort")
            return False

        _state["page"] = page

        # دو لایه‌ی داخلی
        game_layer = ft.Column(expand=True, spacing=0)
        overlay_layer = ft.Stack(expand=True, spacing=0)
        _state["game_layer"] = game_layer
        _state["overlay_layer"] = overlay_layer

        # جعبه‌ی 1280×720 که با scale کوچک می‌شود
        stage_box = ft.Container(
            left=0,
            top=0,
            width=STAGE_W,
            height=STAGE_H,
            scale=ft.Scale(scale=1.0, alignment=ft.alignment.top_left),
            content=ft.Stack(controls=[game_layer, overlay_layer], expand=True),
        )
        _state["stage_box"] = stage_box

        # استک بیرونی به اندازه‌ی scale*1280 × scale*720
        stage_stack = ft.Stack(
            width=STAGE_W,
            height=STAGE_H,
            alignment=ft.alignment.top_left,
            controls=[stage_box],
        )
        _state["stage_stack"] = stage_stack

        # وسط‌چین کردن در ناحیه‌ی قابل‌استفاده
        outer = ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            content=stage_stack,
        )
        _state["outer"] = outer

        # ریشه‌ی گرادیانی
        root = ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=["#0A0F1F", "#0E1428", "#04060D"],
            ),
            content=outer,
        )
        _state["root"] = root

        # نصب ریشه با setter اصلی
        try:
            _orig["controls_set"](page, [root])
        except Exception as e:
            print("set root err:", e)
            return False

        _state["active"] = True
        _apply_patch()
        _install_hooks(page)
        _relayout(page)
        return True
    except Exception as e:
        print("stage_install err:", e)
        _state["active"] = False
        return False


def info_text():
    page = _state.get("page")
    plat = ""
    w = h = 0
    uw = uh = 0
    if page is not None:
        plat = _platform_str(page)
        try:
            w, h, uw, uh = _usable_area(page)
        except Exception as e:
            print("info_text err:", e)
    s = _state.get("scale", 1.0)
    a = _state.get("active", False)
    return (
        f"پلتفرم: {plat} | صفحه: {w}×{h} | قابل‌استفاده: {uw}×{uh} | "
        f"ضریب: {s:.3f} | صحنه فعال: {a}"
    )