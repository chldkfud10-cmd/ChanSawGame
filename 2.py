from PIL import Image, ImageTk
import tkinter as tk
import random
import os


# ==========================
# 기본 설정
# ==========================
CANVAS_W = 900
CANVAS_H = 600
IMG_DIR = "img"

# ==========================
# 레트로 스타일 팔레트 & 폰트
# ==========================
PIXEL_TITLE = ("Courier New", 28, "bold")
PIXEL_FONT = ("Courier New", 14, "bold")
PIXEL_SMALL = ("Courier New", 10, "bold")

# 바깥 배경 / 게임 화면 / 패널 색
ROOT_BG = "#111827"      # 전체 배경(진한 남색)
GAME_BG = "#6ba96b"      # 게임 캔버스 기본 초록
GROUND_COLOR = "#3f6b3f" # 바닥
SKY_COLOR = "#90c5ff"    # 하늘
PANEL_BG = "#f4f4f4"     # 패널/대화창
PANEL_BORDER = "#000000"

HP_GREEN = "#00b050"
HP_RED = "#d00030"

ROOT_W = CANVAS_W + 120
ROOT_H = CANVAS_H + 140

# 뽑기권 개수 (전역)
ticket_count = 0

# 스테이지 토벌 여부 (1~4 스테이지)
stage_cleared = {
    1: False,
    2: False,
    3: False,
    4: False
}

# 뽑아서 얻은 동료들 (키: "aki", "power" ...)
allies_obtained = set()

# ==========================
# 초기화
# ==========================
root = tk.Tk()
root.title("Chainsaw Man - Retro Ver")
root.geometry(f"{ROOT_W}x{ROOT_H}")

current_screen = None


def clear_screen():
    global current_screen
    if current_screen:
        current_screen.destroy()


# ==========================
# 타이틀 화면
# ==========================
def title_screen():
    global current_screen
    clear_screen()

    frame = tk.Frame(root, bg=ROOT_BG)
    frame.pack(fill="both", expand=True)
    current_screen = frame

    canvas = tk.Canvas(frame, width=ROOT_W, height=ROOT_H,
                       highlightthickness=0, bg=ROOT_BG)
    canvas.pack(expand=True)

    # 배경
    bg_path = os.path.join(IMG_DIR, "back2.png")
    if os.path.exists(bg_path):
        bg_img = Image.open(bg_path).convert("RGBA")
        bg_img = bg_img.resize((ROOT_W, ROOT_H), Image.NEAREST)
        bg_tk = ImageTk.PhotoImage(bg_img)
        canvas.create_image(ROOT_W//2, ROOT_H//2,
                            image=bg_tk, anchor="center")
        canvas.bg = bg_tk
    else:
        canvas.configure(bg=ROOT_BG)

    # 로고 크기 맞추기
    def fit(img, w, h):
        iw, ih = img.size
        scale = min(w/iw, h/ih, 1)
        return img.resize((int(iw*scale), int(ih*scale)), Image.NEAREST)

    # 로고
    logo_id = None
    logo_path = os.path.join(IMG_DIR, "logo.png")
    if os.path.exists(logo_path):
        logo_img = Image.open(logo_path).convert("RGBA")
        logo_img = fit(logo_img, 520, 220)
        logo_tk = ImageTk.PhotoImage(logo_img)
        logo_id = canvas.create_image(
            ROOT_W//2, 150,
            image=logo_tk,
            anchor="center"
        )
        canvas.logo = logo_tk
        canvas.logo_id = logo_id

    # 로고 깜빡이기
    def blink_logo(visible=True):
        if current_screen is not frame:
            return
        if logo_id is not None:
            canvas.itemconfigure(
                logo_id,
                state="hidden" if visible else "normal"
            )
        root.after(500, blink_logo, not visible)

    if logo_id is not None:
        blink_logo(True)

    # ARE YOU READY?
    title_font = ("Courier New", 34, "bold")
    choice_font = ("Courier New", 24, "bold")
    arrow_font = ("Courier New", 24, "bold")

    msg = "ARE YOU READY?"
    tx = ROOT_W // 2
    ty = 280

    for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        canvas.create_text(
            tx + ox, ty + oy,
            text=msg,
            font=title_font,
            fill="#000000"
        )

    canvas.create_text(
        tx, ty,
        text=msg,
        font=title_font,
        fill="#ffffff"
    )

    # YES / NO
    choice_y = 350
    yes_x = ROOT_W//2 - 100
    no_x = ROOT_W//2 + 100

    yes_id = canvas.create_text(
        yes_x, choice_y,
        text="YES",
        font=choice_font,
        fill="#ffffff"
    )
    no_id = canvas.create_text(
        no_x, choice_y,
        text="NO",
        font=choice_font,
        fill="#6b7280"
    )

    arrow_y = choice_y
    arrow_id = canvas.create_text(
        yes_x - 45, arrow_y,
        text="▶",
        font=arrow_font,
        fill="#facc15"
    )

    selected = 0

    def update_selection():
        if selected == 0:
            canvas.itemconfig(yes_id, fill="#ffffff")
            canvas.itemconfig(no_id, fill="#6b7280")
            canvas.coords(arrow_id, yes_x - 45, arrow_y)
        else:
            canvas.itemconfig(yes_id, fill="#6b7280")
            canvas.itemconfig(no_id, fill="#ffffff")
            canvas.coords(arrow_id, no_x - 45, arrow_y)

    def on_key(e):
        nonlocal selected
        if current_screen is not frame:
            return

        if e.keysym in ("Left", "Right", "Up", "Down"):
            selected = 1 - selected
            update_selection()
        elif e.keysym in ("Return", "space"):
            if selected == 0:
                story_mode()
            else:
                root.quit()

    root.bind("<Key>", on_key)

    def click_yes(event):
        story_mode()

    def click_no(event):
        root.quit()

    canvas.tag_bind(yes_id, "<Button-1>", click_yes)
    canvas.tag_bind(no_id, "<Button-1>", click_no)

    update_selection()


# ==========================
# 스토리 (한글 대사)
# ==========================
story = [
    ("마키마", "이름은?"),
    ("덴지", "덴지......"),
    ("마키마", "그래, 덴지  군. 넌 오늘부터 내 사람이야."),
    ("마키마", "덴지 군, 날 위해서 모든 악마들을 죽여줘. 이건 계약이야.")
]
story_index = 0


