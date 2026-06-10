import tkinter as tk
import math, time, threading, random, os
from pynput import mouse, keyboard
try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

# ── State ──────────────────────────────────────────────────────────────────
mouse_x, mouse_y   = 0, 0
is_typing          = False
type_timer         = None
heat               = 0
last_key_time      = 0
paw_left           = False
dragging           = False
drag_offset_x      = drag_offset_y = 0
blink_state        = False
last_activity_time = time.time()

IDLE_SLEEP_AFTER = 120
bob_offset       = 0.0
zzz_index        = 0

STRETCH_EVERY  = 30 * 60
POMODORO_WORK  = 25 * 60
POMODORO_BREAK =  5 * 60
stretch_waving  = False
pomodoro_active = False
pomodoro_start  = 0.0
pomodoro_phase  = "work"

# ── Hearts ────────────────────────────────────────────────────────────────
hearts = []   # [{x, y, born, size, screen}]
heart_fullscreen = False  # True for 2s after heavy scratch

# ── Wander ────────────────────────────────────────────────────────────────
WANDER_EVERY = 30 * 60   # move to new spot every 30 min
wander_target_x = None
wander_target_y = None
wandering = False

# ── Color schemes ─────────────────────────────────────────────────────────
COLORS = {
    "Classic": ("#F5DEB3", "#8B6914"),
    "Pink":    ("#FFB6C1", "#CC6677"),
    "Grey":    ("#C8C8C8", "#555555"),
    "Blue":    ("#AADDFF", "#2266AA"),
    "White":   ("#F5F5F0", "#888888"),
}
current_color = "Classic"

W, H = 130, 155

# ── Sound ─────────────────────────────────────────────────────────────────
try:
    import pygame
    pygame.mixer.init()
    BASE = os.path.dirname(os.path.abspath(__file__))
    MEOW_PATH = os.path.join(BASE, "meow.wav")
    _sound_ready = os.path.exists(MEOW_PATH)
except:
    _sound_ready = False

def play_meow():
    if not _sound_ready: return
    try:
        sound = pygame.mixer.Sound(MEOW_PATH)
        sound.set_volume(0.6)
        sound.play()
    except: pass

def clamp(v, lo, hi): return max(lo, min(hi, v))

def get_eye_offset(eye_cx, eye_cy, win_x, win_y):
    tx = mouse_x - (win_x + eye_cx)
    ty = mouse_y - (win_y + eye_cy)
    dist = math.hypot(tx, ty)
    if dist == 0: return 0, 0
    scale = min(3, dist * 0.15) / max(dist, 1)
    return tx * scale, ty * scale

def is_sleeping(): return (time.time() - last_activity_time) > IDLE_SLEEP_AFTER
def is_idle():     return not is_typing and not is_sleeping()

