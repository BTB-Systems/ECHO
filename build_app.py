import os
import re
from PIL import Image, ImageDraw, ImageFont

ECHO_DIR = r"C:\Users\darren.ruddick\OneDrive - Manchester University NHS FT\DTS\Github\ECHO"
ICONS_DIR = os.path.join(ECHO_DIR, "icons")
WWW_DIR = os.path.join(ECHO_DIR, "www")

os.makedirs(ICONS_DIR, exist_ok=True)
os.makedirs(WWW_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. ICON GENERATION (High-Resolution Terminal Aesthetic)
# ---------------------------------------------------------------------------
def generate_icon(size, filename):
    img = Image.new("RGBA", (size, size), (5, 5, 5, 255))
    draw = ImageDraw.Draw(img)
    
    # Outer rounded rectangle border with terminal green
    margin = int(size * 0.06)
    radius = int(size * 0.22)
    border_width = max(2, int(size * 0.025))
    
    # Rounded background
    draw.rounded_rectangle(
        [(margin, margin), (size - margin, size - margin)],
        radius=radius,
        outline=(0, 255, 0, 180),
        width=border_width
    )
    
    # Inner border glow accent
    inner_margin = margin + border_width + max(2, int(size * 0.015))
    inner_radius = max(4, radius - border_width - 2)
    draw.rounded_rectangle(
        [(inner_margin, inner_margin), (size - inner_margin, size - inner_margin)],
        radius=inner_radius,
        outline=(0, 255, 0, 40),
        width=1
    )
    
    # Try finding standard monospace font, fallback to default
    font_size = int(size * 0.5)
    font = None
    font_candidates = [
        "consola.ttf", "consolas.ttf", "cour.ttf", "arialbd.ttf", 
        "C:\\Windows\\Fonts\\consola.ttf", "C:\\Windows\\Fonts\\cour.ttf"
    ]
    for fc in font_candidates:
        try:
            font = ImageFont.truetype(fc, font_size)
            break
        except Exception:
            continue
    
    if font is None:
        font = ImageFont.load_default()
    
    text = "E_"
    # Measure text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    x = (size - text_w) // 2
    y = (size - text_h) // 2 - int(size * 0.04)
    
    # Subtle glow behind text
    for offset in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1)]:
        draw.text((x + offset[0], y + offset[1]), text, font=font, fill=(0, 255, 0, 45))
        
    # Main crisp neon text
    draw.text((x, y), text, font=font, fill=(0, 255, 0, 255))
    
    out_path = os.path.join(ICONS_DIR, filename)
    img.save(out_path, "PNG")
    print(f"[+] Generated {filename} ({size}x{size})")

generate_icon(180, "apple-touch-icon.png")
generate_icon(192, "icon-192.png")
generate_icon(512, "icon-512.png")

# Generate SVG vector icon
svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <rect width="512" height="512" rx="112" fill="#050505"/>
  <rect x="30" y="30" width="452" height="452" rx="92" fill="none" stroke="#00ff00" stroke-width="14" opacity="0.8"/>
  <rect x="48" y="48" width="416" height="416" rx="76" fill="none" stroke="#00ff00" stroke-width="2" opacity="0.25"/>
  <text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle" font-size="260" font-weight="bold" fill="#00ff00" font-family="'Menlo', 'Monaco', 'Courier New', monospace" letter-spacing="-10">E_</text>
