import tkinter as tk
import random

root = tk.Tk()
root.title("Chainsaw Shooter")
canvas = tk.Canvas(root, width=600, height=400, bg="black")
canvas.pack()

player = canvas.create_rectangle(270, 350, 330, 390, fill="red")
bullets = []
enemies = []

def move_left(event):
    canvas.move(player, -20, 0)

def move_right(event):
    canvas.move(player, 20, 0)

def shoot(event):
    x1, y1, x2, y2 = canvas.coords(player)
    bullet = canvas.create_rectangle(x1+20, y1, x1+30, y1-10, fill="yellow")
    bullets.append(bullet)

def create_enemy():
    x = random.randint(50, 550)
    enemy = canvas.create_oval(x, 0, x+30, 30, fill="purple")
    enemies.append(enemy)
    root.after(1500, create_enemy)

def game_loop():
    # 총알 이동
    for b in bullets:
        canvas.move(b, 0, -10)
    # 적 이동
    for e in enemies:
        canvas.move(e, 0, 5)
    root.after(50, game_loop)

root.bind("<Left>", move_left)
root.bind("<Right>", move_right)
root.bind("<space>", shoot)

create_enemy()
game_loop()
root.mainloop()