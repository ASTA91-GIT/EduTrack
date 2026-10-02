"""
Migrate all public HTML files from Lucide to Font Awesome 6.
- Removes unpkg lucide script tag
- Removes lucide.createIcons() calls
- Replaces <i data-lucide="..."></i> with semantic Font Awesome 6 icons
- Replaces any unicode arrows/checkmarks with Font Awesome icons
- Ensures Font Awesome 6 stylesheet is linked
"""

import os
import glob
import re

MAPPING = {
    "graduation-cap": "fa-solid fa-graduation-cap",
    "layout-dashboard": "fa-solid fa-table-columns",
    "clipboard-check": "fa-solid fa-clipboard-check",
    "clipboard-list": "fa-solid fa-clipboard-list",
    "clipboard-x": "fa-solid fa-clipboard-question",
    "calendar-days": "fa-solid fa-calendar-days",
    "calendar": "fa-solid fa-calendar",
    "calendar-check": "fa-solid fa-calendar-check",
    "calendar-clock": "fa-solid fa-calendar-week",
    "calendar-heart": "fa-solid fa-calendar-star",
    "calendar-off": "fa-solid fa-calendar-xmark",
    "calendar-x": "fa-solid fa-calendar-xmark",
    "presentation": "fa-solid fa-chalkboard-user",
    "folder-open": "fa-solid fa-folder-open",
    "folder-check": "fa-solid fa-folder-closed",
    "folder-x": "fa-solid fa-folder-minus",
    "chart-no-axes-combined": "fa-solid fa-chart-line",
    "chart-spline": "fa-solid fa-chart-line",
    "chart-line": "fa-solid fa-chart-line",
    "chart-pie": "fa-solid fa-chart-pie",
    "line-chart": "fa-solid fa-chart-line",
    "file-bar-chart": "fa-solid fa-file-export",
    "circle-user-round": "fa-solid fa-circle-user",
    "circle-user": "fa-solid fa-circle-user",
    "user": "fa-solid fa-circle-user",
    "users": "fa-solid fa-users",
    "settings": "fa-solid fa-gear",
    "log-out": "fa-solid fa-right-from-bracket",
    "menu": "fa-solid fa-bars",
    "search": "fa-solid fa-magnifying-glass",
    "moon": "fa-solid fa-moon",
    "sun": "fa-solid fa-sun",
    "bell": "fa-solid fa-bell",
    "bell-off": "fa-solid fa-bell-slash",
    "bell-ring": "fa-solid fa-bell",
    "qr-code": "fa-solid fa-qrcode",
    "qrcode": "fa-solid fa-qrcode",
    "scan": "fa-solid fa-qrcode",
    "scan-line": "fa-solid fa-qrcode",
    "map-pin": "fa-solid fa-location-dot",
    "location-crosshairs": "fa-solid fa-location-crosshairs",
    "crosshair": "fa-solid fa-location-crosshairs",
    "check-check": "fa-solid fa-circle-check",
    "check-circle-2": "fa-solid fa-circle-check",
    "check-circle": "fa-solid fa-circle-check",
    "check": "fa-solid fa-check",
    "shield-x": "fa-solid fa-triangle-exclamation",
    "shield-alert": "fa-solid fa-triangle-exclamation",
    "shield-check": "fa-solid fa-shield-halved",
    "alert-triangle": "fa-solid fa-triangle-exclamation",
    "rotate-ccw": "fa-solid fa-rotate",
    "rotate-cw": "fa-solid fa-rotate",
    "refresh-cw": "fa-solid fa-rotate",
    "download": "fa-solid fa-download",
    "file-text": "fa-solid fa-file-lines",
    "file-check-2": "fa-solid fa-file-circle-check",
    "file-spreadsheet": "fa-solid fa-file-excel",
    "file-down": "fa-solid fa-file-arrow-down",
    "play": "fa-solid fa-play",
    "play-circle": "fa-solid fa-circle-play",
    "eye": "fa-solid fa-eye",
    "loader-2": "fa-solid fa-circle-notch fa-spin",
    "loader": "fa-solid fa-circle-notch fa-spin",
    "radio": "fa-solid fa-tower-broadcast",
    "activity": "fa-solid fa-chart-line",
    "history": "fa-solid fa-clock-rotate-left",
    "chevron-right": "fa-solid fa-chevron-right",
    "chevron-left": "fa-solid fa-chevron-left",
    "book-open": "fa-solid fa-book-open",
    "book-x": "fa-solid fa-book",
    "trending-up": "fa-solid fa-arrow-trend-up",
    "trending-down": "fa-solid fa-arrow-trend-down",
    "flame": "fa-solid fa-fire",
    "sparkles": "fa-solid fa-wand-magic-sparkles",
    "maximize": "fa-solid fa-expand",
    "minimize": "fa-solid fa-compress",
    "x": "fa-solid fa-xmark",
    "arrow-right": "fa-solid fa-arrow-right",
    "filter": "fa-solid fa-filter",
    "lock": "fa-solid fa-lock",
    "mail": "fa-solid fa-envelope",
    "key": "fa-solid fa-key",
    "upload": "fa-solid fa-upload",
    "info": "fa-solid fa-circle-info"
}