def story_mode():
    global current_screen, story_index
    clear_screen()
    story_index = 0

    frame = tk.Frame(root, bg=ROOT_BG)
    frame.pack(fill="both", expand=True)
    current_screen = frame

    canvas = tk.Canvas(frame, width=CANVAS_W, height=CANVAS_H,
                       bg=GAME_BG, highlightthickness=4,
                       highlightbackground=PANEL_BORDER)
    canvas.pack(pady=20)

    # ==== 창고 배경 ====
    ground_y = int(CANVAS_H * 0.72)

    canvas.create_rectangle(0, 0, CANVAS_W, ground_y,
                            fill="#82aeea", outline="")

    canvas.create_polygon(
        -40, ground_y-40,
        120, ground_y-90,
        260, ground_y-50,
        400, ground_y-100,
        560, ground_y-60,
        CANVAS_W+40, ground_y-80,
        CANVAS_W+40, ground_y,
        -40, ground_y,
        fill="#4b5563", outline=""
    )

    canvas.create_polygon(
        0, 0,
        int(CANVAS_W * 0.28), 0,
        int(CANVAS_W * 0.18), CANVAS_H,
        0, CANVAS_H,
        fill="#020617", outline=""
    )

    wh_left = int(CANVAS_W * 0.42)
    wh_right = CANVAS_W - 30
    wh_bottom = ground_y + 10
    wh_top = ground_y - 140

    canvas.create_rectangle(wh_left, wh_top, wh_right, wh_bottom,
                            fill="#8a4f32", outline="#4b2b1f")

    stripe_w = 8
    x = wh_left
    toggle = 0
    while x < wh_right:
        color = "#b8734b" if toggle % 2 == 0 else "#a66640"
        canvas.create_rectangle(x, wh_top, x+stripe_w, wh_bottom,
                                fill=color, outline="")
        toggle += 1
        x += stripe_w

    canvas.create_rectangle(wh_left+20, wh_top+10, wh_left+140, wh_top+40,
                            fill="#e5dccf", outline="", stipple="gray50")
    canvas.create_rectangle(wh_right-160, wh_top+25, wh_right-20, wh_top+55,
                            fill="#d3c3b0", outline="", stipple="gray50")

    door_w = 140
    door_h = 70
    door_left = wh_left + (wh_right - wh_left)//2 - door_w//2
    door_right = door_left + door_w
    door_bottom = ground_y + 4
    door_top = door_bottom - door_h

    canvas.create_rectangle(door_left-4, door_top-18, door_right+4, door_top,
                            fill="#e5e7eb", outline="#9ca3af")
    canvas.create_rectangle(door_left, door_top, door_right, door_bottom,
                            fill="#020617", outline="#020617")

    pillar_x = wh_right - 22
    canvas.create_rectangle(pillar_x, wh_top, pillar_x+8, wh_bottom,
                            fill="#5b4330", outline="#2b1f18")
    for y in range(wh_top+10, wh_bottom-20, 30):
        canvas.create_line(pillar_x, y, pillar_x+8, y+20,
                           fill="#2b1f18", width=2)
        canvas.create_line(pillar_x+8, y, pillar_x, y+20,
                           fill="#2b1f18", width=2)

    fence_top = ground_y - 60
    fence_bottom = ground_y
    fence_left = wh_left - 110
    fence_right = wh_left - 10
    canvas.create_rectangle(fence_left, fence_top, fence_right, fence_bottom,
                            fill="#374151", outline="#111827")

    step = 10
    for x in range(fence_left+step, fence_right, step):
        canvas.create_line(x, fence_top, x, fence_bottom,
                           fill="#9ca3af")
    for y in range(fence_top+step, fence_bottom, step):
        canvas.create_line(fence_left, y, fence_right, y,
                           fill="#9ca3af")

    canvas.create_polygon(
        fence_left+8, fence_bottom-8,
        fence_left+40, fence_bottom-40,
        fence_left+90, fence_bottom-25,
        fence_left+70, fence_bottom-8,
        fill="#6b7280", outline="#111827"
    )

    canvas.create_rectangle(0, ground_y, CANVAS_W, CANVAS_H,
                            fill="#7c7c7c", outline="#4b4b4b")

    import random as _rnd
    for _ in range(220):
        gx = _rnd.randint(0, CANVAS_W)
        gy = _rnd.randint(ground_y, CANVAS_H)
        r = _rnd.randint(1, 3)
        col = _rnd.choice(["#5f5f5f", "#9a9a9a", "#646464", "#858585"])
        canvas.create_oval(gx-r, gy-r, gx+r, gy+r,
                           fill=col, outline="")

    # 덴지 / 마키마
    def fit_soft(path, w, h):
        img = Image.open(path).convert("RGBA")
        iw, ih = img.size
        scale = min(w / iw, h / ih)
        new_size = (int(iw * scale), int(ih * scale))
        return img.resize(new_size, Image.LANCZOS)

    denji_p = os.path.join(IMG_DIR, "denji1.png")
    makima_p = os.path.join(IMG_DIR, "makima1.png")

    if os.path.exists(denji_p):
        denji_img = fit_soft(denji_p, 240, 300)
    else:
        denji_img = Image.new("RGBA", (140, 200), (200, 200, 200, 255))

    if os.path.exists(makima_p):
        makima_img = fit_soft(makima_p, 240, 300)
    else:
        makima_img = Image.new("RGBA", (140, 200), (180, 120, 200, 255))

    denji_tk = ImageTk.PhotoImage(denji_img)
    makima_tk = ImageTk.PhotoImage(makima_img)

    denji_x = int(CANVAS_W * 0.25)
    makima_x = int(CANVAS_W * 0.75)
    char_y = int(CANVAS_H * 0.62)

    canvas.create_image(denji_x, char_y, image=denji_tk)
    canvas.create_image(makima_x, char_y, image=makima_tk)

    canvas.denji = denji_tk
    canvas.makima = makima_tk

    # 대화창
    log_y1 = CANVAS_H - 140
    log_y2 = CANVAS_H - 12
    log_x1 = 12
    log_x2 = CANVAS_W - 12

    canvas.create_rectangle(log_x1, log_y1, log_x2, log_y2,
                            fill="#111827", outline="#000000", width=3)
    canvas.create_rectangle(log_x1+6, log_y1+6, log_x2-6, log_y2-6,
                            fill=PANEL_BG, outline="#9ca3af", width=2)
    canvas.create_rectangle(log_x1+8, log_y1+8, log_x2-8, log_y1+28,
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

    next_text_id = canvas.create_text(
        log_x2 - 80, log_y2 - 26,
        anchor="center",
        font=PIXEL_FONT,
        fill="#111827",
        text="▶ 다음"
    )

    # 스토리 진행
    def show_line():
        if story_index < len(story):
            speaker, line = story[story_index]
            canvas.itemconfig(name_text, text=speaker)
            canvas.itemconfig(dialog_text, text=line)
        else:
            hub_mode()   # 스토리 끝나면 메인 허브로

    def next_story(event=None):
        global story_index
        if story_index < len(story):
            show_line()
            story_index += 1
        else:
            hub_mode()

    next_story()

    def on_click_next(event):
        next_story()

    canvas.tag_bind(next_text_id, "<Button-1>", on_click_next)

    def on_key(e):
        if current_screen is not frame:
            return
        if e.keysym in ("Return", "space"):
            next_story()

    root.bind("<Key>", on_key)


# ==========================
# 마키마 메인 허브 화면
# ==========================
def hub_mode():
    global current_screen, ticket_count
    clear_screen()

    frame = tk.Frame(root, bg=ROOT_BG)
    frame.pack(fill="both", expand=True)
    current_screen = frame

    canvas = tk.Canvas(frame, width=CANVAS_W, height=CANVAS_H,
                       bg="#020617", highlightthickness=4,
                       highlightbackground=PANEL_BORDER)
    canvas.pack(pady=20)

    # 배경 그리드
    grid_step = 40
    for x in range(0, CANVAS_W, grid_step):
        canvas.create_line(x, 0, x, CANVAS_H, fill="#111827")
    for y in range(0, CANVAS_H, grid_step):
        canvas.create_line(0, y, CANVAS_W, y, fill="#111827")

    # 상단 텍스트 (뽑기권 표시)
    status_text = canvas.create_text(
        CANVAS_W//2, 40,
        text=f"마키마: 오늘은 무엇부터 할까?  (뽑기권 {ticket_count}장)",
        font=PIXEL_FONT,
        fill="#f9fafb"
    )

    # 마키마2 이미지 중앙 배치
    def fit_soft(path, w, h):
        img = Image.open(path).convert("RGBA")
        iw, ih = img.size
        scale = min(w / iw, h / ih)
        new_size = (int(iw * scale), int(ih * scale))
        return img.resize(new_size, Image.LANCZOS)

    makima2_p = os.path.join(IMG_DIR, "makima2.png")
    if os.path.exists(makima2_p):
        makima2_img = fit_soft(makima2_p, 260, 320)
    else:
        makima2_img = Image.new("RGBA", (180, 260), (180, 120, 200, 255))

    makima2_tk = ImageTk.PhotoImage(makima2_img)
    canvas.makima2 = makima2_tk

    canvas.create_image(
        CANVAS_W//2, CANVAS_H//2 - 20,
        image=makima2_tk
    )

    # 메뉴 버튼 4개
    labels = ["스테이지 밀기", "뽑기", "동료 보기", "저장"]
    btn_infos = []
    base_y = CANVAS_H - 70

    for i, text in enumerate(labels):
        # 4개를 가운데 기준으로 배치
        cx = CANVAS_W//2 + int((i - 1.5) * 150)
        rect = canvas.create_rectangle(
            cx-80, base_y-24,
            cx+80, base_y+24,
            fill="#1f2937", outline="#4b5563", width=2
        )
        txt = canvas.create_text(
            cx, base_y,
            text=text,
            font=PIXEL_FONT,
            fill="#f9fafb"
        )
        btn_infos.append((cx, rect, txt))

    arrow_id = canvas.create_text(
        btn_infos[0][0], base_y+30,
        text="▲",
        font=("Courier New", 18, "bold"),
        fill="#facc15"
    )

    selected = 0

    def update_selection():
        for i, (cx, rect, txt) in enumerate(btn_infos):
            if i == selected:
                canvas.itemconfig(rect, outline="#facc15")
            else:
                canvas.itemconfig(rect, outline="#4b5563")
        canvas.coords(arrow_id, btn_infos[selected][0], base_y+30)

    def execute_choice():
        nonlocal selected
        if selected == 0:
            world_map()
        elif selected == 1:
            gacha_mode()
        elif selected == 2:
            allies_room()
        else:
            canvas.itemconfig(
                status_text,
                text="마키마: 저장 기능은 아직 준비 중이야."
            )

    # 키 입력
    def on_key(e):
        nonlocal selected
        if current_screen is not frame:
            return

        if e.keysym in ("Left", "a", "A"):
            selected = (selected - 1) % len(labels)
            update_selection()
        elif e.keysym in ("Right", "d", "D"):
            selected = (selected + 1) % len(labels)
            update_selection()
        elif e.keysym in ("Return", "space"):
            execute_choice()

    root.bind("<Key>", on_key)

    # 마우스 클릭
    def make_click_handler(idx):
        def handler(event):
            nonlocal selected
            selected = idx
            update_selection()
            execute_choice()
        return handler

    for i, (_, rect, txt) in enumerate(btn_infos):
        canvas.tag_bind(rect, "<Button-1>", make_click_handler(i))
        canvas.tag_bind(txt, "<Button-1>", make_click_handler(i))

    update_selection()

def world_map():
    global current_screen, stage_cleared
    clear_screen()

    frame = tk.Frame(root, bg=ROOT_BG)
    frame.pack(fill="both", expand=True)
    current_screen = frame

    canvas = tk.Canvas(frame, width=CANVAS_W, height=CANVAS_H,
                       bg="#1b1b28", highlightthickness=4,
                       highlightbackground=PANEL_BORDER)
    canvas.pack(pady=20)

    # ===== 도쿄 맵 배경 =====
    bg_path = os.path.join(IMG_DIR, "tokyo_bg.png")
    if os.path.exists(bg_path):
        bg_img = Image.open(bg_path).convert("RGBA")
        bg_img = bg_img.resize((CANVAS_W, CANVAS_H), Image.NEAREST)
        bg_tk = ImageTk.PhotoImage(bg_img)
        canvas.create_image(CANVAS_W//2, CANVAS_H//2, image=bg_tk)
        canvas.bg = bg_tk
    else:
        # 간단한 도시 실루엣
        canvas.create_rectangle(0, CANVAS_H*0.55, CANVAS_W, CANVAS_H,
                                fill="#050511", outline="")
        import random as _rnd
        for _ in range(25):
            w = _rnd.randint(40, 90)
            h = _rnd.randint(80, 200)
            x = _rnd.randint(0, CANVAS_W - w)
            canvas.create_rectangle(x, CANVAS_H-h, x+w, CANVAS_H,
                                    fill="#222533", outline="#000000")

    # 안내 텍스트
    info_text = canvas.create_text(
        CANVAS_W//2, 40,
        text="도쿄 맵: 스테이지를 선택해줘.",
        font=PIXEL_FONT,
        fill="#f9fafb"
    )

    # 스테이지 해금 규칙
    def is_stage_unlocked(stage_id):
        if stage_id == 1:
            return True
        if stage_id == 2:
            return stage_cleared.get(1, False)   # 🔥 1번 클리어 시 2번 개방
        # 3,4는 나중에…
        return False

    # ===== 원형 스테이지 버튼 4개 =====
    circle_positions = [
        (160, 190),  # 1
        (520, 150),  # 2
        (260, 290),  # 3
        (440, 260),  # 4
    ]

    circle_info = []   # (stage_id, circle_id, text_id, label_id)
    blink_targets = [] # 깜빡일 원들 (이동 가능 + 아직 미토벌)

    for i, (cx, cy) in enumerate(circle_positions):
        stage_id = i + 1
        r = 35

        cleared = stage_cleared.get(stage_id, False)
        unlocked = is_stage_unlocked(stage_id)

        # 색/라벨 결정
        if cleared:
            fill_color = "#4b5563"   # 회색 (클리어)
            outline_color = "#9ca3af"
        else:
            if unlocked:
                # 이동 가능 스테이지
                fill_color = "#f97316" if stage_id == 1 else "#3b82f6"
            else:
                fill_color = "#374151"  # 잠김
            outline_color = "#ffffff"

        c = canvas.create_oval(
            cx-r, cy-r, cx+r, cy+r,
            fill=fill_color, outline=outline_color, width=3
        )

        # 안쪽 아이콘/번호
        if cleared:
            t = canvas.create_text(cx, cy,
                                   text="✓",
                                   font=("Courier New", 20, "bold"),
                                   fill="#ffffff")
            label_txt = "토벌 완료"
            label_color = "#a5b4fc"
        else:
            if stage_id == 1:
                t_text = "1"
                label_txt = "토마토의 악마"
                label_color = "#fee2e2" if unlocked else "#9ca3af"
            elif stage_id == 2:
                t_text = "2"
                label_txt = "2번 스테이지"
                label_color = "#bfdbfe" if unlocked else "#9ca3af"
            else:
                t_text = str(stage_id)
                label_txt = "잠김"
                label_color = "#9ca3af"

            t = canvas.create_text(cx, cy,
                                   text=t_text,
                                   font=("Courier New", 20, "bold"),
                                   fill="#ffffff")

        label_id = canvas.create_text(
            cx, cy + 45,
            text=label_txt,
            font=PIXEL_SMALL,
            fill=label_color
        )

        circle_info.append((stage_id, c, t, label_id))

        # 🔥 이동 가능 & 미토벌 스테이지만 깜빡임 대상
        if unlocked and (not cleared):
            blink_targets.append(c)

    # 🔔 깜빡이기 애니메이션
    def blink(step=0, visible=True):
        if current_screen is not frame:
            return
        for cid in blink_targets:
            canvas.itemconfigure(
                cid,
                state="normal" if visible else "hidden"
            )
        root.after(450, lambda: blink(step+1, not visible))

    if blink_targets:
        blink()

    # 클릭 핸들러
    def make_click(stage_id):
        def handler(event):
            cleared = stage_cleared.get(stage_id, False)
            unlocked = is_stage_unlocked(stage_id)

            if cleared:
                canvas.itemconfig(
                    info_text,
                    text="이미 토벌 완료된 스테이지야."
                )
                return

            if not unlocked:
                canvas.itemconfig(
                    info_text,
                    text="아직 개방되지 않은 스테이지야."
                )
                return

            # 🔥 실제 진입
            if stage_id == 1:
                battle_mode()
            elif stage_id == 2:
                canvas.itemconfig(
                    info_text,
                    text="2번 스테이지는 아직 준비 중이야!"
                )
            else:
                canvas.itemconfig(
                    info_text,
                    text="이 스테이지는 아직 준비 중이야."
                )
        return handler

    for (stage_id, c, t, label_id) in circle_info:
        canvas.tag_bind(c, "<Button-1>", make_click(stage_id))
        canvas.tag_bind(t, "<Button-1>", make_click(stage_id))
        canvas.tag_bind(label_id, "<Button-1>", make_click(stage_id))

    # 마키마에게 돌아가기 버튼
    back_btn = tk.Button(
        frame,
        text="← 마키마에게",
        font=PIXEL_FONT,
        relief="solid", bd=3,
        bg="#111827", fg="#f9fafb",
        activebackground="#1f2937",
        command=hub_mode
    )
    back_btn.pack(anchor="nw", padx=20, pady=(5, 0))

# ==========================
# 뽑기 화면
# ==========================
def gacha_mode():
    global current_screen, ticket_count, allies_obtained
    clear_screen()

    frame = tk.Frame(root, bg=ROOT_BG)
    frame.pack(fill="both", expand=True)
    current_screen = frame

    # 상단 뒤로가기 버튼
    back_btn = tk.Button(
        frame,
        text="← 마키마에게",
        font=PIXEL_FONT,
        relief="solid", bd=3,
        bg="#111827", fg="#f9fafb",
        activebackground="#1f2937",
        command=hub_mode
    )
    back_btn.pack(anchor="nw", padx=20, pady=(20, 0))

    canvas = tk.Canvas(frame, width=CANVAS_W, height=CANVAS_H,
                       bg="#020617", highlightthickness=4,
                       highlightbackground=PANEL_BORDER)
    canvas.pack(pady=10)

    # 배경 그리드
    grid_step = 40
    for x in range(0, CANVAS_W, grid_step):
        canvas.create_line(x, 0, x, CANVAS_H, fill="#111827")
    for y in range(0, CANVAS_H, grid_step):
        canvas.create_line(0, y, CANVAS_W, y, fill="#111827")

    # 안내 텍스트 + 뽑기권 표시
    info_text = canvas.create_text(
        CANVAS_W//2, 40,
        text="마키마: 뽑기권으로 동료를 뽑아봐.",
        font=PIXEL_FONT,
        fill="#f9fafb"
    )

    ticket_text = canvas.create_text(
        CANVAS_W - 110, 30,
        text=f"뽑기권: {ticket_count}장",
        font=PIXEL_FONT,
        fill="#e5e7eb"
    )

    def update_ticket_text():
        canvas.itemconfig(ticket_text, text=f"뽑기권: {ticket_count}장")

    # 결과 표시 영역
    canvas.create_rectangle(
        80, 80, CANVAS_W-80, CANVAS_H-80,
        outline="#4b5563", width=3, fill="#020617"
    )

    result_text = canvas.create_text(
        CANVAS_W//2, CANVAS_H-90,
        text="\"뽑기!\" 버튼을 눌러봐.",
        font=PIXEL_FONT,
        fill="#e5e7eb"
    )

    canvas.result_tk = None
    result_img_id = None

    def fit_soft(path, w, h):
        img = Image.open(path).convert("RGBA")
        iw, ih = img.size
        scale = min(w / iw, h / ih)
        new_size = (int(iw * scale), int(ih * scale))
        return img.resize(new_size, Image.LANCZOS)

    def do_draw():
        nonlocal result_img_id
        global ticket_count, allies_obtained

        if ticket_count <= 0:
            canvas.itemconfig(
                info_text,
                text="마키마: 뽑기권이 없네. 다시 악마를 쓰러뜨리고 와."
            )
            return

        # 뽑기권 1장 소비
        ticket_count -= 1
        update_ticket_text()

        # 랜덤 캐릭터 선택
        choice = random.choice(["aki", "power"])
        if choice == "aki":
            path = os.path.join(IMG_DIR, "aki1.png")
            label = "아키가 나타났다!"
        else:
            path = os.path.join(IMG_DIR, "power1.png")
            label = "파워가 나타났다!"

        # 동료 획득 기록
        allies_obtained.add(choice)

        if os.path.exists(path):
            img = fit_soft(path, 260, 320)
        else:
            # 대체 이미지
            color = (80, 160, 220, 255) if choice == "aki" else (220, 120, 180, 255)
            img = Image.new("RGBA", (180, 260), color)

        tkimg = ImageTk.PhotoImage(img)
        canvas.result_tk = tkimg  # GC 방지

        if result_img_id is None:
            result_img_id = canvas.create_image(
                CANVAS_W//2, CANVAS_H//2,
                image=tkimg
            )
        else:
            canvas.itemconfig(result_img_id, image=tkimg)

        # 이미 있던 동료인지 체크
        if choice == "aki":
            name_kor = "아키"
        else:
            name_kor = "파워"

        if len([a for a in allies_obtained if a == choice]) > 1:
            extra = " (중복 획득)"
        else:
            extra = ""

        canvas.itemconfig(info_text, text=f"마키마: {label}{extra}")
        canvas.itemconfig(result_text, text="또 뽑고 싶으면 한 번 더 눌러봐.")

    # 실제 뽑기 버튼 (화면 아래)
    draw_btn = tk.Button(
        frame,
        text="뽑기!",
        font=PIXEL_TITLE,
        relief="solid", bd=4,
        bg="#10b981", fg="#000000",
        activebackground="#34d399",
        command=do_draw
    )
    draw_btn.pack(pady=10)

def allies_room():
    global current_screen, allies_obtained
    clear_screen()

    frame = tk.Frame(root, bg=ROOT_BG)
    frame.pack(fill="both", expand=True)
    current_screen = frame

    title = tk.Label(
        frame,
        text="덴지의 동료들",
        font=PIXEL_TITLE,
        bg=ROOT_BG,
        fg="#fbbf24"
    )
    title.pack(pady=20)

    # 뒤로가기 버튼
    back_btn = tk.Button(
        frame,
        text="← 마키마에게",
        font=PIXEL_FONT,
        relief="solid", bd=3,
        bg="#111827", fg="#f9fafb",
        activebackground="#1f2937",
        command=hub_mode
    )
    back_btn.pack(anchor="nw", padx=20)

    canvas = tk.Canvas(
        frame,
        width=CANVAS_W,
        height=CANVAS_H,
        bg="#020617",
        highlightthickness=4,
        highlightbackground=PANEL_BORDER
    )
    canvas.pack(pady=10)

    # 슬롯 정의 (필요하면 더 추가 가능)
    ally_defs = [
        ("aki", "아키", "aki1.png"),
        ("power", "파워", "power1.png"),
    ]

    slots_x = [CANVAS_W//3, 2*CANVAS_W//3]
    y = CANVAS_H//2

    canvas.ally_imgs = []  # 이미지 참조 유지용

    for i, (key, name_kor, filename) in enumerate(ally_defs):
        cx = slots_x[i]
        cy = y

        # 카드 배경
        card = canvas.create_rectangle(
            cx-110, cy-140, cx+110, cy+140,
            fill="#111827", outline="#4b5563", width=3
        )

        has_ally = key in allies_obtained

        # 이미지 영역
        img_path = os.path.join(IMG_DIR, filename)
        if has_ally and os.path.exists(img_path):
            img = Image.open(img_path).convert("RGBA")
            iw, ih = img.size
            scale = min(180/iw, 150/ih)
            img = img.resize((int(iw*scale), int(ih*scale)), Image.LANCZOS)
        else:
            # 잠금 상태 실루엣/빈 칸
            img = Image.new("RGBA", (160, 130),
                            (30, 30, 40, 255))

        tkimg = ImageTk.PhotoImage(img)
        canvas.ally_imgs.append(tkimg)

        canvas.create_image(cx, cy-20, image=tkimg)

        # 이름
        canvas.create_text(
            cx, cy+80,
            text=name_kor,
            font=PIXEL_FONT,
            fill="#e5e7eb"
        )

        # 상태 텍스트
        status_text = "획득 완료" if has_ally else "미획득"
        status_color = "#34d399" if has_ally else "#9ca3af"

        canvas.create_text(
            cx, cy+110,
            text=status_text,
            font=PIXEL_SMALL,
            fill=status_color
        )

# ==========================
# 전투
# ==========================
def battle_mode():
    global current_screen, ticket_count
    clear_screen()

    frame = tk.Frame(root, bg=ROOT_BG)
    frame.pack(fill="both", expand=True)
    current_screen = frame

    # =====================
    # 기본 전투 스탯
    # =====================
    player_hp = tk.IntVar(value=100)

    # ✅ 보스는 나중에 등장하므로, 처음엔 0으로 시작
    enemy_hp = tk.IntVar(value=0)

    PLAYER_MAX = 100
    ENEMY_MAX = 80

    # ✅ 쫄몹(토마토) 총 체력(= 개수 * 각 체력)
    MOB_COUNT = 5
    MOB_HP_EACH = 2
    mob_total_hp = tk.IntVar(value=MOB_COUNT * MOB_HP_EACH)
    MOB_TOTAL_MAX = MOB_COUNT * MOB_HP_EACH

    tk.Label(frame, text="전투 시작!  (가로 슈팅 모드)",
             font=PIXEL_FONT, bg=ROOT_BG, fg="#e5e7eb").pack(pady=8)

    canvas = tk.Canvas(frame, width=CANVAS_W, height=CANVAS_H,
                       bg=GAME_BG, highlightthickness=4,
                       highlightbackground=PANEL_BORDER)
    canvas.pack()

    # =====================
    # 배경
    # =====================
    ground_y = CANVAS_H - 80
    canvas.create_rectangle(0, 0, CANVAS_W, ground_y,
                            fill=SKY_COLOR, outline=SKY_COLOR)
    canvas.create_rectangle(0, ground_y, CANVAS_W, CANVAS_H,
                            fill=GROUND_COLOR, outline=GROUND_COLOR)

    # =====================
    # 스프라이트 로드
    # =====================
    def fit(path, w, h):
        img = Image.open(path).convert("RGBA")
        iw, ih = img.size
        scale = min(w / iw, h / ih, 1)
        return img.resize((int(iw * scale), int(ih * scale)), Image.NEAREST)

    denji_p = os.path.join(IMG_DIR, "denji2.png")
    devil_p = os.path.join(IMG_DIR, "devil1.png")
    tomato_p = os.path.join(IMG_DIR, "tomato.png")          # 잡몹
    tomatobomb_p = os.path.join(IMG_DIR, "tomatobomb.png")  # 적 탄
    denjibomb_p = os.path.join(IMG_DIR, "denjibomb.png")    # ✅ 덴지 탄

    if os.path.exists(denji_p):
        denji_img = fit(denji_p, 140, 180)
    else:
        denji_img = Image.new("RGBA", (140, 200), (200, 200, 200, 255))

    if os.path.exists(devil_p):
        devil_img = fit(devil_p, 260, 220)
    else:
        devil_img = Image.new("RGBA", (220, 220), (180, 50, 50, 255))

    denji_tk = ImageTk.PhotoImage(denji_img)
    devil_tk = ImageTk.PhotoImage(devil_img)

    # ✅ 적 폭탄(토마토탄) 크기
    BOMB_SIZE = 44
    bomb_tk = None
    if os.path.exists(tomatobomb_p):
        bomb_img = fit(tomatobomb_p, BOMB_SIZE, BOMB_SIZE)
        bomb_tk = ImageTk.PhotoImage(bomb_img)

    # ✅ 덴지 폭탄(덴지탄) 크기 (여기만 키우면 덴지 탄만 커짐)
    DENJI_BOMB_SIZE = 60   # <- 원하는 크기로 조절
    denji_bomb_tk = None
    if os.path.exists(denjibomb_p):
        denji_bomb_img = fit(denjibomb_p, DENJI_BOMB_SIZE, DENJI_BOMB_SIZE)
        denji_bomb_tk = ImageTk.PhotoImage(denji_bomb_img)


    # =====================
    # 위치 (가로 슈팅)
    # =====================
    denji_x = 140
    denji_y = CANVAS_H // 2
    denji_id = canvas.create_image(denji_x, denji_y, image=denji_tk)

    # ✅ 보스는 처음엔 생성하지 않음
    boss_active = False
    devil_id = None

    # ✅ 보스 위치를 "조금 더 오른쪽"으로
    devil_x = CANVAS_W - 150
    devil_y = CANVAS_H // 2

    canvas.denji = denji_tk
    canvas.devil = devil_tk
    canvas.bomb = bomb_tk           # GC 방지
    canvas.denji_bomb = denji_bomb_tk  # ✅ GC 방지

    # =====================
    # HP 패널
    # =====================
    PANEL_W = 210
    PANEL_H = 56
    HP_BAR_W = 95
    HP_BAR_H = 10

    def make_status_panel(x1, y1, name, max_hp, hp_var):
        x2 = x1 + PANEL_W
        y2 = y1 + PANEL_H

        canvas.create_rectangle(x1+3, y1+3, x2+3, y2+3,
                                fill="#4b5563", outline="")
        canvas.create_rectangle(x1, y1, x2, y2,
                                fill="#d1d5db", outline="#111827", width=2)

        inner_x1 = x1 + 5
        inner_y1 = y1 + 5
        inner_x2 = x2 - 5
        inner_y2 = y2 - 5
        canvas.create_rectangle(inner_x1, inner_y1, inner_x2, inner_y2,
                                fill="#e5e7eb", outline="#9ca3af")

        name_y = inner_y1 + 14
        name_id = canvas.create_text(inner_x1 + 8, name_y,
                                     text=name, anchor="w",
                                     font=PIXEL_FONT, fill="#111827")

        hp_row_y = inner_y1 + 34
        hp_label_x = inner_x1 + 8
        canvas.create_text(hp_label_x, hp_row_y,
                           text="HP:",
                           anchor="w", font=PIXEL_SMALL, fill="#f97316")

        hp_bg_x1 = hp_label_x + 30
        hp_bg_y1 = hp_row_y - HP_BAR_H//2
        hp_bg_x2 = hp_bg_x1 + HP_BAR_W
        hp_bg_y2 = hp_bg_y1 + HP_BAR_H

        canvas.create_rectangle(
            hp_bg_x1, hp_bg_y1, hp_bg_x2, hp_bg_y2,
            fill="#9ca3af", outline="#111827"
        )

        hp_rect = canvas.create_rectangle(
            hp_bg_x1, hp_bg_y1, hp_bg_x2, hp_bg_y2,
            fill=HP_GREEN, outline="#111827"
        )

        hp_text = canvas.create_text(
            hp_bg_x2 + 8, hp_row_y,
            anchor="w", font=PIXEL_SMALL,
            fill="#111827",
            text=f"{hp_var.get()}/{max_hp}"
        )

        return {
            "name_id": name_id,
            "rect": hp_rect,
            "x1": hp_bg_x1,
            "y1": hp_bg_y1,
            "x2": hp_bg_x2,
            "y2": hp_bg_y2,
            "hp_text": hp_text,
            "max_hp": max_hp,
            "var": hp_var
        }

    player_panel = make_status_panel(30, 20, "덴지", PLAYER_MAX, player_hp)

    # ✅ 처음엔 "토마토 부하" 체력(총합) 표시
    enemy_panel = make_status_panel(
        CANVAS_W - PANEL_W - 30, 20,
        "토마토 부하", MOB_TOTAL_MAX, mob_total_hp
    )

    def update_single_bar(panel_info):
        hp = panel_info["var"].get()
        max_hp = panel_info["max_hp"]
        ratio = max(0, min(1, hp / max_hp)) if max_hp > 0 else 0

        x1 = panel_info["x1"]
        x2 = panel_info["x2"]
        y1 = panel_info["y1"]
        y2 = panel_info["y2"]

        canvas.coords(panel_info["rect"],
                      x1, y1,
                      x1 + (x2 - x1) * ratio, y2)

        color = HP_GREEN if ratio > 0.5 else ("#facc15" if ratio > 0.25 else "#ef4444")
        canvas.itemconfig(panel_info["rect"], fill=color)
        canvas.itemconfig(panel_info["hp_text"], text=f"{hp}/{max_hp}")

    def update_bars():
        update_single_bar(player_panel)
        update_single_bar(enemy_panel)

    # ✅ 적 패널을 "보스"로 전환
    def switch_enemy_panel_to_boss():
        enemy_panel["var"] = enemy_hp
        enemy_panel["max_hp"] = ENEMY_MAX
        canvas.itemconfig(enemy_panel["name_id"], text="토마토의 악마")
        update_bars()

    # =====================
    # 아래 메시지창(기본 숨김, 보스 등장 때만 잠깐)
    # =====================
    log_y1 = CANVAS_H - 120
    log_y2 = CANVAS_H - 12
    log_x1 = 12
    log_x2 = CANVAS_W - 12

    canvas.create_rectangle(log_x1, log_y1, log_x2, log_y2,
                            fill="#111827", outline="#000000", width=3, tags="logui")
    canvas.create_rectangle(log_x1+6, log_y1+6, log_x2-6, log_y2-6,
                            fill=PANEL_BG, outline="#9ca3af", width=2, tags="logui")
    canvas.create_rectangle(log_x1+8, log_y1+8, log_x2-8, log_y1+16,
                            fill="#e5e7eb", outline="", tags="logui")

    log = canvas.create_text(
        log_x1+18, log_y1+22,
        anchor="nw", width=(log_x2-log_x1)-36,
        font=PIXEL_FONT,
        text="",
        tags="logui"
    )

    def show_log_ui(msg):
        canvas.itemconfig(log, text=msg)
        canvas.itemconfigure("logui", state="normal")

    def hide_log_ui():
        canvas.itemconfigure("logui", state="hidden")
        canvas.itemconfig(log, text="")

    hide_log_ui()

    # =====================
    # 데미지 이펙트
    # =====================
    def damage_splash(cx, cy, val, color):
        for _ in range(2):
            dx = random.randint(-20, 20)
            dy = random.randint(-10, 10)
            t = canvas.create_text(cx+dx, cy+dy,
                                   text=f"-{val}",
                                   fill=color,
                                   font=("Courier New", 14, "bold"))

            def anim(step=0, tid=t):
                if current_screen is not frame:
                    return
                if step < 14:
                    canvas.move(tid, 0, -2)
                    root.after(40, anim, step+1, tid)
                else:
                    canvas.delete(tid)
            anim()

    # =====================
    # 슈팅 요소
    # =====================
    player_bullets = []
    enemy_bullets = []

    BULLET_SPEED_PLAYER = 12
    BULLET_SPEED_ENEMY = 4

    ENEMY_FIRE_MIN = 900
    ENEMY_FIRE_MAX = 1300

    MOB_FIRE_MIN = 1000
    MOB_FIRE_MAX = 2000
    MOB_FIRE_CHANCE = 0.28

    game_over = False
    pressed_keys = set()
    player_speed = 8

    # =====================
    # 유도 탄 속도 계산
    # =====================
    import math

    def calc_homing_velocity(from_x, from_y, speed, angle_error_deg=0):
        dx = denji_x - from_x
        dy = denji_y - from_y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return 0, 0

        angle = math.atan2(dy, dx)

        if angle_error_deg > 0:
            error = math.radians(random.uniform(-angle_error_deg, angle_error_deg))
            angle += error

        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        return vx, vy

    # =====================
    # 쫄몹(tomato) "<" 배치
    # =====================
    tomatoes = []

    def spawn_line_tomatoes():
        cx = CANVAS_W - 200
        cy = CANVAS_H // 2

        gap = 90
        mid_dx = 75
        left_dx = 155

        mid_x = cx - mid_dx
        left_x = cx - left_dx

        positions = [
            (cx,     cy - 2*gap),
            (mid_x,  cy - gap),
            (left_x, cy),
            (mid_x,  cy + gap),
            (cx,     cy + 2*gap),
        ]

        if not hasattr(canvas, "tomato_imgs"):
            canvas.tomato_imgs = []

        for tx, ty in positions:
            if os.path.exists(tomato_p):
                img = fit(tomato_p, 80, 80)
                tkimg = ImageTk.PhotoImage(img)
                tid = canvas.create_image(tx, ty, image=tkimg)
                canvas.tomato_imgs.append(tkimg)
                radius = 26
                is_image = True
            else:
                r = 18
                tid = canvas.create_oval(
                    tx-r, ty-r, tx+r, ty+r,
                    fill="#ef4444", outline="#7f1d1d", width=2
                )
                radius = r
                is_image = False

            tomatoes.append({
                "id": tid,
                "hp": MOB_HP_EACH,
                "x": tx,
                "y": ty,
                "base_y": ty,
                "vy_dir": random.choice([-1, 1]),
                "radius": radius,
                "is_image": is_image,
                "alive": True
            })

    spawn_line_tomatoes()

    # =====================
    # ✅ 플레이어 공격 (덴지 탄을 denjibomb로)
    # =====================
    def shoot_chainsaw():
        if game_over:
            return
        bx = denji_x + 40
        by = denji_y

        b_id = create_denji_bomb(bx, by)  # ✅ 덴지탄 생성(이미지)

        player_bullets.append({"id": b_id, "vx": BULLET_SPEED_PLAYER, "vy": 0})

    # =====================
    # 키 입력
    # =====================
    def on_key_down(e):
        if current_screen is not frame:
            return
        k = e.keysym
        pressed_keys.add(k)
        if k in ("space", "z", "Z"):
            shoot_chainsaw()
        if k == "Escape":
            root.after(200, bad_end)

    def on_key_up(e):
        if e.keysym in pressed_keys:
            pressed_keys.remove(e.keysym)

    root.bind("<KeyPress>", on_key_down)
    root.bind("<KeyRelease>", on_key_up)

    # =====================
    # 충돌 판정
    # =====================
    def bbox_intersect(b1, b2):
        if not b1 or not b2:
            return False
        x1, y1, x2, y2 = b1
        a1, b, a2, d = b2
        return not (x2 < a1 or a2 < x1 or y2 < b or d < y1)

    # =====================
    # 적 탄 생성
    # =====================
    def create_enemy_bomb(x, y):
        if bomb_tk is not None:
            return canvas.create_image(x, y, image=bomb_tk)
        return canvas.create_oval(x-6, y-6, x+6, y+6,
                                 fill="#60a5fa", outline="#1d4ed8", width=1)

    # =====================
    # 덴지 탄 생성
    # =====================
    def create_denji_bomb(x, y):
        if denji_bomb_tk is not None:
            return canvas.create_image(x, y, image=denji_bomb_tk)
        # 이미지 없을 때 임시 대체
        return canvas.create_oval(x-6, y-6, x+6, y+6,
                                fill="#f97316", outline="#111827", width=1)


    # =====================
    # 보스 등장 시: 이전 쫄몹 탄 전부 삭제
    # =====================
    def clear_enemy_bullets():
        for b in enemy_bullets[:]:
            try:
                canvas.delete(b["id"])
            except Exception:
                pass
        enemy_bullets.clear()

    # =====================
    # 보스 등장 처리 (멘트 1회)
    # =====================
    def spawn_boss():
        nonlocal boss_active, devil_id
        if boss_active or game_over:
            return

        clear_enemy_bullets()

        boss_active = True
        enemy_hp.set(ENEMY_MAX)
        switch_enemy_panel_to_boss()
        devil_id = canvas.create_image(devil_x, devil_y, image=devil_tk)

        show_log_ui("토마토의 악마가 모습을 드러낸다!")
        root.after(1200, hide_log_ui)

    # =====================
    # enemy 발사 (쫄몹 → 보스)
    # =====================
    def enemy_shoot():
        if current_screen is not frame or game_over:
            return

        if not boss_active:
            for mob in tomatoes:
                if not mob["alive"]:
                    continue
                if random.random() < MOB_FIRE_CHANCE:
                    tx = mob["x"] - mob["radius"]
                    ty = mob["y"]
                    tid = create_enemy_bomb(tx, ty)

                    vx, vy = calc_homing_velocity(
                        tx, ty,
                        BULLET_SPEED_ENEMY * 0.85,
                        angle_error_deg=12
                    )

                    enemy_bullets.append({"id": tid, "vx": vx, "vy": vy})

            root.after(random.randint(MOB_FIRE_MIN, MOB_FIRE_MAX), enemy_shoot)

        else:
            bx = devil_x - 90
            by = devil_y + random.randint(-40, 40)
            bid = create_enemy_bomb(bx, by)

            vx, vy = calc_homing_velocity(
                bx, by,
                BULLET_SPEED_ENEMY * 1.10,
                angle_error_deg=0
            )

            enemy_bullets.append({"id": bid, "vx": vx, "vy": vy})
            root.after(random.randint(ENEMY_FIRE_MIN, ENEMY_FIRE_MAX), enemy_shoot)

    # =====================
    # 메인 루프
    # =====================
    def game_loop():
        nonlocal denji_x, denji_y, game_over
        global ticket_count

        if current_screen is not frame or game_over:
            return

        dx = dy = 0
        if "Left" in pressed_keys or "a" in pressed_keys:
            dx -= player_speed
        if "Right" in pressed_keys or "d" in pressed_keys:
            dx += player_speed
        if "Up" in pressed_keys or "w" in pressed_keys:
            dy -= player_speed
        if "Down" in pressed_keys or "s" in pressed_keys:
            dy += player_speed

        denji_x += dx
        denji_y += dy

        denji_x = max(40, min(CANVAS_W - 260, denji_x))
        denji_y = max(60, min(ground_y - 20, denji_y))
        canvas.coords(denji_id, denji_x, denji_y)

        # 쫄몹 흔들기
        for mob in tomatoes:
            if not mob["alive"]:
                continue
            mob["y"] += mob["vy_dir"] * 0.65
            if abs(mob["y"] - mob["base_y"]) > 18:
                mob["vy_dir"] *= -1

            if mob["is_image"]:
                canvas.coords(mob["id"], mob["x"], mob["y"])
            else:
                r = mob["radius"]
                canvas.coords(mob["id"],
                              mob["x"]-r, mob["y"]-r,
                              mob["x"]+r, mob["y"]+r)

        # 플레이어 탄 이동 + 충돌
        remove_player = []
        enemy_bbox = canvas.bbox(devil_id) if (boss_active and devil_id is not None) else None

        for b in player_bullets:
            bid = b["id"]
            canvas.move(bid, b["vx"], b["vy"])
            bx = canvas.bbox(bid)

            if not bx or bx[0] > CANVAS_W:
                remove_player.append(b)
                continue

            hit_any = False

            # 쫄몹 판정
            for mob in tomatoes:
                if not mob["alive"]:
                    continue
                mb = canvas.bbox(mob["id"])
                if mb and bbox_intersect(bx, mb):
                    mob["hp"] -= 1
                    mob_total_hp.set(max(0, mob_total_hp.get() - 1))
                    damage_splash(mob["x"], mob["y"]-10, 1, "#fde68a")
                    if mob["hp"] <= 0:
                        mob["alive"] = False
                        canvas.delete(mob["id"])
                    update_bars()
                    hit_any = True
                    break

            # 보스 판정
            if (not hit_any) and boss_active and enemy_bbox and bbox_intersect(bx, enemy_bbox):
                dmg = random.randint(8, 14)
                enemy_hp.set(max(0, enemy_hp.get() - dmg))
                damage_splash(devil_x-40, devil_y - 20, dmg, "#ef4444")
                update_bars()
                hit_any = True

            if hit_any:
                canvas.delete(bid)
                remove_player.append(b)

        for b in remove_player:
            if b in player_bullets:
                player_bullets.remove(b)

        # ✅ 쫄몹 전부 죽으면 보스 등장
        if (not boss_active) and mob_total_hp.get() <= 0:
            spawn_boss()

        # enemy 탄 이동 + 피격
        player_bbox = canvas.bbox(denji_id)
        remove_enemy = []

        for t in enemy_bullets:
            tid = t["id"]
            canvas.move(tid, t["vx"], t["vy"])
            tb = canvas.bbox(tid)

            if not tb or tb[2] < 0:
                remove_enemy.append(t)
                continue

            if bbox_intersect(tb, player_bbox):
                dmg = random.randint(6, 10)
                player_hp.set(max(0, player_hp.get() - dmg))
                damage_splash(denji_x+20, denji_y - 20, dmg, "#3b82f6")
                update_bars()
                canvas.delete(tid)
                remove_enemy.append(t)

        for t in remove_enemy:
            if t in enemy_bullets:
                enemy_bullets.remove(t)

        # 승패
        if boss_active and enemy_hp.get() <= 0 and not game_over:
            game_over = True
            ticket_count += 1
            root.after(200, victory)
            return

        if player_hp.get() <= 0 and not game_over:
            game_over = True
            root.after(200, bad_end)
            return

        root.after(33, game_loop)

    update_bars()
    enemy_shoot()
    game_loop()

# ==========================
# 엔딩
# ==========================
def victory():
    global stage_cleared
    # 1번 스테이지(토마토의 악마) 토벌 완료 처리
    stage_cleared[1] = True

    ending(
        "토마토의 악마 토벌 완료!",
        "토마토의 악마를 잡는 데 성공했다!\n뽑기권 하나 증정!"
    )

def escape_end():
    ending("도망 성공", "간신히 목숨은 건졌다…")

def bad_end():
    ending("GAME OVER", "덴지는 쓰러지고 말았다.")


def ending(title, msg):
    clear_screen()
    f = tk.Frame(root, bg=ROOT_BG)
    f.pack(fill="both", expand=True)

    tk.Label(f, text=title, font=PIXEL_TITLE,
             bg=ROOT_BG, fg="#fbbf24").pack(pady=30)

    tk.Label(f, text=msg, font=PIXEL_FONT,
             bg=ROOT_BG, fg="#e5e7eb",
             justify="center").pack(pady=10)

    # 엔딩 이후에는 마키마 허브로 이동
    tk.Button(
        f,
        text="마키마에게로",
        font=PIXEL_FONT, width=16,
        relief="solid", bd=4,
        bg="#10b981", fg="black",
        activebackground="#34d399",
        command=hub_mode
    ).pack(pady=24)

    global current_screen
    current_screen = f


# ==========================
# 실행
# ==========================
title_screen()
root.mainloop()