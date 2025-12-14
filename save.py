# save.py
import tkinter as tk
from ui_config import *
import game_state as gs

def save_screen():
    import main
    gs.reset_binds()
    gs.clear_screen()

    frame = tk.Frame(gs.root, bg=ROOT_BG)
    frame.pack(fill="both", expand=True)
    gs.current_screen = frame

    tk.Label(frame, text="저장 기능 (준비 중)",
             font=PIXEL_TITLE,
             bg=ROOT_BG, fg="#fbbf24").pack(pady=40)

    tk.Button(frame, text="← 마키마에게",
              font=PIXEL_FONT,
              relief="solid", bd=3,
              bg="#111827", fg="#f9fafb",
              activebackground="#1f2937",
              command=main.hub_mode).pack()