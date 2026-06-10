<div align="center">

```
    /\_____/\
   /  o   o  \
  ( ==  ^  == )
   )         (
  (           )
 ( (  )   (  ) )
(__(__)___(__)__)
```

# 🐱 Meeow

### *A desktop cat companion that lives on your screen*

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square&logo=windows)](https://microsoft.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Made with love](https://img.shields.io/badge/Made%20with-❤️-red?style=flat-square)](https://github.com/siddujain525-star/Meeow)

</div>

---

<div align="center">

## ✨ What is Meeow?

**Meeow** is a free, open-source desktop companion cat that sits on top of all your windows.  
She watches your cursor, reacts to your typing, falls asleep when you're idle,  
and reminds you to take breaks — all while looking adorable. 🐾

*Built from scratch in Python. No subscriptions. No installs. Just a cat.*

</div>

---

## 🎮 Features

| Feature | Description |
|--------|-------------|
| 👀 **Eye Tracking** | Eyes follow your cursor in real time |
| ⌨️ **Typing Reactions** | Paws tap-alternate as you type |
| 🔥 **Overheat Mode** | Types fast? Cat turns red with steam |
| 💤 **Sleep Mode** | Idle for 2 min → cat closes eyes and snores zzz |
| 💗 **Scratch Hearts** | Drag slowly = floating hearts. Drag fast = heart explosion across the whole screen |
| 🧘 **Stretch Reminder** | Every 30 min, cat waves and reminds you to stand up |
| 🍅 **Pomodoro Timer** | Double-click to start 25/5 min work-break cycles with a progress bar |
| 🎨 **Color Picker** | Right-click → choose Classic, Pink, Grey, Blue, or White |
| 🚀 **Auto-Launch** | Starts automatically when Windows boots |
| 🖱️ **Draggable** | Move her anywhere on screen |

---

## 🚀 Quick Start

### Option 1 — Run from source

```bash
# 1. Clone the repo
git clone https://github.com/siddujain525-star/Meeow.git
cd Meeow

# 2. Install dependency
pip install pynput

# 3. Run
python cat.py
```

### Option 2 — Build your own .exe

```bash
pip install pynput
python build.py
# → DesktopCat.exe appears in /dist
```

### Option 3 — Auto-launch on startup

```bash
python install.py         # adds to Windows startup
python install.py remove  # removes from startup
```

---

## 🎮 Controls

| Action | Result |
|--------|--------|
| `Left-click + drag` | Move the cat |
| `Drag slowly` | Floating hearts ♥ |
| `Drag fast` | Heart explosion across screen 💥 |
| `Double-click` | Start / stop Pomodoro timer |
| `Right-click` | Menu → color, pomodoro, quit |

---

## 🗂️ Project Structure

```
Meeow/
├── cat.py          # Main app — all the magic lives here
├── build.py        # Builds cat.py into a standalone .exe
├── install.py      # Adds/removes Windows startup entry
└── requirements.txt
```

---

## 🛠️ Built With

- **Python** + **Tkinter** — drawing, animation, window management
- **pynput** — global mouse + keyboard hooks
- **PyInstaller** — packaging into .exe
- Zero external assets — the cat is drawn entirely in code

---

## 🧠 How It Works

The cat is drawn **frame by frame using Tkinter Canvas** — no images, no sprites.  
Every 40ms a new frame is rendered with updated eye positions, paw states, and colors.  
A sine wave drives the breathing bob. Global hooks via `pynput` track keypresses and mouse movement system-wide so the cat reacts even when she's not in focus.

---

## 📸 Stages of Development

```
Stage 1 → Basic cat, eye tracking, typing paws
Stage 2 → Sleep mode, breathing animation
Stage 3 → Stretch reminder, Pomodoro timer
Stage 4 → Scratch hearts, right-click menu, color picker, .exe build, auto-launch
Stage 5 → Full-screen heart explosion, wandering behavior
```

---

<div align="center">

**Made with 🐾 by [Siddharth Jain](https://github.com/siddujain525-star)**

*If you liked this project, leave a ⭐ — it means a lot!*

</div>