# ── Draw ──────────────────────────────────────────────────────────────────
def draw_cat(canvas, win_x, win_y):
    canvas.delete("all")
    sleeping = is_sleeping()
    body_color, outline_color = COLORS[current_color]

    # Heat overrides color
    if heat >= 7:   body_color, outline_color = "#FF6B6B", "#CC3333"
    elif heat >= 4: body_color, outline_color = "#FFB347", "#CC7700"

    # Break color
    if pomodoro_active and pomodoro_phase == "break" and heat < 4:
        body_color, outline_color = "#90EE90", "#2E8B57"

    bob = int(bob_offset) if (is_idle() or sleeping) else 0

    # ZZZ
    if sleeping:
        zzz_chars = ["z", "z z", "Z z z"]
        frame = zzz_index % 3
        canvas.create_text(90, 8+frame, text=zzz_chars[frame],
                           font=("Arial", [9,10,12][frame], "bold"), fill="#8888CC")

    # Tail
    canvas.create_arc(10, 83+bob, 55, 133+bob, start=0, extent=200,
                      style=tk.ARC, outline=outline_color, width=5)
    # Body
    canvas.create_oval(25, 68+bob, 100, 123+bob,
                       fill=body_color, outline=outline_color, width=2)
    # Head
    canvas.create_oval(28, 25+bob, 97, 80+bob,
                       fill=body_color, outline=outline_color, width=2)
    # Ears
    canvas.create_polygon(32,45+bob,28,12+bob,52,30+bob,
                          fill=body_color,outline=outline_color,width=2)
    canvas.create_polygon(36,42+bob,32,18+bob,50,33+bob,
                          fill="#FFB6C1",outline="#FFB6C1")
    canvas.create_polygon(93,45+bob,97,12+bob,73,30+bob,
                          fill=body_color,outline=outline_color,width=2)
    canvas.create_polygon(89,42+bob,93,18+bob,75,33+bob,
                          fill="#FFB6C1",outline="#FFB6C1")

    # Eyes
    eye_ly = eye_ry = 49+bob
    eye_lx, eye_rx = 47, 78
    eye_r = 8
    for ex,ey in [(eye_lx,eye_ly),(eye_rx,eye_ry)]:
        canvas.create_oval(ex-eye_r,ey-eye_r,ex+eye_r,ey+eye_r,
                           fill="white",outline=outline_color,width=1)

    if sleeping or blink_state:
        for ex,ey in [(eye_lx,eye_ly),(eye_rx,eye_ry)]:
            canvas.create_arc(ex-eye_r+1,ey-4,ex+eye_r-1,ey+6,
                              start=0,extent=180,style=tk.ARC,
                              outline=outline_color,width=2)
    else:
        for ex,ey in [(eye_lx,eye_ly),(eye_rx,eye_ry)]:
            dx,dy = get_eye_offset(ex,ey,win_x,win_y)
            px,py = ex+dx, ey+dy
            canvas.create_oval(px-4,py-4,px+4,py+4,fill="#222222",outline="")
            canvas.create_oval(px-1.5,py-2,px+1.5,py+1,fill="white",outline="")

    # Nose
    canvas.create_polygon(60,57+bob,65,57+bob,62,61+bob,
                          fill="#FFB6C1",outline="#CC8899")
    # Mouth
    canvas.create_arc(55,59+bob,63,67+bob,start=180,extent=180,
                      style=tk.ARC,outline=outline_color,width=1)
    canvas.create_arc(62,59+bob,70,67+bob,start=180,extent=180,
                      style=tk.ARC,outline=outline_color,width=1)
    # Whiskers
    canvas.create_line(10,55+bob,47,57+bob,fill=outline_color,width=1)
    canvas.create_line(10,61+bob,47,60+bob,fill=outline_color,width=1)
    canvas.create_line(78,57+bob,115,55+bob,fill=outline_color,width=1)
    canvas.create_line(78,60+bob,115,61+bob,fill=outline_color,width=1)

    # Paws
    wave = stretch_waving and int(time.time()*6)%2==0
    left_y  = 115+bob if ((is_typing and paw_left) or wave) else 122+bob
    right_y = 115+bob if (is_typing and not paw_left) else 122+bob
    canvas.create_oval(22, left_y,  48, 138+bob, fill=body_color, outline=outline_color, width=2)
    canvas.create_oval(82, right_y, 108, 138+bob, fill=body_color, outline=outline_color, width=2)

    # Overheat steam
    if heat >= 7:
        for i,(sx,sy) in enumerate([(45,17),(63,12),(81,17)]):
            off = 4 if (int(time.time()*3)+i)%2==0 else 0
            canvas.create_text(sx,sy-off,text="~",
                               font=("Arial",10,"bold"),fill="#AAAAFF")

    # Pomodoro bar
    if pomodoro_active:
        elapsed = time.time()-pomodoro_start
        total = POMODORO_WORK if pomodoro_phase=="work" else POMODORO_BREAK
        ratio = clamp(1-elapsed/total,0,1)
        bar_w = int(110*ratio)
        col = "#FF6B6B" if pomodoro_phase=="work" else "#90EE90"
        canvas.create_rectangle(5,H-12,115,H-4,fill="#444",outline="")
        canvas.create_rectangle(5,H-12,5+bar_w,H-4,fill=col,outline="")
        mins = max(0,int((total-elapsed)/60))
        secs = max(0,int((total-elapsed)%60))
        label = "WORK" if pomodoro_phase=="work" else "BREAK"
        canvas.create_text(60,H-17,text=f"{label} {mins:02d}:{secs:02d}",
                           font=("Arial",7,"bold"),fill="#CCCCCC")

    # Hearts
    now = time.time()
    alive = []
    for h in hearts:
        age = now - h["born"]
        if age > 1.2: continue
        hy = h["y"] - int(age*45)
        hx = h["x"] + int(math.sin(age*6)*5)
        canvas.create_text(hx, hy, text="♥",
                           font=("Arial", h["size"], "bold"), fill="#FF6B8A")
        alive.append(h)
    hearts[:] = alive

