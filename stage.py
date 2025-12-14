# stage.py
from PIL import Image, ImageTk
import tkinter as tk
import random, os, math

from ui_config import *
import game_state as gs


# =========================================================
# 공용 유틸
# =========================================================
def bbox_intersect(b1, b2):
    if not b1 or not b2:
        return False
    x1, y1, x2, y2 = b1
    a1, b, a2, d = b2
    return not (x2 < a1 or a2 < x1 or y2 < b or d < y1)


def fit_nearest(path, w, h):
    img = Image.open(path).convert("RGBA")
    iw, ih = img.size
    s = min(w / iw, h / ih, 1)
    return img.resize((max(1, int(iw * s)), max(1, int(ih * s))), Image.NEAREST)


def make_status_panel(canvas, x1, y1, name, max_hp, hp_var):
    PANEL_W = 210
    PANEL_H = 56
    HP_BAR_W = 95
    HP_BAR_H = 10

    x2 = x1 + PANEL_W
    y2 = y1 + PANEL_H

    canvas.create_rectangle(x1 + 3, y1 + 3, x2 + 3, y2 + 3, fill="#4b5563", outline="")
    canvas.create_rectangle(x1, y1, x2, y2, fill="#d1d5db", outline="#111827", width=2)

    inner_x1 = x1 + 5
    inner_y1 = y1 + 5
    inner_x2 = x2 - 5
    inner_y2 = y2 - 5
    canvas.create_rectangle(inner_x1, inner_y1, inner_x2, inner_y2, fill="#e5e7eb", outline="#9ca3af")

    name_y = inner_y1 + 14
    name_id = canvas.create_text(inner_x1 + 8, name_y, text=name, anchor="w",
                                 font=PIXEL_FONT, fill="#111827")

    hp_row_y = inner_y1 + 34
    hp_label_x = inner_x1 + 8
    canvas.create_text(hp_label_x, hp_row_y, text="HP:",
                       anchor="w", font=PIXEL_SMALL, fill="#f97316")

    hp_bg_x1 = hp_label_x + 30
    hp_bg_y1 = hp_row_y - HP_BAR_H // 2
    hp_bg_x2 = hp_bg_x1 + HP_BAR_W
    hp_bg_y2 = hp_bg_y1 + HP_BAR_H

    canvas.create_rectangle(hp_bg_x1, hp_bg_y1, hp_bg_x2, hp_bg_y2,
                            fill="#9ca3af", outline="#111827")

    hp_rect = canvas.create_rectangle(hp_bg_x1, hp_bg_y1, hp_bg_x2, hp_bg_y2,
                                      fill=HP_GREEN, outline="#111827")

    hp_text = canvas.create_text(hp_bg_x2 + 8, hp_row_y, anchor="w",
                                 font=PIXEL_SMALL, fill="#111827",
                                 text=f"{hp_var.get()}/{max_hp}")

    return {
        "name_id": name_id,
        "rect": hp_rect,
        "x1": hp_bg_x1, "y1": hp_bg_y1, "x2": hp_bg_x2, "y2": hp_bg_y2,
        "hp_text": hp_text,
        "max_hp": max_hp,
        "var": hp_var
    }


def update_single_bar(canvas, panel_info):
    hp = panel_info["var"].get()
    max_hp = panel_info["max_hp"]
    ratio = max(0, min(1, hp / max_hp)) if max_hp > 0 else 0

    x1 = panel_info["x1"]
    x2 = panel_info["x2"]
    y1 = panel_info["y1"]
    y2 = panel_info["y2"]

    canvas.coords(panel_info["rect"], x1, y1, x1 + (x2 - x1) * ratio, y2)

    color = HP_GREEN if ratio > 0.5 else ("#facc15" if ratio > 0.25 else "#ef4444")
    canvas.itemconfig(panel_info["rect"], fill=color)
    canvas.itemconfig(panel_info["hp_text"], text=f"{hp}/{max_hp}")