</svg>"""

with open(os.path.join(ICONS_DIR, "icon.svg"), "w", encoding="utf-8") as f:
    f.write(svg_content)
print("[+] Generated icon.svg")

# ---------------------------------------------------------------------------
# 2. WEB APP MANIFEST (manifest.webmanifest)
# ---------------------------------------------------------------------------
manifest_content = """{
  "name": "ECHO Mental Health Coach & Mentor",
  "short_name": "ECHO",
  "description": "Offline-first clinical mental health coach and grounding companion for NHS and emergency responders.",
  "start_url": "./index.html",
  "scope": "./",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#000000",
  "theme_color": "#000000",
  "categories": ["health", "lifestyle", "medical"],
  "icons": [
    {
      "src": "icons/apple-touch-icon.png",
      "sizes": "180x180",
      "type": "image/png"
    },
    {
      "src": "icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "icons/icon.svg",
      "sizes": "512x512",
      "type": "image/svg+xml"
    }
  ]
}
"""

with open(os.path.join(ECHO_DIR, "manifest.webmanifest"), "w", encoding="utf-8") as f:
    f.write(manifest_content)
print("[+] Generated manifest.webmanifest")

# ---------------------------------------------------------------------------
# 3. OFFLINE SERVICE WORKER (sw.js)
# ---------------------------------------------------------------------------
sw_content = """// ECHO Clinical Coach - Offline Cache Service Worker
const CACHE_NAME = 'echo-standalone-v1.1';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icons/apple-touch-icon.png',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon.svg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  // Offline-first strategy
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request).then((networkResponse) => {
        if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
          return networkResponse;
        }
        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
        return networkResponse;
      }).catch(() => {
        // Fallback for navigation requests
        if (event.request.mode === 'navigate') {
          return caches.match('./index.html');
        }
      });
    })
  );
});
"""

with open(os.path.join(ECHO_DIR, "sw.js"), "w", encoding="utf-8") as f:
    f.write(sw_content)
print("[+] Generated sw.js")

# ---------------------------------------------------------------------------
# 4. EXTRACT AND SANITISE INDEX.HTML
# ---------------------------------------------------------------------------
raw_html_path = os.path.join(ECHO_DIR, "echo.html")
with open(raw_html_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Line index 605 is line 606 (<meta charset="UTF-8">)
app_lines = lines[605:]
app_body = "".join(app_lines)

# Inject manifest, icon references, and Service Worker registration
head_prefix = """<!DOCTYPE html>
<html lang="en-GB">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="ECHO">
  <meta name="theme-color" content="#000000">

  <!-- PWA Manifest & iOS App Icons -->
  <link rel="manifest" href="manifest.webmanifest">
  <link rel="apple-touch-icon" sizes="180x180" href="icons/apple-touch-icon.png">
  <link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
  <link rel="icon" type="image/svg+xml" href="icons/icon.svg">
  <link rel="shortcut icon" href="icons/icon.svg">
"""

# Replace the beginning of app_body (which had redundant <meta charset="UTF-8"> and data-uri icon)
pattern = re.compile(r'<meta charset="UTF-8">.*?<title>', re.DOTALL)
app_body_clean = pattern.sub('<title>', app_body, count=1)

# Add service worker registration before </body>
sw_registration_code = """
  <!-- Offline Service Worker Registration -->
  <script>
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('./sw.js')
          .then(reg => console.log('ECHO PWA: Service Worker registered successfully (scope: ' + reg.scope + ')'))
          .catch(err => console.warn('ECHO PWA: Service Worker registration failed:', err));
      });
    }

    // iOS Standalone Mode Detection
    window.addEventListener('DOMContentLoaded', () => {
      const isStandalone = window.navigator.standalone === true || window.matchMedia('(display-mode: standalone)').matches;
      if (isStandalone) {
        document.body.classList.add('ios-standalone');
        console.log('ECHO running in native standalone mode.');
      }
    });
  </script>
</body>"""

app_body_clean = app_body_clean.replace('</body>', sw_registration_code)

final_index_html = head_prefix + app_body_clean

with open(os.path.join(ECHO_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(final_index_html)
print("[+] Generated clean production index.html")

# Also copy assets into www folder for Capacitor packaging
import shutil
shutil.copyfile(os.path.join(ECHO_DIR, "index.html"), os.path.join(WWW_DIR, "index.html"))
shutil.copyfile(os.path.join(ECHO_DIR, "manifest.webmanifest"), os.path.join(WWW_DIR, "manifest.webmanifest"))
shutil.copyfile(os.path.join(ECHO_DIR, "sw.js"), os.path.join(WWW_DIR, "sw.js"))

www_icons = os.path.join(WWW_DIR, "icons")
os.makedirs(www_icons, exist_ok=True)
for item in os.listdir(ICONS_DIR):
    shutil.copyfile(os.path.join(ICONS_DIR, item), os.path.join(www_icons, item))
print("[+] Mirrored assets to www/ for Capacitor build")
