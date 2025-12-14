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

    # 배경def battle_mode_stage2():
    import main
    gs.reset_binds()
    gs.clear_screen()

    frame = tk.Frame(gs.root, bg=ROOT_BG)
    frame.pack(fill="both", expand=True)
    gs.current_screen = frame

    W, H = ROOT_W, ROOT_H
    ground_y = H - 80

    PLAYER_MAX = 110
    AKANE_MAX = 90
    KATANA_MAX = 110

    player_hp = tk.IntVar(value=PLAYER_MAX)
    akane_hp = tk.IntVar(value=AKANE_MAX)
    katana_hp = tk.IntVar(value=KATANA_MAX)

    canvas = tk.Canvas(
        frame, width=W, height=H,
        bg=GAME_BG, highlightthickness=4,
        highlightbackground=PANEL_BORDER
    )
    canvas.pack(expand=True)

    canvas.create_rectangle(0, 0, W, ground_y, fill=SKY_COLOR, outline=SKY_COLOR)
    canvas.create_rectangle(0, ground_y, W, H, fill=GROUND_COLOR, outline=GROUND_COLOR)

    # ===== 덴지 크기 대폭 업 (여기만 핵심 변경) =====
    DENJI_W, DENJI_H = 260, 350

    denji1_p = os.path.join(IMG_DIR, "denji1.png")
    denji2_p = os.path.join(IMG_DIR, "denji2.png")
    chain2_p = os.path.join(IMG_DIR, "chain2.png")
    attack_p = os.path.join(IMG_DIR, "attack.png")

    akane_p = os.path.join(IMG_DIR, "akane.png")
    katana_p = os.path.join(IMG_DIR, "katana.png")
    akane_shot_p = os.path.join(IMG_DIR, "shot.png")
    knife_p = os.path.join(IMG_DIR, "knife.png")

    # 덴지(커짐)
    denji1_tk = ImageTk.PhotoImage(fit_nearest(denji1_p, DENJI_W, DENJI_H))
    denji2_tk = ImageTk.PhotoImage(fit_nearest(denji2_p, DENJI_W, DENJI_H))
    chain2_tk = ImageTk.PhotoImage(fit_nearest(chain2_p, DENJI_W + 50, DENJI_H + 30))

    # 적(그대로)
    akane_tk = ImageTk.PhotoImage(fit_nearest(akane_p, 200, 240))
    katana_tk = ImageTk.PhotoImage(fit_nearest(katana_p, 220, 240))

    akane_shot_tk = ImageTk.PhotoImage(fit_nearest(akane_shot_p, 40, 14))
    knife_tk = ImageTk.PhotoImage(fit_nearest(knife_p, 52, 22))

    # attack.png(회전용) - 크기도 같이 키워줌
    attack_base_pil = Image.open(attack_p).convert("RGBA").resize((260, 260), Image.NEAREST)

    # GC
    canvas.denji1 = denji1_tk
    canvas.denji2 = denji2_tk
    canvas.chain2 = chain2_tk
    canvas.attack_base = attack_base_pil
    canvas.akane = akane_tk
    canvas.katana = katana_tk
    canvas.akane_shot = akane_shot_tk
    canvas.knife = knife_tk

    game_over = {"v": False}

    denji = setup_denji(
        frame, canvas, W, H, ground_y,
        denji_walk_frames_tk=[denji1_tk, denji2_tk],
        chain2_tk=chain2_tk,
        attack_base_pil=attack_base_pil,
        player_speed=8,
        on_escape=lambda: main.hub_mode()
    )

    SAFE_TOP = 60
    SAFE_BOTTOM = ground_y - 20

    def damage_splash(cx, cy, val, color):
        t = canvas.create_text(cx, cy, text=f"-{val}", fill=color,
                               font=("Courier New", 14, "bold"))

        def anim(step=0):
            if gs.current_screen is not frame:
                return
            if step < 14:
                canvas.move(t, 0, -2)
                gs.root.after(40, anim, step + 1)
            else:
                canvas.delete(t)
        anim()

    akane = {"alive": True, "x": int(W * 0.68), "y": int(H * 0.45), "id": None}
    katana = {"alive": True, "x": int(W * 0.83), "y": int(H * 0.55), "id": None}

    akane["id"] = canvas.create_image(akane["x"], akane["y"], image=akane_tk)
    katana["id"] = canvas.create_image(katana["x"], katana["y"], image=katana_tk)

    enemy_bullets = []

    AKANE_FIRE_MIN = 1600
    AKANE_FIRE_MAX = 2400
    AKANE_BULLET_SPEED = 9

    KATANA_FIRE_MIN = 1200
    KATANA_FIRE_MAX = 2000
    KNIFE_SPEED = 7

    def create_akane_shot(x, y):
        return canvas.create_image(x, y, image=akane_shot_tk)

    def create_knife(x, y):
        return canvas.create_image(x, y, image=knife_tk)

    def clear_enemy_bullets():
        for b in enemy_bullets[:]:
            try:
                canvas.delete(b["id"])
            except Exception:
                pass
        enemy_bullets.clear()

    def akane_attack():
        if gs.current_screen is not frame or game_over["v"] or not akane["alive"]:
            return
        y = random.randint(SAFE_TOP, SAFE_BOTTOM)
        x = W + 30
        bid = create_akane_shot(x, y)
        enemy_bullets.append({"id": bid, "vx": -AKANE_BULLET_SPEED, "vy": 0})
        gs.root.after(random.randint(AKANE_FIRE_MIN, AKANE_FIRE_MAX), akane_attack)

    def katana_attack():
        if gs.current_screen is not frame or game_over["v"] or not katana["alive"]:
            return
        y = katana["y"] + random.randint(-70, 70)
        y = max(SAFE_TOP, min(SAFE_BOTTOM, y))
        x = katana["x"] - 80
        bid = create_knife(x, y)
        enemy_bullets.append({"id": bid, "vx": -KNIFE_SPEED, "vy": 0})
        gs.root.after(random.randint(KATANA_FIRE_MIN, KATANA_FIRE_MAX), katana_attack)

    def victory():
        game_over["v"] = True
        clear_enemy_bullets()
        gs.ticket_count += 1
        gs.stage_cleared[2] = True
        show_victory(
            title="악마 토벌 완료!",
            subtitle="아카네와 카타나맨을 쓰러뜨렸다.",
            reward_text="보상: 뽑기권 1장 획득!",
            on_map=world_map,
            on_hub=main.hub_mode
        )

    def defeat():
        game_over["v"] = True
        clear_enemy_bullets()
        show_defeat(on_map=world_map, on_hub=main.hub_mode)

    def game_loop():
        if gs.current_screen is not frame or game_over["v"]:
            return

        # ===== 덴지 이동 =====
        dx = dy = 0
        p = denji["pressed"]
        if "Left" in p or "a" in p or "A" in p:
            dx -= denji["speed"]
        if "Right" in p or "d" in p or "D" in p:
            dx += denji["speed"]
        if "Up" in p or "w" in p or "W" in p:
            dy -= denji["speed"]
        if "Down" in p or "s" in p or "S" in p:
            dy += denji["speed"]

        denji["pos"]["x"] = max(40, min(W - 40, denji["pos"]["x"] + dx))
        denji["pos"]["y"] = max(SAFE_TOP, min(ground_y - 20, denji["pos"]["y"] + dy))
        canvas.coords(denji["id"], denji["pos"]["x"], denji["pos"]["y"])

        player_bbox = canvas.bbox(denji["id"])

        # ===== 근접 공격 판정(스페이스) =====
        denji["consume_attack"]()

        if denji["attack"]["just"]:
            ax1 = denji["pos"]["x"] + 25
            ax2 = denji["pos"]["x"] + 25 + denji["attack"]["range_x"]
            ay1 = denji["pos"]["y"] - denji["attack"]["range_y"]
            ay2 = denji["pos"]["y"] + denji["attack"]["range_y"]
            attack_box = (ax1, ay1, ax2, ay2)

            akane_bbox = canvas.bbox(akane["id"]) if akane["alive"] else None
            katana_bbox = canvas.bbox(katana["id"]) if katana["alive"] else None

            if akane["alive"] and akane_bbox and bbox_intersect(attack_box, akane_bbox):
                dmg = random.randint(10, 16)
                akane_hp.set(max(0, akane_hp.get() - dmg))
                damage_splash(akane["x"], akane["y"] - 60, dmg, "#a855f7")
                if akane_hp.get() <= 0:
                    akane["alive"] = False
                    try:
                        canvas.delete(akane["id"])
                    except Exception:
                        pass

            if katana["alive"] and katana_bbox and bbox_intersect(attack_box, katana_bbox):
                dmg = random.randint(10, 16)
                katana_hp.set(max(0, katana_hp.get() - dmg))
                damage_splash(katana["x"], katana["y"] - 60, dmg, "#ef4444")
                if katana_hp.get() <= 0:
                    katana["alive"] = False
                    try:
                        canvas.delete(katana["id"])
                    except Exception:
                        pass

        # ===== 적 탄 이동/피격 =====
        for e in enemy_bullets[:]:
            canvas.move(e["id"], e["vx"], e["vy"])
            eb = canvas.bbox(e["id"])

            if not eb or eb[2] < -50:
                canvas.delete(e["id"])
                enemy_bullets.remove(e)
                continue

            if player_bbox and bbox_intersect(eb, player_bbox):
                dmg = random.randint(6, 10)
                player_hp.set(max(0, player_hp.get() - dmg))
                damage_splash(denji["pos"]["x"], denji["pos"]["y"] - 40, dmg, "#3b82f6")
                canvas.delete(e["id"])
                enemy_bullets.remove(e)

        if player_hp.get() <= 0:
            defeat()
            return

        if (not akane["alive"]) and (not katana["alive"]):
            victory()
            return

        gs.root.after(33, game_loop)

    akane_attack()
    katana_attack()
    game_loop()

    bg_path = os.path.join(IMG_DIR, "back1.png")
    if os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGBA")
        img = img.resize((ROOT_W, ROOT_H), Image.NEAREST)
        tkimg = ImageTk.PhotoImage(img)
        canvas.create_image(ROOT_W // 2, ROOT_H // 2, image=tkimg, anchor="center")
        canvas.bg = tkimg  # 참조 유지

    # ==========================
    # ARE YOU READY?
    # ==========================
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

    # ==========================
    # YES / NO 선택 UI
    # ==========================
    choice_y = 350
    yes_x = ROOT_W // 2 - 100
    no_x  = ROOT_W // 2 + 100

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

    selected = 0  # 0=YES, 1=NO

    def update_selection():
        if selected == 0:
            canvas.itemconfig(yes_id, fill="#ffffff")
            canvas.itemconfig(no_id, fill="#6b7280")
            canvas.coords(arrow_id, yes_x - 45, arrow_y)
        else:
            canvas.itemconfig(yes_id, fill="#6b7280")
            canvas.itemconfig(no_id, fill="#ffffff")
            canvas.coords(arrow_id, no_x - 45, arrow_y)

    def do_select():
        if selected == 0:
            story_mode()
        else:
            gs.root.quit()

    def on_key(e):
        nonlocal selected
        if gs.current_screen is not frame:
            return

        if e.keysym in ("Left", "Right", "Up", "Down"):
            selected = 1 - selected
            update_selection()
        elif e.keysym in ("Return", "space"):
            do_select()

    gs.root.bind("<Key>", on_key)

    def click_yes(_event=None):
        if gs.current_screen is not frame:
            return
        story_mode()

    def click_no(_event=None):
        if gs.current_screen is not frame:
            return
        gs.root.quit()

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

    # ==== 창고 배경 ====
    ground_y = int(H * 0.72)

    canvas.create_rectangle(0, 0, W, ground_y,
                            fill="#82aeea", outline="")

    canvas.create_polygon(
        -40, ground_y - 40,
        120, ground_y - 90,
        260, ground_y - 50,
        400, ground_y - 100,
        560, ground_y - 60,
        W + 40, ground_y - 80,
        W + 40, ground_y,
        -40, ground_y,
        fill="#4b5563", outline=""
    )

    canvas.create_polygon(
        0, 0,
        int(W * 0.28), 0,
        int(W * 0.18), H,
        0, H,
        fill="#020617", outline=""
    )

    wh_left = int(W * 0.42)
    wh_right = W - 30
    wh_bottom = ground_y + 10
    wh_top = ground_y - 140

    canvas.create_rectangle(wh_left, wh_top, wh_right, wh_bottom,
                            fill="#8a4f32", outline="#4b2b1f")

    stripe_w = 8
    x = wh_left
    toggle = 0
    while x < wh_right:
        color = "#b8734b" if toggle % 2 == 0 else "#a66640"
        canvas.create_rectangle(x, wh_top, x + stripe_w, wh_bottom,
                                fill=color, outline="")
        toggle += 1
        x += stripe_w

    canvas.create_rectangle(wh_left + 20, wh_top + 10, wh_left + 140, wh_top + 40,
                            fill="#e5dccf", outline="", stipple="gray50")
    canvas.create_rectangle(wh_right - 160, wh_top + 25, wh_right - 20, wh_top + 55,
                            fill="#d3c3b0", outline="", stipple="gray50")

    door_w = 140
    door_h = 70
    door_left = wh_left + (wh_right - wh_left) // 2 - door_w // 2
    door_right = door_left + door_w
    door_bottom = ground_y + 4
    door_top = door_bottom - door_h

    canvas.create_rectangle(door_left - 4, door_top - 18, door_right + 4, door_top,
                            fill="#e5e7eb", outline="#9ca3af")
    canvas.create_rectangle(door_left, door_top, door_right, door_bottom,
                            fill="#020617", outline="#020617")

    pillar_x = wh_right - 22
    canvas.create_rectangle(pillar_x, wh_top, pillar_x + 8, wh_bottom,
                            fill="#5b4330", outline="#2b1f18")
    for yy in range(wh_top + 10, wh_bottom - 20, 30):
        canvas.create_line(pillar_x, yy, pillar_x + 8, yy + 20,
                           fill="#2b1f18", width=2)
        canvas.create_line(pillar_x + 8, yy, pillar_x, yy + 20,
                           fill="#2b1f18", width=2)

    fence_top = ground_y - 60
    fence_bottom = ground_y
    fence_left = wh_left - 110
    fence_right = wh_left - 10
    canvas.create_rectangle(fence_left, fence_top, fence_right, fence_bottom,
                            fill="#374151", outline="#111827")

    step = 10
    for xx in range(fence_left + step, fence_right, step):
        canvas.create_line(xx, fence_top, xx, fence_bottom, fill="#9ca3af")
    for yy in range(fence_top + step, fence_bottom, step):
        canvas.create_line(fence_left, yy, fence_right, yy, fill="#9ca3af")

    canvas.create_polygon(
        fence_left + 8, fence_bottom - 8,
        fence_left + 40, fence_bottom - 40,
        fence_left + 90, fence_bottom - 25,
        fence_left + 70, fence_bottom - 8,
        fill="#6b7280", outline="#111827"
    )

    canvas.create_rectangle(0, ground_y, W, H,
                            fill="#7c7c7c", outline="#4b4b4b")

    for _ in range(260):
        gx = _rnd.randint(0, W)
        gy = _rnd.randint(ground_y, H)
        r = _rnd.randint(1, 3)
        col = _rnd.choice(["#5f5f5f", "#9a9a9a", "#646464", "#858585"])
        canvas.create_oval(gx - r, gy - r, gx + r, gy + r,
                           fill=col, outline="")

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
        denji_img = denji_img.transpose(Image.FLIP_TOP_BOTTOM)  # ✅ 세로(위아래) 반전
    else:
        denji_img = Image.new("RGBA", (160, 240), (200, 200, 200, 255))
        denji_img = denji_img.transpose(Image.FLIP_TOP_BOTTOM)

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
    # 마키마2 이미지 중앙 배치
    # ==========================
    def fit_soft(path, w, h):
        img = Image.open(path).convert("RGBA")
        iw, ih = img.size
        scale = min(w / iw, h / ih)
        new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
        return img.resize(new_size, Image.LANCZOS)

    makima2_p = os.path.join(IMG_DIR, "makima1.png")
    if os.path.exists(makima2_p):
        makima2_img = fit_soft(makima2_p, int(W * 0.30), int(H * 0.45))
    else:
        makima2_img = Image.new("RGBA", (220, 320), (180, 120, 200, 255))

    makima2_tk = ImageTk.PhotoImage(makima2_img)
    canvas.makima2 = makima2_tk

    canvas.create_image(
        W // 2, int(H * 0.48),
        image=makima2_tk,
        anchor="center"
    )

    # ==========================
    # (레트로 도트) 메뉴 버튼 4개
    # ==========================
    labels = ["스테이지 밀기", "뽑기", "동료 보기", "저장"]
    # (cx, outer, inner, face, shine_list, shade_list, txt)
    btn_infos = []

    base_y = int(H * 0.86)
    gap = int(W * 0.17)
    bw = int(W * 0.14)
    bh = int(H * 0.038)

    # 픽셀 UI 팔레트
    OUTER_DARK   = "#0b1220"
    INNER_DARK   = "#1f2a3a"
    FACE_NORMAL  = "#111827"
    FACE_HOVER   = "#162033"
    HI_LINE      = "#94a3b8"
    SHADOW_LINE  = "#020617"

    TXT_NORMAL   = "#cbd5e1"
    TXT_DIM      = "#64748b"

    ACCENT       = "#facc15"
    ACCENT_DARK  = "#a16207"
    TXT_ACTIVE   = "#ffffff"

    def draw_pixel_button(cx, cy, text):
        x1, y1 = cx - bw, cy - bh
        x2, y2 = cx + bw, cy + bh

        # 프레임 2겹 + 면
        outer = canvas.create_rectangle(x1, y1, x2, y2,
                                        fill=OUTER_DARK, outline=OUTER_DARK)

        pad1 = 3
        inner = canvas.create_rectangle(x1 + pad1, y1 + pad1, x2 - pad1, y2 - pad1,
                                        fill=INNER_DARK, outline=INNER_DARK)

        pad2 = 6
        face = canvas.create_rectangle(x1 + pad2, y1 + pad2, x2 - pad2, y2 - pad2,
                                       fill=FACE_NORMAL, outline=FACE_NORMAL)

        # 돌출 라인(픽셀 느낌)
        shine = []
        shade = []

        shine.append(canvas.create_line(x1 + pad2, y1 + pad2, x2 - pad2, y1 + pad2,
                                        fill=HI_LINE, width=2))
        shine.append(canvas.create_line(x1 + pad2, y1 + pad2, x1 + pad2, y2 - pad2,
                                        fill=HI_LINE, width=2))
        shade.append(canvas.create_line(x1 + pad2, y2 - pad2, x2 - pad2, y2 - pad2,
                                        fill=SHADOW_LINE, width=2))
        shade.append(canvas.create_line(x2 - pad2, y1 + pad2, x2 - pad2, y2 - pad2,
                                        fill=SHADOW_LINE, width=2))

        # 텍스트 + 픽셀 그림자(1px)
        shadow_txt = canvas.create_text(cx + 2, cy + 2, text=text, font=PIXEL_FONT, fill="#000000")
        txt = canvas.create_text(cx, cy, text=text, font=PIXEL_FONT, fill=TXT_NORMAL)

        return outer, inner, face, shine, shade, shadow_txt, txt

    for i, text in enumerate(labels):
        cx = W // 2 + int((i - 1.5) * gap)
        outer, inner, face, shine, shade, sh_txt, txt = draw_pixel_button(cx, base_y, text)
        btn_infos.append((cx, outer, inner, face, shine, shade, sh_txt, txt))

    arrow_id = canvas.create_text(
        btn_infos[0][0], base_y + bh + 18,
        text="▲",
        font=("Courier New", 18, "bold"),
        fill=ACCENT
    )

    selected = 0
    hovered = -1

    def set_button_style(i, active=False, hover=False):
        cx, outer, inner, face, shine, shade, sh_txt, txt = btn_infos[i]

        if active:
            canvas.itemconfig(outer, fill=ACCENT_DARK, outline=ACCENT_DARK)
            canvas.itemconfig(inner, fill=ACCENT, outline=ACCENT)
            canvas.itemconfig(face,  fill="#0b1220", outline="#0b1220")
            canvas.itemconfig(txt,   fill=TXT_ACTIVE)
            canvas.itemconfig(sh_txt, fill="#000000")

            for item in shine:
                canvas.itemconfig(item, fill="#fff7ed")
            for item in shade:
                canvas.itemconfig(item, fill="#1f2937")
        else:
            canvas.itemconfig(outer, fill=OUTER_DARK, outline=OUTER_DARK)
            canvas.itemconfig(inner, fill=INNER_DARK, outline=INNER_DARK)
            canvas.itemconfig(face,  fill=(FACE_HOVER if hover else FACE_NORMAL),
                              outline=(FACE_HOVER if hover else FACE_NORMAL))
            canvas.itemconfig(txt,   fill=(TXT_NORMAL if hover else TXT_DIM))
            canvas.itemconfig(sh_txt, fill="#000000")

            for item in shine:
                canvas.itemconfig(item, fill=HI_LINE)
            for item in shade:
                canvas.itemconfig(item, fill=SHADOW_LINE)

    def update_selection():
        for i in range(len(btn_infos)):
            set_button_style(i, active=(i == selected), hover=(i == hovered))
        canvas.coords(arrow_id, btn_infos[selected][0], base_y + bh + 18)

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
        elif selected == 2:
            ok = safe_call(partner, ["allies_room", "partner_room", "partner_mode", "partner_screen"])
            if not ok:
                canvas.itemconfig(status_text, text="마키마: 동료 보기 함수명을 못 찾았어 (partner 모듈 확인).")
        else:
            ok = safe_call(save, ["save_mode", "save_game", "open_save"])
            if not ok:
                canvas.itemconfig(status_text, text="마키마: 저장 기능은 아직 준비 중이야.")

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

    for i, (_cx, outer, inner, face, _shine, _shade, sh_txt, txt) in enumerate(btn_infos):
        for tag in (outer, inner, face, sh_txt, txt):
            canvas.tag_bind(tag, "<Button-1>", make_click(i))
            canvas.tag_bind(tag, "<Enter>", on_enter(i))
            canvas.tag_bind(tag, "<Leave>", on_leave)

    update_selection()


if __name__ == "__main__":
    title_screen()
    gs.root.mainloop()