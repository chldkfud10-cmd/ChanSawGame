# partner.py
import tkinter as tk
from PIL import Image, ImageTk, Image
import os

from ui_config import *
import game_state as gs


def partner_mode():
    import main  # 순환 import 방지

    gs.reset_binds()
    gs.clear_screen()

    frame = tk.Frame(gs.root, bg=ROOT_BG)
    frame.pack(fill="both", expand=True)
    gs.current_screen = frame

    W, H = ROOT_W, ROOT_H

    canvas = tk.Canvas(
        frame,
        width=W, height=H,
        bg="#020617",
        highlightthickness=4,
        highlightbackground=PANEL_BORDER
    )
    canvas.pack(expand=True)

    # ==========================
    # 상단 타이틀
    # ==========================
    canvas.create_text(
        W // 2, 55,
        text="덴지의 동료들",
        font=PIXEL_TITLE,
        fill="#fbbf24"
    )
    canvas.create_text(
        W // 2, 90,
        text="지금까지 모은 동료들이야.",
        font=PIXEL_FONT,
        fill="#cbd5e1"
    )

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
    # 동료 정의
    # (획득했을 때 보여줄 이미지)
    # ==========================
    ally_defs = [
        ("aki", "아키", "aki1.png"),
        ("power", "파워", "power1.png"),
    ]

    allies_obtained = set(gs.allies_obtained) if hasattr(gs, "allies_obtained") else set()

    # ==========================
    # 카드 레이아웃(모든 동료 표시)
    # ==========================
    n = len(ally_defs)
    xs = [int(W * (i + 1) / (n + 1)) for i in range(n)]  # 균등 분배로 가운데 정렬
    cy = H // 2 + 20

    card_w = int(min(260, W * 0.22))
    card_h = int(min(330, H * 0.46))

    img_box_w = int(card_w * 0.75)
    img_box_h = int(card_h * 0.55)

    canvas.ally_imgs = []  # ✅ 이미지 참조 유지

    def fit_soft(path, w, h):
        img = Image.open(path).convert("RGBA")
        iw, ih = img.size
        scale = min(w / iw, h / ih)
        new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
        return img.resize(new_size, Image.LANCZOS)

    def convert_to_grayscale(img):
        """이미지를 흑백으로 변환"""
        # RGBA 이미지를 RGB로 변환 후 grayscale로 변환
        rgb_img = img.convert("RGB")
        gray_img = rgb_img.convert("L")
        # 다시 RGBA로 변환 (알파 채널 유지)
        rgba_img = Image.new("RGBA", img.size)
        rgba_img.paste(gray_img.convert("RGB"), (0, 0))
        # 알파 채널 복원
        if img.mode == "RGBA":
            rgba_img.putalpha(img.split()[3])
        return rgba_img

    # ==========================
    # 카드 생성 (모든 동료 표시)
    # ==========================
    for i, (key, name_kor, filename) in enumerate(ally_defs):
        cx = xs[i]
        is_obtained = key in allies_obtained

        x1 = cx - card_w // 2
        y1 = cy - card_h // 2
        x2 = cx + card_w // 2
        y2 = cy + card_h // 2

        # 카드 배경 (흰색)
        canvas.create_rectangle(
            x1, y1, x2, y2,
            fill="#ffffff", outline="#d1d5db", width=3
        )
        canvas.create_rectangle(
            x1 + 6, y1 + 6, x2 - 6, y2 - 6,
            fill="#f9fafb", outline="#e5e7eb", width=2
        )

        # 이미지 로드 및 처리
        img_path = os.path.join(IMG_DIR, filename)
        if os.path.exists(img_path):
            img = fit_soft(img_path, img_box_w, img_box_h)
            # 획득하지 않은 동료는 흑백으로 변환
            if not is_obtained:
                img = convert_to_grayscale(img)
        else:
            # 혹시 파일 없으면 fallback
            img = Image.new("RGBA", (img_box_w, img_box_h), (30, 30, 40, 255))
            if not is_obtained:
                img = convert_to_grayscale(img)

        tkimg = ImageTk.PhotoImage(img)
        canvas.ally_imgs.append(tkimg)

        canvas.create_image(cx, y1 + 60 + img_box_h // 2, image=tkimg)

        # 이름 (획득 여부에 따라 색상 변경)
        name_color = "#e5e7eb" if is_obtained else "#6b7280"
        canvas.create_text(
            cx, y2 - 80,
            text=name_kor,
            font=PIXEL_FONT,
            fill=name_color
        )

        # 상태 (획득 여부에 따라 표시)
        if is_obtained:
            status_text = "동료"
            status_color = "#34d399"
        else:
            status_text = "미획득"
            status_color = "#6b7280"
        
        canvas.create_text(
            cx, y2 - 50,
            text=status_text,
            font=PIXEL_SMALL,
            fill=status_color
        )

    # ==========================
    # 안내 문구
    # ==========================
    canvas.create_text(
        W // 2, H - 40,
        text="※ 뽑기에서 동료를 획득하면 컬러로 표시돼.",
        font=PIXEL_SMALL,
        fill="#94a3b8"
    )