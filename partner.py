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
    # 뒤로가기 버튼
    # ==========================
    back_btn = tk.Button(
        frame,
        text="← 마키마에게",
        font=PIXEL_FONT,
        relief="solid", bd=3,
        bg="#111827", fg="#f9fafb",
        activebackground="#1f2937",
        command=main.hub_mode
    )
    canvas.create_window(20, 20, window=back_btn, anchor="nw")

    # ==========================
    # 동료 정의
    # (획득했을 때 보여줄 이미지)
    # ==========================
    ally_defs = [
        ("aki", "아키", "aki1.png"),
        ("power", "파워", "power1.png"),
    ]

    allies_obtained = set(gs.allies_obtained) if hasattr(gs, "allies_obtained") else set()

    # ✅ "획득한 애들만" 필터
    obtained_defs = [d for d in ally_defs if d[0] in allies_obtained]

    # 아무도 없으면 안내만 띄우고 종료
    if not obtained_defs:
        canvas.create_text(
            W // 2, H // 2,
            text="아직 동료가 없어.\n뽑기를 통해 동료를 모아봐!",
            font=PIXEL_FONT,
            fill="#9ca3af",
            justify="center"
        )
        canvas.create_text(
            W // 2, H - 40,
            text="※ 뽑기에서 동료를 획득하면 이곳에 표시돼.",
            font=PIXEL_SMALL,
            fill="#94a3b8"
        )
        return

    # ==========================
    # 카드 레이아웃(획득한 수에 맞춰 중앙 정렬)
    # ==========================
    n = len(obtained_defs)
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

    # ==========================
    # 카드 생성 (획득한 동료만)
    # ==========================
    for i, (key, name_kor, filename) in enumerate(obtained_defs):
        cx = xs[i]

        x1 = cx - card_w // 2
        y1 = cy - card_h // 2
        x2 = cx + card_w // 2
        y2 = cy + card_h // 2

        # 카드 배경
        canvas.create_rectangle(
            x1, y1, x2, y2,
            fill="#111827", outline="#4b5563", width=3
        )
        canvas.create_rectangle(
            x1 + 6, y1 + 6, x2 - 6, y2 - 6,
            fill="#0b1220", outline="#1f2937", width=2
        )

        # 이미지 (획득했으니 got 이미지만 씀)
        img_path = os.path.join(IMG_DIR, filename)
        if os.path.exists(img_path):
            img = fit_soft(img_path, img_box_w, img_box_h)
        else:
            # 혹시 파일 없으면 fallback
            img = Image.new("RGBA", (img_box_w, img_box_h), (30, 30, 40, 255))

        tkimg = ImageTk.PhotoImage(img)
        canvas.ally_imgs.append(tkimg)

        canvas.create_image(cx, y1 + 60 + img_box_h // 2, image=tkimg)

        # 이름
        canvas.create_text(
            cx, y2 - 80,
            text=name_kor,
            font=PIXEL_FONT,
            fill="#e5e7eb"
        )

        # 상태(획득한 애들만 표시하니까 고정)
        canvas.create_text(
            cx, y2 - 50,
            text="동료",
            font=PIXEL_SMALL,
            fill="#34d399"
        )

    # ==========================
    # 안내 문구
    # ==========================
    canvas.create_text(
        W // 2, H - 40,
        text="※ 뽑기에서 동료를 획득하면 이곳에 표시돼.",
        font=PIXEL_SMALL,
        fill="#94a3b8"
    )