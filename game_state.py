# game_state.py
import tkinter as tk
from ui_config import ROOT_W, ROOT_H

root = tk.Tk()
root.title("Chainsaw Man - Retro Ver")
root.geometry(f"{ROOT_W}x{ROOT_H}")

current_screen = None

ticket_count = 0

stage_cleared = {
    1: False,
    2: False,
    3: False,
    4: False
}

allies_obtained = set()


def clear_screen():
    global current_screen
    if current_screen:
        current_screen.destroy()
        current_screen = None


def reset_binds():
    """
    화면이 바뀔 때마다 이전 화면에서 걸어둔 bind가 살아있어서
    (엔터 누르면 계속 넘어가거나) 이상해지는 걸 방지.
    """
    # 자주 쓰는 것들만 싹 제거
    for seq in ("<Return>", "<space>", "<Key>", "<KeyPress>", "<KeyRelease>"):
        try:
            root.unbind(seq)
        except Exception:
            pass