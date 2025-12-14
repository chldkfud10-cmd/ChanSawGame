# gacha.py
import tkinter as tk
from PIL import Image, ImageTk, Image
import random, os

from ui_config import *
import game_state as gs


def gacha_mode():
    import main  # 🔥 순환 import 방지

    gs.reset_binds()
    gs.clear_screen()

    frame = tk.Frame(gs.root, bg=ROOT_BG)
    frame.pack(fill="both", expand=True)
    gs.current_screen = frame

    # ✅ 메인/허브처럼 꽉 차게
    W, H = ROOT_W, ROOT_H

    # ==========================
    # 캔버스 (ROOT 크기)
    # ==========================
    canvas = tk.Canvas(
        frame,
        width=W, height=H,
        bg="#020617",
        highlightthickness=4,
        highlightbackground=PANEL_BORDER
    )
    canvas.pack(expand=True)

    # 배경 그리드
    grid_step = 40
    for x in range(0, W, grid_step):
        canvas.create_line(x, 0, x, H, fill="#111827")
    for y in range(0, H, grid_step):
        canvas.create_line(0, y, W, y, fill="#111827")

    # 안내 텍스트
    info_text = canvas.create_text(
        W // 2, 55,
        text="마키마: 뽑기권으로 동료를 뽑아봐.",
        font=PIXEL_FONT,
        fill="#f9fafb"
    )

    # 티켓 표시 (우상단)
    ticket_text = canvas.create_text(
        W - 130, 40,
        text=f"뽑기권: {gs.ticket_count}장",
        font=PIXEL_FONT,
        fill="#e5e7eb"
    )

    def update_ticket_text():
        canvas.itemconfig(ticket_text, text=f"뽑기권: {gs.ticket_count}장")

    # 결과 표시 영역 프레임 (화면 커진만큼 조금 더 크게)
    box_margin_x = 110
    box_top = 100
    box_bottom = H - 140

    canvas.create_rectangle(
        box_margin_x, box_top, W - box_margin_x, box_bottom,
        outline="#4b5563", width=3, fill="#020617"
    )

    result_text = canvas.create_text(
        W // 2, H - 120,
        text="\"뽑기!\" 버튼을 눌러봐.",
        font=PIXEL_FONT,
        fill="#e5e7eb"
    )

    # 이미지 GC 방지용
    canvas.result_tk = None
    result_img_id = None

    # ==========================
    # 이미지 리사이즈
    # ==========================
    def fit_soft(path, w, h):
        img = Image.open(path).convert("RGBA")
        iw, ih = img.size
        scale = min(w / iw, h / ih)
        new_size = (int(iw * scale), int(ih * scale))
        return img.resize(new_size, Image.LANCZOS)

    # ==========================
    # 중복 획득 판정용 카운터
    # ==========================
    if not hasattr(gs, "gacha_counts") or gs.gacha_counts is None:
        gs.gacha_counts = {}  # {"aki": 1, "power": 2, ...}

    def do_draw():
        nonlocal result_img_id

        if gs.ticket_count <= 0:
            canvas.itemconfig(
                info_text,
                text="마키마: 뽑기권이 없네. 다시 악마를 쓰러뜨리고 와."
            )
            return

        # 티켓 1장 소비
        gs.ticket_count -= 1
        update_ticket_text()

        # ✅ 무조건 아키
        choice = "aki"
        gs.allies_obtained.add(choice)

        # 중복 카운트 증가
        gs.gacha_counts[choice] = gs.gacha_counts.get(choice, 0) + 1
        is_dup = gs.gacha_counts[choice] > 1

        # 아키 설정
        path = os.path.join(IMG_DIR, "aki1.png")
        label = "아키가 나타났다!"
        fallback = (80, 160, 220, 255)

        # 이미지 로드/리사이즈
        if os.path.exists(path):
            img = fit_soft(path, 300, 380)
        else:
            img = Image.new("RGBA", (220, 320), fallback)

        tkimg = ImageTk.PhotoImage(img)
        canvas.result_tk = tkimg  # GC 방지

        # 이미지 위치: 중앙
        img_cx = W // 2
        img_cy = (box_top + box_bottom) // 2 - 10

        if result_img_id is None:
            result_img_id = canvas.create_image(img_cx, img_cy, image=tkimg)
        else:
            canvas.itemconfig(result_img_id, image=tkimg)
            canvas.coords(result_img_id, img_cx, img_cy)

        extra = " (중복 획득)" if is_dup else ""
        canvas.itemconfig(info_text, text=f"마키마: {label}{extra}")
        canvas.itemconfig(result_text, text="또 뽑고 싶으면 한 번 더 눌러봐.")

    # ==========================
    # 뒤로가기 버튼 (텍스트만)
    # ==========================
    back_text = canvas.create_text(
        20, 20,
        text="← 마키마에게",
        font=PIXEL_FONT,
        fill="#f9fafb",
        anchor="nw"
    )
    
    def on_back_click(_event=None):
        if gs.current_screen is not frame:
            return
        main.hub_mode()
    
    canvas.tag_bind(back_text, "<Button-1>", on_back_click)
    
    # 호버 효과
    def on_back_enter(_event=None):
        canvas.itemconfig(back_text, fill="#cbd5e1")
    
    def on_back_leave(_event=None):
        canvas.itemconfig(back_text, fill="#f9fafb")
    
    canvas.tag_bind(back_text, "<Enter>", on_back_enter)
    canvas.tag_bind(back_text, "<Leave>", on_back_leave)

    # ==========================
    # 뽑기 버튼
    # ==========================
    draw_btn = tk.Button(
        frame,
        text="뽑기!",
        font=PIXEL_TITLE,
        relief="solid", bd=4,
        bg="#10b981", fg="#000000",
        activebackground="#34d399",
        command=do_draw
    )

    # ✅ 중요: 캔버스 위젯들은 "맨 마지막에" 올려야 안 가려짐
    canvas.create_window(W // 2, H - 55, window=draw_btn, anchor="center")  # 하단 중앙