# ── Toast ──────────────────────────────────────────────────────────────────
def show_toast(title, message):
    toast = tk.Tk()
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)
    toast.configure(bg="#2C2C2C")
    sw = toast.winfo_screenwidth()
    sh = toast.winfo_screenheight()
    tw, th = 260, 70
    toast.geometry(f"{tw}x{th}+{sw-tw-20}+{sh-th-60}")
    tk.Label(toast,text=title,bg="#2C2C2C",fg="#FFFFFF",
             font=("Arial",11,"bold")).pack(anchor="w",padx=12,pady=(10,0))
    tk.Label(toast,text=message,bg="#2C2C2C",fg="#AAAAAA",
             font=("Arial",9)).pack(anchor="w",padx=12)
    toast.after(4000,toast.destroy)
    toast.mainloop()

# ── Tray icon ─────────────────────────────────────────────────────────────
def make_tray_icon_image():
    """Draw a tiny cat face as the tray icon."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Body circle
    d.ellipse([8, 20, 56, 58], fill=(255, 200, 120), outline=(100, 60, 10), width=2)
    # Ears
    d.polygon([(12,24),(8,8),(22,18)], fill=(255,200,120), outline=(100,60,10))
    d.polygon([(52,24),(56,8),(42,18)], fill=(255,200,120), outline=(100,60,10))
    # Eyes
    d.ellipse([18,28,30,40], fill="white", outline=(100,60,10), width=1)
    d.ellipse([34,28,46,40], fill="white", outline=(100,60,10), width=1)
    d.ellipse([22,31,28,37], fill=(30,20,10))
    d.ellipse([36,31,42,37], fill=(30,20,10))
    # Nose
    d.polygon([(30,43),(34,43),(32,46)], fill=(255,160,180))
    return img

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    global blink_state, bob_offset, zzz_index, last_activity_time
    global stretch_waving, pomodoro_active, pomodoro_start, pomodoro_phase
    global current_color, hearts, heart_fullscreen
    global wander_target_x, wander_target_y, wandering

    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-transparentcolor", "#010101")
    root.configure(bg="#010101")
    root.geometry(f"{W}x{H}+1200+600")

    canvas = tk.Canvas(root,width=W,height=H,bg="#010101",highlightthickness=0)
    canvas.pack()

    # ── Redraw ────────────────────────────────────────────────
    def redraw():
        draw_cat(canvas, root.winfo_x(), root.winfo_y())
        root.after(40, redraw)
    redraw()

    # ── Drag ──────────────────────────────────────────────────
    def on_press(e):
        global dragging, drag_offset_x, drag_offset_y
        dragging = True
        drag_offset_x = e.x_root - root.winfo_x()
        drag_offset_y = e.y_root - root.winfo_y()

    def on_drag(e):
        if dragging:
            root.geometry(f"+{e.x_root-drag_offset_x}+{e.y_root-drag_offset_y}")

    def on_release(e):
        global dragging; dragging = False

    canvas.bind("<ButtonPress-1>",  on_press)
    canvas.bind("<B1-Motion>",      on_drag)
    canvas.bind("<ButtonRelease-1>",on_release)

    # ── Fullscreen hearts overlay ─────────────────────────────
    heart_win = tk.Toplevel(root)
    heart_win.overrideredirect(True)
    heart_win.attributes("-topmost", True)
    heart_win.attributes("-transparentcolor", "#010101")
    heart_win.configure(bg="#010101")
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    heart_win.geometry(f"{sw}x{sh}+0+0")
    heart_canvas = tk.Canvas(heart_win, width=sw, height=sh,
                             bg="#010101", highlightthickness=0)
    heart_canvas.pack()
    heart_win.lower(root)   # keep behind cat window normally

    screen_hearts = []   # fullscreen floating hearts

    def redraw_hearts():
        heart_canvas.delete("all")
        now = time.time()
        alive = []
        for h in screen_hearts:
            age = now - h["born"]
            if age > 1.5: continue
            hy = h["y"] - int(age * 60)
            hx = h["x"] + int(math.sin(age * 5) * 8)
            heart_canvas.create_text(hx, hy, text="♥",
                                     font=("Arial", h["size"], "bold"),
                                     fill="#FF6B8A")
            alive.append(h)
        screen_hearts[:] = alive
        if screen_hearts:
            heart_win.lift()
            root.lift()
        else:
            heart_win.lower(root)
        heart_win.after(40, redraw_hearts)

    redraw_hearts()

    # ── Scratch = hearts ──────────────────────────────────────
    scratch_count = [0]
    last_scratch_time = [0]

    def on_scratch(e):
        now = time.time()
        # Local hearts on cat
        for _ in range(3):
            hearts.append({
                "x": e.x + random.randint(-15, 15),
                "y": e.y + random.randint(-10, 5),
                "born": now,
                "size": random.choice([10, 12, 14])
            })
        # Count rapid scratches → trigger fullscreen hearts
        if now - last_scratch_time[0] < 0.1:
            scratch_count[0] += 1
        else:
            scratch_count[0] = 0
        last_scratch_time[0] = now

        # After 8 rapid scratch moves → explode hearts across screen
        if scratch_count[0] >= 8:
            scratch_count[0] = 0
            cat_x = root.winfo_x()
            cat_y = root.winfo_y()
            for _ in range(40):
                screen_hearts.append({
                    "x": random.randint(0, sw),
                    "y": random.randint(sh // 4, sh),
                    "born": now + random.uniform(0, 0.4),
                    "size": random.choice([14, 18, 22, 28])
                })

    canvas.bind("<B1-Motion>", lambda e: (on_drag(e), on_scratch(e)))

    # ── Wander loop ───────────────────────────────────────────
    def wander_loop():
        global wander_target_x, wander_target_y, wandering
        while True:
            time.sleep(WANDER_EVERY)
            # Pick random spot on screen, avoid edges
            tx = random.randint(50, sw - W - 50)
            ty = random.randint(50, sh - H - 100)
            wander_target_x = tx
            wander_target_y = ty
            wandering = True
            # Animate cat sliding to new position
            def slide():
                global wandering
                steps = 40
                cx = root.winfo_x()
                cy = root.winfo_y()
                dx = (wander_target_x - cx) / steps
                dy = (wander_target_y - cy) / steps
                for _ in range(steps):
                    cx += dx
                    cy += dy
                    root.geometry(f"+{int(cx)}+{int(cy)}")
                    time.sleep(0.03)
                wandering = False
            threading.Thread(target=slide, daemon=True).start()

    threading.Thread(target=wander_loop, daemon=True).start()

    # ── Right-click menu ──────────────────────────────────────
    def show_menu(e):
        menu = tk.Menu(root, tearoff=0, bg="#2C2C2C", fg="white",
                       activebackground="#555", activeforeground="white",
                       font=("Arial", 10))

        # Pomodoro toggle
        pom_label = "Stop Pomodoro" if pomodoro_active else "Start Pomodoro"
        def toggle_pom():
            global pomodoro_active, pomodoro_start, pomodoro_phase
            if pomodoro_active:
                pomodoro_active = False
                threading.Thread(target=show_toast,
                    args=("Pomodoro stopped","Timer cancelled."),daemon=True).start()
            else:
                pomodoro_active = True
                pomodoro_start = time.time()
                pomodoro_phase = "work"
                threading.Thread(target=show_toast,
                    args=("Pomodoro started!","25 min focus session."),daemon=True).start()
        menu.add_command(label=pom_label, command=toggle_pom)
        menu.add_separator()

        # Color submenu
        color_menu = tk.Menu(menu, tearoff=0, bg="#2C2C2C", fg="white",
                             activebackground="#555", activeforeground="white",
                             font=("Arial", 10))
        for name in COLORS:
            def set_color(n=name):
                global current_color
                current_color = n
            label = f"✓ {name}" if name == current_color else f"  {name}"
            color_menu.add_command(label=label, command=set_color)
        menu.add_cascade(label="Color", menu=color_menu)
        menu.add_separator()
        menu.add_command(label="Quit", command=root.destroy)

        try:
            menu.tk_popup(e.x_root, e.y_root)
        finally:
            menu.grab_release()

    canvas.bind("<Button-3>", show_menu)

    # ── Double-click → Pomodoro ───────────────────────────────
    def on_double(e):
        global pomodoro_active, pomodoro_start, pomodoro_phase
        if pomodoro_active:
            pomodoro_active = False
        else:
            pomodoro_active = True
            pomodoro_start = time.time()
            pomodoro_phase = "work"
    canvas.bind("<Double-Button-1>", on_double)

    # ── Blink ─────────────────────────────────────────────────
    def blink_loop():
        global blink_state
        while True:
            time.sleep(4)
            if not is_sleeping():
                blink_state = True; time.sleep(0.12); blink_state = False
    threading.Thread(target=blink_loop,daemon=True).start()

    # ── Bob ───────────────────────────────────────────────────
    def bob_loop():
        global bob_offset, zzz_index
        t = 0
        while True:
            speed = 0.04 if is_sleeping() else 0.07
            t += speed
            bob_offset = math.sin(t)*3
            if is_sleeping(): zzz_index = int(t*0.4)%3
            time.sleep(0.04)
    threading.Thread(target=bob_loop,daemon=True).start()

    # ── Stretch reminder ──────────────────────────────────────
    def stretch_loop():
        global stretch_waving
        time.sleep(STRETCH_EVERY)
        while True:
            stretch_waving = True
            threading.Thread(target=show_toast,
                args=("Stretch time!","Stand up and stretch for 1 minute."),
                daemon=True).start()
            time.sleep(5); stretch_waving = False
            time.sleep(STRETCH_EVERY)
    threading.Thread(target=stretch_loop,daemon=True).start()

    # ── Pomodoro loop ─────────────────────────────────────────
    def pomodoro_loop():
        global pomodoro_active, pomodoro_start, pomodoro_phase
        while True:
            time.sleep(1)
            if not pomodoro_active: continue
            elapsed = time.time()-pomodoro_start
            limit = POMODORO_WORK if pomodoro_phase=="work" else POMODORO_BREAK
            if elapsed >= limit:
                if pomodoro_phase=="work":
                    pomodoro_phase="break"; pomodoro_start=time.time()
                    threading.Thread(target=show_toast,
                        args=("Break time!","5 min break."),daemon=True).start()
                else:
                    pomodoro_phase="work"; pomodoro_start=time.time()
                    threading.Thread(target=show_toast,
                        args=("Back to work!","25 min focus session."),daemon=True).start()
    threading.Thread(target=pomodoro_loop,daemon=True).start()

    # ── Mouse tracker ─────────────────────────────────────────
    def on_move(x,y):
        global mouse_x, mouse_y, last_activity_time
        mouse_x, mouse_y = x, y
        last_activity_time = time.time()
    mouse.Listener(on_move=on_move,daemon=True).start()

    # ── Keyboard tracker ──────────────────────────────────────
    def on_key(key):
        global is_typing, type_timer, heat, last_key_time, paw_left, last_activity_time
        now = time.time()
        paw_left = not paw_left
        last_activity_time = now
        heat = clamp(heat+(1 if now-last_key_time<0.3 else -1),0,10)
        last_key_time = now
        is_typing = True
        if type_timer: type_timer.cancel()
        type_timer = threading.Timer(1.2, lambda: globals().update(is_typing=False))
        type_timer.daemon = True
        type_timer.start()
    keyboard.Listener(on_press=on_key,daemon=True).start()

    # ── System tray icon ──────────────────────────────────────
    if TRAY_AVAILABLE:
        def on_tray_quit(icon, item):
            icon.stop()
            root.destroy()

        def on_tray_show(icon, item):
            root.deiconify()
            root.lift()

        def on_tray_pomodoro(icon, item):
            global pomodoro_active, pomodoro_start, pomodoro_phase
            if pomodoro_active:
                pomodoro_active = False
                threading.Thread(target=show_toast,
                    args=("Pomodoro stopped","Timer cancelled."),daemon=True).start()
            else:
                pomodoro_active = True
                pomodoro_start = time.time()
                pomodoro_phase = "work"
                threading.Thread(target=show_toast,
                    args=("Pomodoro started!","25 min focus session."),daemon=True).start()

        tray_menu = pystray.Menu(
            pystray.MenuItem("🐱 Meeow", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Show Cat", on_tray_show),
            pystray.MenuItem("Toggle Pomodoro", on_tray_pomodoro),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", on_tray_quit),
        )

        tray_icon = pystray.Icon(
            "Meeow",
            make_tray_icon_image(),
            "Meeow 🐱",
            tray_menu
        )

        threading.Thread(target=tray_icon.run, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    main()
