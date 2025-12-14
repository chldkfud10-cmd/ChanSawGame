# main.py
from PIL import Image, ImageTk
import tkinter as tk
import os
import random as _rnd

from ui_config import *
import game_state as gs

import stage
from stage import fit_nearest, bbox_intersect, setup_denji, show_victory, show_defeat, world_map
import gacha
import partner
import save
import random

# ==========================
# 타이틀
# ==========================
def title_screen():
    gs.reset_binds()
    gs.clear_screen()

    frame = tk.Frame(gs.root, bg=ROOT_BG)
    frame.pack(fill="both", expand=True)
    gs.current_screen = frame

    canvas = tk.Canvas(
        frame, width=ROOT_W, height=ROOT_H,
        highlightthickness=0, bg=ROOT_BG
    )
    canvas.pack(expand=True)

    # 배경
    bg_path = os.path.join(IMG_DIR, "back1.png")
    if os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGBA")
        img = img.resize((ROOT_W, ROOT_H), Image.NEAREST)
        tkimg = ImageTk.PhotoImage(img)
        canvas.create_image(ROOT_W // 2, ROOT_H // 2, image=tkimg, anchor="center")
        canvas.bg = tkimg  # 참조 유지

    # ==========================
    # START GAME 버튼
    # ==========================
    button_path = os.path.join(IMG_DIR, "back1button.png")
    if os.path.exists(button_path):
        # 버튼 이미지 로드 및 크기 조정
        button_img = Image.open(button_path).convert("RGBA")
        # 버튼 크기를 적절하게 조정 (원본 비율 유지)
        button_width = 300
        button_height = int(button_img.height * (button_width / button_img.width))
        button_img = button_img.resize((button_width, button_height), Image.NEAREST)
        button_tk = ImageTk.PhotoImage(button_img)
        canvas.button_img = button_tk  # 참조 유지
        
        # 화면 중앙 아래쪽에 버튼 배치
        button_x = ROOT_W // 2
        button_y = int(ROOT_H * 0.75)  # 화면 높이의 75% 위치
        
        button_id = canvas.create_image(
            button_x, button_y,
            image=button_tk,
            anchor="center"
        )
        
        # 버튼 클릭 이벤트
        def start_game(_event=None):
            if gs.current_screen is not frame:
                return
            story_mode()
        
        canvas.tag_bind(button_id, "<Button-1>", start_game)
        
        # Enter 키로도 게임 시작 가능
        def on_key(e):
            if gs.current_screen is not frame:
                return
            if e.keysym in ("Return", "space"):
                start_game()
        
        gs.root.bind("<Key>", on_key)
    else:
        # 버튼 이미지가 없을 경우 대체 텍스트 버튼
        button_x = ROOT_W // 2
        button_y = int(ROOT_H * 0.75)
        
        button_id = canvas.create_text(
            button_x, button_y,
            text="START GAME",
            font=("Courier New", 28, "bold"),
            fill="#ffffff"
        )
        
        def start_game(_event=None):
            if gs.current_screen is not frame:
                return
            story_mode()
        
        canvas.tag_bind(button_id, "<Button-1>", start_game)
        
        def on_key(e):
            if gs.current_screen is not frame:
                return
            if e.keysym in ("Return", "space"):
                start_game()
        
        gs.root.bind("<Key>", on_key)


# ==========================
# 스토리 (한글 대사)
# ==========================
story = [
    ("마키마", "이름은?"),
    ("덴지", "덴지......"),
    ("마키마", "그래, 덴지  군. 넌 오늘부터 내 사람이야."),
    ("마키마", "덴지 군, 날 위해서 모든 악마들을 죽여줘. 이건 계약이야.")
]
story_idx = 0


def story_mode():
    global story_idx
    story_idx = 0

    gs.reset_binds()
    gs.clear_screen()

    frame = tk.Frame(gs.root, bg=ROOT_BG)
    frame.pack(fill="both", expand=True)
    gs.current_screen = frame

    W, H = ROOT_W, ROOT_H

    canvas = tk.Canvas(
        frame, width=W, height=H,
        bg=GAME_BG, highlightthickness=4,
        highlightbackground=PANEL_BORDER
    )
    canvas.pack(expand=True)

    # ==== 배경 이미지 (stori1.png) ====
    bg_path = os.path.join(IMG_DIR, "stori1.png")
    if os.path.exists(bg_path):
        bg_img = Image.open(bg_path).convert("RGBA")
        bg_img = bg_img.resize((W, H), Image.NEAREST)
        bg_tk = ImageTk.PhotoImage(bg_img)
        canvas.create_image(W // 2, H // 2, image=bg_tk, anchor="center")
        canvas.bg = bg_tk  # 참조 유지
    else:
        # 이미지가 없을 경우 기본 배경색
        canvas.create_rectangle(0, 0, W, H, fill=GAME_BG, outline="")

    # ==== 덴지 / 마키마 이미지 ====
    def fit_soft(path, w, h):
        img = Image.open(path).convert("RGBA")
        iw, ih = img.size
        scale = min(w / iw, h / ih)
        new_size = (int(iw * scale), int(ih * scale))
        return img.resize(new_size, Image.LANCZOS)

    denji_p = os.path.join(IMG_DIR, "denji1.png")
    makima_p = os.path.join(IMG_DIR, "makima1.png")

    if os.path.exists(denji_p):
        denji_img = fit_soft(denji_p, 1500, 500)
    else:
        denji_img = Image.new("RGBA", (160, 240), (200, 200, 200, 255))

    if os.path.exists(makima_p):
        makima_img = fit_soft(makima_p, 1500, 500)
    else:
        makima_img = Image.new("RGBA", (160, 240), (180, 120, 200, 255))

    denji_tk = ImageTk.PhotoImage(denji_img)
    makima_tk = ImageTk.PhotoImage(makima_img)

    denji_x = int(W * 0.25)
    makima_x = int(W * 0.75)

    char_y = int(H * 0.62)
    denji_y = char_y + 48  # ✅ 덴지(denji1)만 아래로 조금 내리기

    canvas.create_image(denji_x, denji_y, image=denji_tk)   # ✅ 변경
    canvas.create_image(makima_x, char_y, image=makima_tk)  # 마키마는 그대로

    canvas.denji = denji_tk
    canvas.makima = makima_tk

    # ==== 대화창 ====
    log_y1 = H - 160
    log_y2 = H - 12
    log_x1 = 12
    log_x2 = W - 12

    canvas.create_rectangle(log_x1, log_y1, log_x2, log_y2,
                            fill="#111827", outline="#000000", width=3)
    canvas.create_rectangle(log_x1 + 6, log_y1 + 6, log_x2 - 6, log_y2 - 6,
                            fill=PANEL_BG, outline="#9ca3af", width=2)
    canvas.create_rectangle(log_x1 + 8, log_y1 + 8, log_x2 - 8, log_y1 + 28,
                            fill="#e5e7eb", outline="")

    name_text = canvas.create_text(
        log_x1 + 18, log_y1 + 18,
        anchor="w",
        font=PIXEL_FONT,
        fill="#111827",
        text=""
    )

    dialog_text = canvas.create_text(
        log_x1 + 18, log_y1 + 36,
        anchor="nw",
        width=(log_x2 - log_x1) - 36,
        font=PIXEL_FONT,
        fill="#111827",
        text=""
    )

    canvas.create_text(
        log_x2 - 90, log_y2 - 26,
        anchor="center",
        font=PIXEL_FONT,
        fill="#111827",
        text="▶ 다음"
    )

    def next_line(_=None):
        global story_idx
        if story_idx < len(story):
            speaker, line = story[story_idx]
            canvas.itemconfig(name_text, text=speaker)
            canvas.itemconfig(dialog_text, text=line)
            story_idx += 1
        else:
            hub_mode()

    next_line()
    canvas.bind("<Button-1>", next_line)
    gs.root.bind("<Return>", next_line)


def hub_mode():
    gs.reset_binds()
    gs.clear_screen()

    frame = tk.Frame(gs.root, bg=ROOT_BG)
    frame.pack(fill="both", expand=True)
    gs.current_screen = frame

    W, H = ROOT_W, ROOT_H

    canvas = tk.Canvas(
        frame, width=W, height=H,
        highlightthickness=0, bg=ROOT_BG
    )
    canvas.pack(expand=True)

    # ==========================
    # 배경: makimaback.png
    # ==========================
    bg_path = os.path.join(IMG_DIR, "makimaback.png")
    if os.path.exists(bg_path):
        bg = Image.open(bg_path).convert("RGBA")
        bg = bg.resize((W, H), Image.NEAREST)
        bg_tk = ImageTk.PhotoImage(bg)
        canvas.create_image(W // 2, H // 2, image=bg_tk, anchor="center")
        canvas.bg = bg_tk
    else:
        canvas.create_rectangle(0, 0, W, H, fill="#020617", outline="")

    # ==========================
    # 상단 상태 텍스트
    # ==========================
    status_text = canvas.create_text(
        W // 2, 50,
        text=f"마키마: 오늘은 무엇부터 할까?  (뽑기권 {gs.ticket_count}장)",
        font=PIXEL_FONT,
        fill="#f9fafb"
    )

    # ==========================
    # 이미지 메뉴 버튼 3개
    # ==========================
    button_configs = [
        {"img": "stagebutton.png", "label": "스테이지 밀기"},
        {"img": "gachabutton.png", "label": "뽑기"},
        {"img": "friendbutton.png", "label": "동료 보기"}
    ]
    
    btn_infos = []
    button_images = []  # 이미지 참조 유지용
    
    base_y = int(H * 0.8)
    gap = int(W * 0.25)
    button_size = 100  # 버튼 이미지 크기

    ACCENT = "#facc15"
    TXT_NORMAL = "#cbd5e1"
    TXT_DIM = "#64748b"
    TXT_ACTIVE = "#ffffff"

    # 버튼 이미지 로드 및 배치
    for i, config in enumerate(button_configs):
        cx = W // 2 + int((i - 1) * gap)
        button_path = os.path.join(IMG_DIR, config["img"])
        
        if os.path.exists(button_path):
            # 이미지 로드 및 크기 조정
            btn_img = Image.open(button_path).convert("RGBA")
            btn_img = btn_img.resize((button_size, button_size), Image.NEAREST)
            btn_tk = ImageTk.PhotoImage(btn_img)
            button_images.append(btn_tk)  # 참조 유지
            
            # 버튼 이미지 배치
            btn_id = canvas.create_image(cx, base_y, image=btn_tk, anchor="center")
            
            # 설명 텍스트 (버튼 위에)
            label_y = base_y - button_size // 2 - 20
            label_id = canvas.create_text(
                cx, label_y,
                text=config["label"],
                font=PIXEL_FONT,
                fill=TXT_DIM
            )
            
            btn_infos.append((cx, btn_id, label_id))
        else:
            # 이미지가 없을 경우 대체 텍스트 버튼
            btn_id = canvas.create_text(
                cx, base_y,
                text=config["label"],
                font=PIXEL_FONT,
                fill=TXT_DIM
            )
            label_id = None
            btn_infos.append((cx, btn_id, label_id))
    
    # 화살표 표시
    arrow_id = canvas.create_text(
        btn_infos[0][0], base_y + button_size // 2 + 18,
        text="▲",
        font=("Courier New", 18, "bold"),
        fill=ACCENT
    )
    
    # 이미지 참조 유지
    canvas.button_images = button_images

    selected = 0
    hovered = -1

    def set_button_style(i, active=False, hover=False):
        cx, btn_id, label_id = btn_infos[i]
        
        if label_id:
            if active:
                canvas.itemconfig(label_id, fill=TXT_ACTIVE)
            elif hover:
                canvas.itemconfig(label_id, fill=TXT_NORMAL)
            else:
                canvas.itemconfig(label_id, fill=TXT_DIM)

    def update_selection():
        for i in range(len(btn_infos)):
            set_button_style(i, active=(i == selected), hover=(i == hovered))
        canvas.coords(arrow_id, btn_infos[selected][0], base_y + button_size // 2 + 18)

        canvas.itemconfig(
            status_text,
            text=f"마키마: 오늘은 무엇부터 할까?  (뽑기권 {gs.ticket_count}장)"
        )

    def safe_call(mod, candidates):
        for name in candidates:
            if hasattr(mod, name):
                getattr(mod, name)()
                return True
        return False

    def execute_choice():
        nonlocal selected

        if selected == 0:
            ok = safe_call(stage, ["world_map", "world_map_mode", "stage_mode", "stage_select"])
            if not ok:
                canvas.itemconfig(status_text, text="마키마: 스테이지 화면 함수명을 못 찾았어 (stage 모듈 확인).")
        elif selected == 1:
            ok = safe_call(gacha, ["gacha_mode"])
            if not ok:
                canvas.itemconfig(status_text, text="마키마: gacha_mode()가 없어. gacha.py 확인해줘.")
        else:  # selected == 2
            ok = safe_call(partner, ["allies_room", "partner_room", "partner_mode", "partner_screen"])
            if not ok:
                canvas.itemconfig(status_text, text="마키마: 동료 보기 함수명을 못 찾았어 (partner 모듈 확인).")

    def on_key(e):
        nonlocal selected
        if gs.current_screen is not frame:
            return

        if e.keysym in ("Left", "Up"):
            selected = (selected - 1) % len(btn_infos)
            update_selection()
        elif e.keysym in ("Right", "Down"):
            selected = (selected + 1) % len(btn_infos)
            update_selection()
        elif e.keysym in ("Return", "space"):
            execute_choice()

    gs.root.bind("<Key>", on_key)

    def on_enter(i):
        def _(_e=None):
            nonlocal hovered
            hovered = i
            update_selection()
        return _

    def on_leave(_e=None):
        nonlocal hovered
        hovered = -1
        update_selection()

    def make_click(i):
        def _click(_event=None):
            nonlocal selected
            if gs.current_screen is not frame:
                return
            selected = i
            update_selection()
            execute_choice()
        return _click

    for i, (cx, btn_id, label_id) in enumerate(btn_infos):
        # 버튼 이미지와 라벨에 이벤트 바인딩
        canvas.tag_bind(btn_id, "<Button-1>", make_click(i))
        canvas.tag_bind(btn_id, "<Enter>", on_enter(i))
        canvas.tag_bind(btn_id, "<Leave>", on_leave)
        if label_id:
            canvas.tag_bind(label_id, "<Button-1>", make_click(i))
            canvas.tag_bind(label_id, "<Enter>", on_enter(i))
            canvas.tag_bind(label_id, "<Leave>", on_leave)

    update_selection()


if __name__ == "__main__":
    title_screen()
    gs.root.mainloop()