def show_victory(title, subtitle, reward_text, on_map, on_hub):
    gs.reset_binds()
    gs.clear_screen()

    import main
    W, H = ROOT_W, ROOT_H

    f = tk.Frame(gs.root, bg=ROOT_BG)
    f.pack(fill="both", expand=True)
    gs.current_screen = f

    c = tk.Canvas(f, width=W, height=H, bg="#020617",
                  highlightthickness=4, highlightbackground=PANEL_BORDER)
    c.pack(expand=True)

    grid_step = 40
    for x in range(0, W, grid_step):
        c.create_line(x, 0, x, H, fill="#111827")
    for y in range(0, H, grid_step):
        c.create_line(0, y, W, y, fill="#111827")

    c.create_rectangle(120, 150, W - 120, H - 170,
                       outline="#4b5563", width=3, fill="#0b1220")

    c.create_text(W // 2, 230, text=title,
                  font=("Courier New", 30, "bold"), fill="#fbbf24")
    c.create_text(W // 2, 310, text=subtitle,
                  font=PIXEL_FONT, fill="#e5e7eb")
    c.create_text(W // 2, 370, text=reward_text,
                  font=PIXEL_FONT, fill="#34d399")

    btn_map = tk.Button(
        f, text="← 도쿄 맵으로",
        font=PIXEL_FONT, relief="solid", bd=3,
        bg="#111827", fg="#f9fafb",
        activebackground="#1f2937",
        command=on_map
    )
    btn_hub = tk.Button(
        f, text="← 마키마에게",
        font=PIXEL_FONT, relief="solid", bd=3,
        bg="#111827", fg="#f9fafb",
        activebackground="#1f2937",
        command=on_hub
    )

    c.create_window(W // 2, 410, window=btn_map)
    c.create_window(W // 2, 452, window=btn_hub)


def show_defeat(on_map, on_hub):
    gs.reset_binds()
    gs.clear_screen()

    W, H = ROOT_W, ROOT_H

    f = tk.Frame(gs.root, bg=ROOT_BG)
    f.pack(fill="both", expand=True)
    gs.current_screen = f

    c = tk.Canvas(f, width=W, height=H, bg="#020617",
                  highlightthickness=4, highlightbackground=PANEL_BORDER)
    c.pack(expand=True)

    grid_step = 40
    for x in range(0, W, grid_step):
        c.create_line(x, 0, x, H, fill="#111827")
    for y in range(0, H, grid_step):
        c.create_line(0, y, W, y, fill="#111827")

    c.create_rectangle(120, 150, W - 120, H - 170,
                       outline="#4b5563", width=3, fill="#0b1220")

    c.create_text(W // 2, 250, text="전투 패배...",
                  font=("Courier New", 30, "bold"), fill="#ef4444")
    c.create_text(W // 2, 330, text="다시 준비해서 도전하자.",
                  font=PIXEL_FONT, fill="#e5e7eb")

    btn_map = tk.Button(
        f, text="← 도쿄 맵으로",
        font=PIXEL_FONT, relief="solid", bd=3,
        bg="#111827", fg="#f9fafb",
        activebackground="#1f2937",
        command=on_map
    )
    btn_hub = tk.Button(
        f, text="← 마키마에게",
        font=PIXEL_FONT, relief="solid", bd=3,
        bg="#111827", fg="#f9fafb",
        activebackground="#1f2937",
        command=on_hub
    )

    c.create_window(W // 2, 390, window=btn_map)
    c.create_window(W // 2, 432, window=btn_hub)


def setup_denji(frame, canvas, W, H, ground_y,
                denji_walk_frames_tk,   # [denji1_tk, denji2_tk]
                chain2_tk,              # chain2_tk
                attack_base_pil,        # (이 버전에서는 무시됨) 기존 호환용
                player_speed=8,
                on_escape=None):

    pos = {"x": 140, "y": H // 2}
    pressed = set()

    if not denji_walk_frames_tk or len(denji_walk_frames_tk) < 2:
        denji_walk_frames_tk = [None, None]
    denji1_tk, denji2_tk = denji_walk_frames_tk[0], denji_walk_frames_tk[1]

    current_walk_idx = {"i": 1}
    denji_id = canvas.create_image(pos["x"], pos["y"], image=(denji2_tk or denji1_tk or chain2_tk))

    # ✅ GC 방지
    canvas.denji_walk_frames = denji_walk_frames_tk
    canvas.denji_chain2 = chain2_tk

    # attack 회전 프레임 캐시/GC 방지
    attack_anim = {
        "active": False,
        "overlay_id": None,
        "tk_frames": [],
        "step": 0
    }

    attack = {
        "request": False,
        "just": False,
        "cool_ms": 380,
        "cooling": False,
        "range_x": 140,
        "range_y": 80,
    }

    def start_cooldown():
        attack["cooling"] = True

        def end_cd():
            if gs.current_screen is not frame:
                return
            attack["cooling"] = False

        gs.root.after(attack["cool_ms"], end_cd)

    def request_attack():
        if attack["cooling"] or attack_anim["active"]:
            return
        attack["request"] = True

    def on_key_down(e):
        if gs.current_screen is not frame:
            return
        k = e.keysym
        pressed.add(k)

        if k in ("space", "z", "Z"):
            request_attack()

        if k == "Escape" and on_escape:
            on_escape()

    def on_key_up(e):
        pressed.discard(e.keysym)

    gs.root.bind("<KeyPress>", on_key_down)
    gs.root.bind("<KeyRelease>", on_key_up)

    def is_moving_now():
        p = pressed
        return any(k in p for k in ("Left", "Right", "Up", "Down", "a", "A", "d", "D", "w", "W", "s", "S"))

    def walk_anim_loop():
        if gs.current_screen is not frame:
            return

        if attack_anim["active"]:
            gs.root.after(120, walk_anim_loop)
            return

        if is_moving_now():
            current_walk_idx["i"] = 1 - current_walk_idx["i"]
            img = denji_walk_frames_tk[current_walk_idx["i"]] or denji2_tk or denji1_tk
            if img:
                canvas.itemconfig(denji_id, image=img)
        else:
            img = denji2_tk or denji1_tk
            if img:
                canvas.itemconfig(denji_id, image=img)

        gs.root.after(120, walk_anim_loop)

    walk_anim_loop()

    # ✅ 여기서부터가 핵심: "무조건 attack.png" 로 회전 오버레이 생성
    def _load_attack_base_from_png():
        attack_path = os.path.join(IMG_DIR, "attack.png")
        if not os.path.exists(attack_path):
            return None
        try:
            return Image.open(attack_path).convert("RGBA").resize((220, 220), Image.NEAREST)
        except Exception:
            return None

    def start_attack_anim():
        # 덴지 -> chain2
        if chain2_tk:
            canvas.itemconfig(denji_id, image=chain2_tk)

        # ✅ 무조건 attack.png 로드
        base_pil = _load_attack_base_from_png()
        if base_pil is None:
            return

        # 기존 overlay 정리
        if attack_anim["overlay_id"] is not None:
            try:
                canvas.delete(attack_anim["overlay_id"])
            except Exception:
                pass
            attack_anim["overlay_id"] = None

        attack_anim["tk_frames"].clear()
        attack_anim["step"] = 0
        attack_anim["active"] = True

        ox = pos["x"] + 35
        oy = pos["y"] - 10

        tk0 = ImageTk.PhotoImage(base_pil)
        attack_anim["tk_frames"].append(tk0)
        oid = canvas.create_image(ox, oy, image=tk0)
        canvas.tag_raise(oid)
        attack_anim["overlay_id"] = oid

        total_steps = 10
        step_ms = 28
        deg_per_step = 28

        def rotate_loop():
            if gs.current_screen is not frame:
                return
            if not attack_anim["active"]:
                return

            i = attack_anim["step"]
            if i >= total_steps:
                try:
                    if attack_anim["overlay_id"] is not None:
                        canvas.delete(attack_anim["overlay_id"])
                except Exception:
                    pass
                attack_anim["overlay_id"] = None
                attack_anim["active"] = False
                attack_anim["tk_frames"].clear()

                img = denji2_tk or denji1_tk or chain2_tk
                if img:
                    canvas.itemconfig(denji_id, image=img)
                return

            angle = -(i * deg_per_step)
            rotated = base_pil.rotate(angle, resample=Image.NEAREST, expand=True)

            tkimg = ImageTk.PhotoImage(rotated)
            attack_anim["tk_frames"].append(tkimg)

            nx = pos["x"] + 35
            ny = pos["y"] - 10

            canvas.itemconfig(attack_anim["overlay_id"], image=tkimg)
            canvas.coords(attack_anim["overlay_id"], nx, ny)
            canvas.tag_raise(attack_anim["overlay_id"])

            attack_anim["step"] += 1
            gs.root.after(step_ms, rotate_loop)

        rotate_loop()

    def consume_attack_request():
        if attack["request"] and (not attack["cooling"]) and (not attack_anim["active"]):
            attack["request"] = False
            attack["just"] = True
            start_cooldown()
            start_attack_anim()
        else:
            attack["just"] = False

    return {
        "id": denji_id,
        "pos": pos,
        "pressed": pressed,
        "speed": player_speed,
        "attack": attack,
        "consume_attack": consume_attack_request,
        "attack_anim": attack_anim
    }

# =========================================================
# 월드맵
# =========================================================
def world_map():
    import main
    gs.reset_binds()
    gs.clear_screen()

    frame = tk.Frame(gs.root, bg=ROOT_BG)
    frame.pack(fill="both", expand=True)
    gs.current_screen = frame

    W, H = ROOT_W, ROOT_H

    canvas = tk.Canvas(
        frame, width=W, height=H,
        bg="#1b1b28", highlightthickness=4,
        highlightbackground=PANEL_BORDER
    )
    canvas.pack(expand=True)

    bg_path = os.path.join(IMG_DIR, "stage1.png")
    if os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGBA")
        img = img.resize((W, H), Image.NEAREST)
        tkimg = ImageTk.PhotoImage(img)
        canvas.create_image(W // 2, H // 2, image=tkimg)
        canvas.bg = tkimg

    info_text = canvas.create_text(
        W // 2, 55,
        text="도쿄 맵: 스테이지를 선택해줘.",
        font=PIXEL_FONT, fill="#f9fafb"
    )

    def is_stage_unlocked(stage_id):
        if stage_id == 1:
            return True
        if stage_id == 2:
            return gs.stage_cleared.get(1, False)
        return False

    base_w, base_h = CANVAS_W, CANVAS_H
    sx = W / base_w
    sy = H / base_h

    circle_positions_base = [
        (260, 190),  # stage1
        (620, 150),  # stage2
        (360, 290),
        (540, 260),
    ]
    circle_positions = [(int(x * sx), int(y * sy)) for (x, y) in circle_positions_base]

    for i, (cx, cy) in enumerate(circle_positions):
        stage_id = i + 1
        r = int(35 * (sx * 0.5 + sy * 0.5) / 1.0)
        r = max(28, min(44, r))

        cleared = gs.stage_cleared.get(stage_id, False)
        unlocked = is_stage_unlocked(stage_id)

        if cleared:
            fill = "#4b5563"
        else:
            if unlocked:
                fill = "#f97316" if stage_id == 1 else "#3b82f6"
            else:
                fill = "#374151"

        c = canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                               fill=fill, outline="#ffffff", width=3)

        label = "✓" if cleared else str(stage_id)
        t = canvas.create_text(cx, cy, text=label,
                               font=("Courier New", 20, "bold"),
                               fill="#ffffff")

        def make_click(sid):
            def handler(_):
                if gs.stage_cleared.get(sid, False):
                    canvas.itemconfig(info_text, text="이미 클리어한 스테이지는 재진입이 불가능해.")
                    return
                if not is_stage_unlocked(sid):
                    canvas.itemconfig(info_text, text="아직 개방되지 않은 스테이지야.")
                    return

                if sid == 1:
                    battle_mode()
                elif sid == 2:
                    battle_mode_stage2()
                else:
                    canvas.itemconfig(info_text, text="아직 준비 중인 스테이지야.")
            return handler

        canvas.tag_bind(c, "<Button-1>", make_click(stage_id))
        canvas.tag_bind(t, "<Button-1>", make_click(stage_id))

    btn_hub = tk.Button(
        frame, text="← 마키마에게",
        font=PIXEL_FONT, relief="solid", bd=3,
        bg="#111827", fg="#f9fafb",
        activebackground="#1f2937",
        command=main.hub_mode
    )
    canvas.create_window(20, 20, window=btn_hub, anchor="nw")

# =========================================================
# 전투(토마토의 악마) - stage1
# =========================================================
def battle_mode():
    import main
    gs.reset_binds()
    gs.clear_screen()

    frame = tk.Frame(gs.root, bg=ROOT_BG)
    frame.pack(fill="both", expand=True)
    gs.current_screen = frame

    W, H = ROOT_W, ROOT_H
    ground_y = H - 80

    # =========================
    # 기본 스탯
    # =========================
    PLAYER_MAX = 100

    # ✅ 보스 피 더 줄임 (원래 80 → 55)
    ENEMY_MAX = 55

    # ✅ 쫄몹: 한 대 맞으면 즉사
    MOB_COUNT = 10
    MOB_HP_EACH = 1
    MOB_TOTAL_MAX = MOB_COUNT * MOB_HP_EACH

    player_hp = tk.IntVar(value=PLAYER_MAX)
    mob_total_hp = tk.IntVar(value=MOB_TOTAL_MAX)
    enemy_hp = tk.IntVar(value=0)

    canvas = tk.Canvas(
        frame, width=W, height=H,
        bg=GAME_BG, highlightthickness=4,
        highlightbackground=PANEL_BORDER
    )
    canvas.pack(expand=True)

    # =========================================================
    # ✅ 배경: tomatoback.png (조금 더 확대 + 스크롤)
    # =========================================================
    bg_path = os.path.join(IMG_DIR, "tomatoback.png")
    bg_id = None
    bg_img_tk = None
    bg_scroll = {
        "x": 0.0, "y": 0.0,
        "max_x": 0.0, "max_y": 0.0,
        "factor": 0.35
    }

    if os.path.exists(bg_path):
        try:
            base = Image.open(bg_path).convert("RGBA")
            # ✅ 확대 더(원래 1.18 → 1.32)
            zoom = 1.32
            bw = int(W * zoom)
            bh = int(H * zoom)
            bg_pil = base.resize((bw, bh), Image.NEAREST)

            bg_img_tk = ImageTk.PhotoImage(bg_pil)
            bg_id = canvas.create_image(W // 2, H // 2, image=bg_img_tk)
            canvas.bg_img = bg_img_tk  # GC 방지

            bg_scroll["max_x"] = max(0, (bw - W) / 2)
            bg_scroll["max_y"] = max(0, (bh - H) / 2)
        except Exception:
            bg_id = None

    if bg_id is None:
        canvas.create_rectangle(0, 0, W, ground_y, fill=SKY_COLOR, outline=SKY_COLOR)
        canvas.create_rectangle(0, ground_y, W, H, fill=GROUND_COLOR, outline=GROUND_COLOR)

    # =========================================================
    # ✅ 덴지 / 이미지 로드
    # =========================================================
    DENJI_W, DENJI_H = 330, 460

    denji1_p = os.path.join(IMG_DIR, "denji1.png")
    denji2_p = os.path.join(IMG_DIR, "denji2.png")
    chain2_p = os.path.join(IMG_DIR, "chain2.png")
    attack_p = os.path.join(IMG_DIR, "attack.png")

    devil_p = os.path.join(IMG_DIR, "devil1.png")
    tomato_p = os.path.join(IMG_DIR, "tomato.png")
    tomatobomb_p = os.path.join(IMG_DIR, "tomatobomb.png")

    denji1_tk = ImageTk.PhotoImage(fit_nearest(denji1_p, DENJI_W, DENJI_H))
    denji2_tk = ImageTk.PhotoImage(fit_nearest(denji2_p, DENJI_W, DENJI_H))
    chain2_tk = ImageTk.PhotoImage(fit_nearest(chain2_p, DENJI_W + 70, DENJI_H + 40))

    devil_tk = ImageTk.PhotoImage(fit_nearest(devil_p, 260, 220))
    bomb_tk = ImageTk.PhotoImage(fit_nearest(tomatobomb_p, 44, 44))

    attack_base_pil = Image.open(attack_p).convert("RGBA").resize((280, 280), Image.NEAREST)

    # GC
    canvas.denji1 = denji1_tk
    canvas.denji2 = denji2_tk
    canvas.chain2 = chain2_tk
    canvas.attack_base = attack_base_pil
    canvas.devil = devil_tk
    canvas.bomb = bomb_tk

    game_over = {"v": False}

    denji = setup_denji(
        frame, canvas, W, H, ground_y,
        denji_walk_frames_tk=[denji1_tk, denji2_tk],
        chain2_tk=chain2_tk,
        attack_base_pil=attack_base_pil,
        player_speed=8,
        on_escape=lambda: main.hub_mode()
    )

    # =========================================================
    # ✅ 패널(통째로 숨김/표시 가능한 버전) - battle_mode 내부 전용
    # =========================================================
    def make_status_panel_ex(canvas, x1, y1, name, max_hp, hp_var):
        PANEL_W = 210
        PANEL_H = 56
        HP_BAR_W = 95
        HP_BAR_H = 10

        x2 = x1 + PANEL_W
        y2 = y1 + PANEL_H

        sh = canvas.create_rectangle(x1 + 3, y1 + 3, x2 + 3, y2 + 3, fill="#4b5563", outline="")
        out = canvas.create_rectangle(x1, y1, x2, y2, fill="#d1d5db", outline="#111827", width=2)

        inner_x1 = x1 + 5
        inner_y1 = y1 + 5
        inner_x2 = x2 - 5
        inner_y2 = y2 - 5
        inn = canvas.create_rectangle(inner_x1, inner_y1, inner_x2, inner_y2, fill="#e5e7eb", outline="#9ca3af")

        name_y = inner_y1 + 14
        name_id = canvas.create_text(inner_x1 + 8, name_y, text=name, anchor="w",
                                     font=PIXEL_FONT, fill="#111827")

        hp_row_y = inner_y1 + 34
        hp_label_x = inner_x1 + 8
        hp_label = canvas.create_text(hp_label_x, hp_row_y, text="HP:",
                                      anchor="w", font=PIXEL_SMALL, fill="#f97316")

        hp_bg_x1 = hp_label_x + 30
        hp_bg_y1 = hp_row_y - HP_BAR_H // 2
        hp_bg_x2 = hp_bg_x1 + HP_BAR_W
        hp_bg_y2 = hp_bg_y1 + HP_BAR_H

        hp_bg = canvas.create_rectangle(hp_bg_x1, hp_bg_y1, hp_bg_x2, hp_bg_y2,
                                        fill="#9ca3af", outline="#111827")

        hp_rect = canvas.create_rectangle(hp_bg_x1, hp_bg_y1, hp_bg_x2, hp_bg_y2,
                                          fill=HP_GREEN, outline="#111827")

        hp_text = canvas.create_text(hp_bg_x2 + 8, hp_row_y, anchor="w",
                                     font=PIXEL_SMALL, fill="#111827",
                                     text=f"{hp_var.get()}/{max_hp}")

        return {
            "items": [sh, out, inn, name_id, hp_label, hp_bg, hp_rect, hp_text],
            "name_id": name_id,
            "rect": hp_rect,
            "x1": hp_bg_x1, "y1": hp_bg_y1, "x2": hp_bg_x2, "y2": hp_bg_y2,
            "hp_text": hp_text,
            "max_hp": max_hp,
            "var": hp_var
        }

    def show_panel(panel, show=True):
        state = "normal" if show else "hidden"
        for it in panel["items"]:
            try:
                canvas.itemconfig(it, state=state)
            except Exception:
                pass

    # =========================================================
    # ✅ 상태창 배치
    # - 왼쪽 위: DENJI
    # - 오른쪽 위: MOBS <-> BOSS 같은 자리에서 스위칭
    # =========================================================
    panel_player = make_status_panel_ex(canvas, 20, 18, "DENJI", PLAYER_MAX, player_hp)

    PANEL_RIGHT_X = W - 240
    PANEL_RIGHT_Y = 18
    panel_mobs = make_status_panel_ex(canvas, PANEL_RIGHT_X, PANEL_RIGHT_Y, "MOBS", MOB_TOTAL_MAX, mob_total_hp)
    panel_boss = make_status_panel_ex(canvas, PANEL_RIGHT_X, PANEL_RIGHT_Y, "BOSS", ENEMY_MAX, enemy_hp)

    # ✅ 시작은 쫄몹 구간
    show_panel(panel_mobs, True)
    show_panel(panel_boss, False)

    # =========================================================
    # ✅ 덴지 피격 판정(hitbox) 줄이기
    # =========================================================
    def get_denji_hitbox():
        cx = denji["pos"]["x"]
        cy = denji["pos"]["y"]
        half_w = int(DENJI_W * 0.22)
        up_h   = int(DENJI_H * 0.33)
        down_h = int(DENJI_H * 0.24)
        return (cx - half_w, cy - up_h, cx + half_w, cy + down_h)

    # =========================================================
    # 전투 로직
    # =========================================================
    boss_active = False
    devil_x, devil_y = W - 150, H // 2
    devil_id = None

    SAFE_TOP = 60
    SAFE_BOTTOM = ground_y - 60

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

    tomatoes = []

    def spawn_tomatoes():
        canvas.tomato_imgs = []
        for _ in range(MOB_COUNT):
            x = W + random.randint(100, 700)
            y = random.randint(SAFE_TOP, SAFE_BOTTOM)

            img = ImageTk.PhotoImage(fit_nearest(tomato_p, 80, 80))
            tid = canvas.create_image(x, y, image=img)
            canvas.tomato_imgs.append(img)

            tomatoes.append({
                "id": tid,
                "x": x,
                "y": y,
                "radius": 26,
                "hp": MOB_HP_EACH,
                "alive": True,
                "vx": -random.uniform(1.2, 2.2),
            })

    spawn_tomatoes()

    enemy_bullets = []

    BULLET_SPEED_ENEMY = 3

    # ✅ 쫄몹 공격 속도 훨씬 느리게
    MOB_FIRE_MIN = 4200
    MOB_FIRE_MAX = 6200
    MOB_FIRE_CHANCE = 0.10

    ENEMY_FIRE_MIN = 1400
    ENEMY_FIRE_MAX = 2000

    def calc_homing_velocity(from_x, from_y, speed, angle_error_deg=0):
        dx = denji["pos"]["x"] - from_x
        dy = denji["pos"]["y"] - from_y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return 0, 0
        ang = math.atan2(dy, dx)
        if angle_error_deg:
            ang += math.radians(random.uniform(-angle_error_deg, angle_error_deg))
        return math.cos(ang) * speed, math.sin(ang) * speed

    def create_enemy_bomb(x, y):
        return canvas.create_image(x, y, image=bomb_tk)

    def clear_enemy_bullets():
        for b in enemy_bullets[:]:
            try:
                canvas.delete(b["id"])
            except Exception:
                pass
        enemy_bullets.clear()

    def spawn_boss():
        nonlocal boss_active, devil_id
        if boss_active or game_over["v"]:
            return

        clear_enemy_bullets()
        boss_active = True
        enemy_hp.set(ENEMY_MAX)

        # ✅ 패널 스위칭: 보스 등장 -> MOBS 숨기고 BOSS 표시
        show_panel(panel_mobs, False)
        show_panel(panel_boss, True)

        for mob in tomatoes:
            if mob["alive"]:
                try:
                    canvas.delete(mob["id"])
                except Exception:
                    pass
                mob["alive"] = False

        devil_id = canvas.create_image(devil_x, devil_y, image=devil_tk)

    def enemy_shoot():
        if gs.current_screen is not frame or game_over["v"]:
            return

        if not boss_active:
            for mob in tomatoes:
                if not mob["alive"]:
                    continue
                if random.random() < MOB_FIRE_CHANCE:
                    bx = mob["x"] - mob["radius"]
                    by = mob["y"]
                    bid = create_enemy_bomb(bx, by)
                    vx, vy = calc_homing_velocity(bx, by, BULLET_SPEED_ENEMY * 0.75, 10)
                    enemy_bullets.append({"id": bid, "vx": vx, "vy": vy})
            gs.root.after(random.randint(MOB_FIRE_MIN, MOB_FIRE_MAX), enemy_shoot)
        else:
            bx = devil_x - 90
            by = devil_y + random.randint(-40, 40)
            bid = create_enemy_bomb(bx, by)
            vx, vy = calc_homing_velocity(bx, by, BULLET_SPEED_ENEMY, 0)
            enemy_bullets.append({"id": bid, "vx": vx, "vy": vy})
            gs.root.after(random.randint(ENEMY_FIRE_MIN, ENEMY_FIRE_MAX), enemy_shoot)

    def victory():
        game_over["v"] = True
        clear_enemy_bullets()
        gs.ticket_count += 1
        gs.stage_cleared[1] = True
        show_victory(
            title="악마 토벌 완료!",
            subtitle="토마토의 악마를 쓰러뜨렸다.",
            reward_text="보상: 뽑기권 1장 획득!",
            on_map=world_map,
            on_hub=main.hub_mode
        )

    def defeat():
        game_over["v"] = True
        clear_enemy_bullets()
        show_defeat(on_map=world_map, on_hub=main.hub_mode)

    def scroll_background(dx, dy):
        if bg_id is None:
            return
        nx = bg_scroll["x"] - dx * bg_scroll["factor"]
        ny = bg_scroll["y"] - dy * bg_scroll["factor"]
        nx = max(-bg_scroll["max_x"], min(bg_scroll["max_x"], nx))
        ny = max(-bg_scroll["max_y"], min(bg_scroll["max_y"], ny))
        bg_scroll["x"], bg_scroll["y"] = nx, ny
        canvas.coords(bg_id, W // 2 + nx, H // 2 + ny)

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

        if dx != 0 or dy != 0:
            scroll_background(dx, dy)

        player_hitbox = get_denji_hitbox()

        # ===== 쫄몹 이동 =====
        if not boss_active:
            for mob in tomatoes:
                if not mob["alive"]:
                    continue
                mob["x"] += mob["vx"]
                if mob["x"] < -80:
                    mob["x"] = W + random.randint(100, 700)
                    mob["y"] = random.randint(SAFE_TOP, SAFE_BOTTOM)
                    mob["vx"] = -random.uniform(1.2, 2.2)
                canvas.coords(mob["id"], mob["x"], mob["y"])

        # ===== 공격(근접) =====
        denji["consume_attack"]()

        if denji["attack"]["just"]:
            ax1 = denji["pos"]["x"] + 25
            ax2 = denji["pos"]["x"] + 25 + denji["attack"]["range_x"]
            ay1 = denji["pos"]["y"] - denji["attack"]["range_y"]
            ay2 = denji["pos"]["y"] + denji["attack"]["range_y"]
            attack_box = (ax1, ay1, ax2, ay2)

            if not boss_active:
                for mob in tomatoes:
                    if not mob["alive"]:
                        continue
                    mb = canvas.bbox(mob["id"])
                    if mb and bbox_intersect(attack_box, mb):
                        mob["alive"] = False
                        mob_total_hp.set(max(0, mob_total_hp.get() - 1))
                        damage_splash(mob["x"], mob["y"] - 20, 1, "#fde68a")
                        try:
                            canvas.delete(mob["id"])
                        except Exception:
                            pass
                        break

            if boss_active and devil_id:
                boss_bbox = canvas.bbox(devil_id)
                if boss_bbox and bbox_intersect(attack_box, boss_bbox):
                    dmg = random.randint(10, 18)
                    enemy_hp.set(max(0, enemy_hp.get() - dmg))
                    damage_splash(devil_x, devil_y - 40, dmg, "#ef4444")

        # ===== 보스 전환 =====
        if (not boss_active) and mob_total_hp.get() <= 0:
            spawn_boss()

        # ===== 적 탄 이동 + 피격 =====
        for e in enemy_bullets[:]:
            canvas.move(e["id"], e["vx"], e["vy"])
            eb = canvas.bbox(e["id"])

            if not eb or eb[2] < 0:
                try:
                    canvas.delete(e["id"])
                except Exception:
                    pass
                enemy_bullets.remove(e)
                continue

            if eb and bbox_intersect(eb, player_hitbox):
                dmg = random.randint(6, 10)
                player_hp.set(max(0, player_hp.get() - dmg))
                damage_splash(denji["pos"]["x"], denji["pos"]["y"] - 40, dmg, "#3b82f6")
                try:
                    canvas.delete(e["id"])
                except Exception:
                    pass
                enemy_bullets.remove(e)

        # ===== 상태창 업데이트 =====
        update_single_bar(canvas, panel_player)
        if boss_active:
            update_single_bar(canvas, panel_boss)
        else:
            update_single_bar(canvas, panel_mobs)

        # 레이어 정리
        if bg_id is not None:
            canvas.tag_lower(bg_id)
        canvas.tag_raise(denji["id"])
        if devil_id:
            canvas.tag_raise(devil_id)

        # 패널은 최상단
        for it in panel_player["items"]:
            canvas.tag_raise(it)
        if boss_active:
            for it in panel_boss["items"]:
                canvas.tag_raise(it)
        else:
            for it in panel_mobs["items"]:
                canvas.tag_raise(it)

        # ===== 승패 =====
        if boss_active and enemy_hp.get() <= 0:
            victory()
            return

        if player_hp.get() <= 0:
            defeat()
            return

        gs.root.after(33, game_loop)

    enemy_shoot()
    game_loop()