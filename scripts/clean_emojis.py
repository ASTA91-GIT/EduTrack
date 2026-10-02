"""
Scan and replace emoji in public HTML files with Font Awesome 6 icons.
"""

import glob
import os
import re

EMOJI_MAP = {
    "\U0001f4cd": '<i class="fa-solid fa-location-dot"></i>',        # 📍
    "\u2705": '<i class="fa-solid fa-circle-check"></i>',             # ✅
    "\u274c": '<i class="fa-solid fa-circle-xmark"></i>',             # ❌
    "\u26a0\ufe0f": '<i class="fa-solid fa-triangle-exclamation"></i>',# ⚠️
    "\u26a0": '<i class="fa-solid fa-triangle-exclamation"></i>',     # ⚠️
    "\u26a1": '<i class="fa-solid fa-bolt"></i>',                     # ⚡
    "\U0001f525": '<i class="fa-solid fa-fire"></i>',                 # 🔥
    "\U0001f4cb": '<i class="fa-solid fa-clipboard"></i>',            # 📋
    "\U0001f4c5": '<i class="fa-solid fa-calendar"></i>',             # 📅
    "\U0001f4ca": '<i class="fa-solid fa-chart-simple"></i>',         # 📊
    "\U0001f4c8": '<i class="fa-solid fa-chart-line"></i>',           # 📈
    "\U0001f4c9": '<i class="fa-solid fa-chart-line-down"></i>',      # 📉
    "\U0001f50d": '<i class="fa-solid fa-magnifying-glass"></i>',     # 🔍
    "\U0001f514": '<i class="fa-solid fa-bell"></i>',                 # 🔔
    "\U0001f393": '<i class="fa-solid fa-graduation-cap"></i>',       # 🎓
    "\U0001f4bb": '<i class="fa-solid fa-laptop"></i>',               # 💻
    "\U0001f4da": '<i class="fa-solid fa-books"></i>',                # 📚
    "\U0001f4d6": '<i class="fa-solid fa-book-open"></i>',            # 📖
    "\U0001f4dd": '<i class="fa-solid fa-pen-to-square"></i>',        # 📝
    "\U0001f680": '<i class="fa-solid fa-rocket"></i>',               # 🚀
    "\U0001f4e2": '<i class="fa-solid fa-bullhorn"></i>',             # 📢
    "\U0001f389": '<i class="fa-solid fa-bullhorn"></i>',             # 🎉
    "\u2192": '<i class="fa-solid fa-arrow-right"></i>',              # →
    "\u2190": '<i class="fa-solid fa-arrow-left"></i>',               # ←
    "\u2714": '<i class="fa-solid fa-check"></i>',                    # ✔
    "\u2713": '<i class="fa-solid fa-check"></i>',                    # ✓
    "\u2715": '<i class="fa-solid fa-xmark"></i>',                    # ✕
    "\u2716": '<i class="fa-solid fa-xmark"></i>',                    # ✖
}

def clean_emojis():
    files = glob.glob("frontend/public/*.html")
    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            content = fp.read()
        
        modified = False
        for emo, replacement in EMOJI_MAP.items():
            if emo in content:
                content = content.replace(emo, replacement)
                modified = True
        
        if modified:
            with open(f, "w", encoding="utf-8") as fp:
                fp.write(content)
            print(f"Cleaned emoji in: {os.path.basename(f)}")

if __name__ == "__main__":
    clean_emojis()