def migrate_html_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Ensure Font Awesome CDN in <head>
    fa_link = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />'
    if "cdnjs.cloudflare.com/ajax/libs/font-awesome" not in content:
        content = content.replace("</head>", f"  {fa_link}\n</head>")

    # 2. Remove Lucide script
    content = re.sub(r'\s*<script src="https://unpkg\.com/lucide@latest"></script>', '', content)
    content = re.sub(r'\s*<script src="https://cdn\.jsdelivr\.net/npm/lucide@latest[^"]*"></script>', '', content)

    # 3. Remove lucide.createIcons() calls
    content = re.sub(r'lucide\.createIcons\(\);?', '', content)
    content = re.sub(r'if\s*\(\s*window\.lucide\s*\)\s*\{\s*window\.lucide\.createIcons\(\);\s*\}', '', content)
    content = re.sub(r'if\s*\(\s*typeof lucide[^\}]+\}', '', content)

    # 4. Replace <i data-lucide="..."></i> (preserving styles or classes if present)
    def replacer(match):
        attrs = match.group(1)
        name_match = re.search(r'data-lucide=[\"\']([^\"\']+)[\"\']', attrs)
        if not name_match:
            return match.group(0)
        icon_name = name_match.group(1)
        fa_class = MAPPING.get(icon_name, f"fa-solid fa-{icon_name}")
        
        # Remove data-lucide="..." from attrs
        cleaned_attrs = re.sub(r'data-lucide=[\"\'][^\"\']+[\"\']\s*', '', attrs).strip()
        
        # If class exists in cleaned_attrs, append fa_class, else add class="fa_class"
        if 'class=' in cleaned_attrs:
            cleaned_attrs = re.sub(r'class=[\"\']([^\"\']+)[\"\']', rf'class="\1 {fa_class}"', cleaned_attrs)
        else:
            cleaned_attrs = f'class="{fa_class}" ' + cleaned_attrs
        
        return f'<i {cleaned_attrs.strip()}></i>'

    content = re.sub(r'<i\s+([^>]*data-lucide=[^>]*)></i>', replacer, content)

    # 5. Check if any JS string creates <i data-lucide="...">
    def js_string_replacer(match):
        icon_name = match.group(1)
        fa_class = MAPPING.get(icon_name, f"fa-solid fa-{icon_name}")
        return f'<i class=\\"{fa_class}\\"'

    content = re.sub(r'<i data-lucide=\\\"([^\\\"]+)\\\"', js_string_replacer, content)
    content = re.sub(r'<i data-lucide=[\'\"]([^\'\"]+)[\'\"]', lambda m: f'<i class="{MAPPING.get(m.group(1), f"fa-solid fa-{m.group(1)}")}"', content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Migrated: {os.path.basename(file_path)}")

def main():
    files = glob.glob("frontend/public/*.html")
    for f in sorted(files):
        migrate_html_file(f)
    print(f"Processed {len(files)} files.")

if __name__ == "__main__":
    main()
