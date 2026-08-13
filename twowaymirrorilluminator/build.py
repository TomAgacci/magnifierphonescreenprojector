# ============================================
# build.py — Two‑Way Mirror Illuminator Builder
# ============================================
#
# This script generates:
#   - wiring_layout.txt
#   - parts_list.txt
#   - brightness_model.json
#   - enclosure_dimensions.txt
#
# It acts as a reproducible "build generator" for the LED + two‑way mirror box.
#
# Run:
#     python build.py
#
# ============================================

import json
import math

# -----------------------------
# CONFIGURATION PARAMETERS
# -----------------------------
LED_LUMENS = 1000                 # total luminous flux of LED panel/strips
AREA_M2 = 0.25                    # illuminated area behind mirror (m^2)
MIRROR_TRANSMISSION = 0.15        # 15% transmission typical for two‑way mirror
DIM_LEVELS = {
    "mirror_mode": 0.0,
    "hybrid_mode": 0.35,
    "display_mode": 1.0
}

# -----------------------------
# BRIGHTNESS MODEL
# -----------------------------
def compute_brightness():
    """Compute illuminance inside box and transmitted through mirror."""
    inside_lux = LED_LUMENS / AREA_M2
    transmitted_lux = inside_lux * MIRROR_TRANSMISSION
    return inside_lux, transmitted_lux

def compute_dimmed_levels():
    """Compute brightness at each dimmer preset."""
    inside, transmitted = compute_brightness()
    levels = {}
    for mode, pct in DIM_LEVELS.items():
        levels[mode] = {
            "inside_lux": inside * pct,
            "transmitted_lux": transmitted * pct
        }
    return levels

# -----------------------------
# FILE GENERATION
# -----------------------------
def write_wiring_layout():
    text = """
TWO‑WAY MIRROR ILLUMINATOR — WIRING LAYOUT
=========================================

Power Input:
    - 12 V DC barrel jack → inline PWM dimmer → LED panel/strips

Connections:
    +12V → DIMMER(+) → LED(+)
    GND → DIMMER(-) → LED(-)

Optional:
    - USB 5 V line routed to phone cradle for charging
    - Toggle switch for preset modes (mirror / hybrid / display)

Phone / Image Source:
    - Phone sits in cradle facing mirror
    - LCD or transparency can be substituted
"""
    with open("wiring_layout.txt", "w") as f:
        f.write(text.strip())

def write_parts_list():
    text = """
PARTS LIST
==========

Optics:
    - Two‑way mirror (30–50% reflectivity, 10–20% transmission)
    - Diffuser sheet (opal acrylic)

Electronics:
    - 12 V LED strip or panel (800–1500 lm)
    - Inline PWM dimmer
    - 12 V 2–3 A power supply
    - DC barrel jack
    - Optional USB 5 V module

Mechanical:
    - Shallow enclosure box (wood, acrylic, or aluminum)
    - Phone cradle or LCD mount
    - Mounting frame for mirror
"""
    with open("parts_list.txt", "w") as f:
        f.write(text.strip())

def write_brightness_model():
    levels = compute_dimmed_levels()
    with open("brightness_model.json", "w") as f:
        json.dump(levels, f, indent=4)

def write_enclosure_dimensions():
    text = """
ENCLOSURE DIMENSIONS (REFERENCE)
================================

Front opening:
    - Same size as two‑way mirror (e.g., 300 mm × 300 mm)

Depth:
    - 60–90 mm total
        - 10 mm mirror mount
        - 20–30 mm image plane / phone cradle
        - 20–40 mm LED + diffuser spacing

LED spacing:
    - Uniform grid or edge‑lit panel
"""
    with open("enclosure_dimensions.txt", "w") as f:
        f.write(text.strip())

# -----------------------------
# MAIN
# -----------------------------
def main():
    write_wiring_layout()
    write_parts_list()
    write_brightness_model()
    write_enclosure_dimensions()
    print("Build files generated successfully.")

if __name__ == "__main__":
    main()
