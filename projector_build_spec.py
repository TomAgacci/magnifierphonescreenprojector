#!/usr/bin/env python3
"""
=============================================================================
  PHONE MIRROR PROJECTOR — COMPLETE BUILD SPECIFICATION GENERATOR
  Phone → Mirror (45°) → Biconvex Lens → Side Wall (landscape image)
  @maxcsmith concept device
=============================================================================
  Run:  python3 projector_build_spec.py
  Output: full builder spec for every iPhone 11 → 16 model
=============================================================================
"""

import math
import datetime

# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM DESIGN CONSTANTS  (change these to redesign the system)
# ─────────────────────────────────────────────────────────────────────────────
TARGET_WALL_W_MM   = 400.0   # Desired projected image width  (mm)
D_LENS_WALL_MM     = 1000.0  # Lens-to-wall distance          (mm)
D_PHONE_MIRROR_MM  = 160.0   # Phone-screen to mirror-centre  (mm)
MIRROR_ANGLE_DEG   = 45.0    # Mirror surface angle, horizontal = 0°
N_GLASS            = 1.52    # BK7 borosilicate refractive index
EDGE_THICK_MM      = 2.0     # Minimum lens edge thickness    (mm)
APERTURE_MARGIN    = 1.25    # Lens aperture = beam_height × this
MOUNT_CLEARANCE_MM = 2.0     # Extra radius added to aperture for mount ring

# ─────────────────────────────────────────────────────────────────────────────
# IPHONE DATABASE
# (name, screen_diagonal_inches, native_ar_wide, native_ar_tall, ppi, year)
# ─────────────────────────────────────────────────────────────────────────────
IPHONES = [
    # ── iPhone 11 family ────────────────────────────────────────────────────
    ("iPhone 11",           6.06, 19.5, 9, 326, 2019),
    ("iPhone 11 Pro",       5.85, 19.5, 9, 458, 2019),
    ("iPhone 11 Pro Max",   6.46, 19.5, 9, 458, 2019),
    # ── iPhone 12 family ────────────────────────────────────────────────────
    ("iPhone 12 mini",      5.42, 19.5, 9, 476, 2020),
    ("iPhone 12",           6.06, 19.5, 9, 460, 2020),
    ("iPhone 12 Pro",       6.06, 19.5, 9, 460, 2020),
    ("iPhone 12 Pro Max",   6.68, 19.5, 9, 458, 2020),
    # ── iPhone 13 family ────────────────────────────────────────────────────
    ("iPhone 13 mini",      5.42, 19.5, 9, 476, 2021),
    ("iPhone 13",           6.06, 19.5, 9, 460, 2021),
    ("iPhone 13 Pro",       6.06, 19.5, 9, 460, 2021),
    ("iPhone 13 Pro Max",   6.68, 19.5, 9, 458, 2021),
    # ── iPhone 14 family ────────────────────────────────────────────────────
    ("iPhone 14",           6.06, 19.5, 9, 460, 2022),
    ("iPhone 14 Plus",      6.68, 19.5, 9, 458, 2022),
    ("iPhone 14 Pro",       6.12, 19.5, 9, 460, 2022),
    ("iPhone 14 Pro Max",   6.69, 19.5, 9, 460, 2022),
    # ── iPhone 15 family ────────────────────────────────────────────────────
    ("iPhone 15",           6.12, 19.5, 9, 460, 2023),
    ("iPhone 15 Plus",      6.69, 19.5, 9, 460, 2023),
    ("iPhone 15 Pro",       6.12, 19.5, 9, 460, 2023),
    ("iPhone 15 Pro Max",   6.69, 19.5, 9, 460, 2023),
    # ── iPhone 16 family ────────────────────────────────────────────────────
    ("iPhone 16",           6.12, 19.5, 9, 460, 2024),
    ("iPhone 16 Plus",      6.69, 19.5, 9, 460, 2024),
    ("iPhone 16 Pro",       6.27, 19.5, 9, 460, 2024),
    ("iPhone 16 Pro Max",   6.90, 19.5, 9, 460, 2024),
]

# ─────────────────────────────────────────────────────────────────────────────
# OPTICAL CALCULATIONS
# ─────────────────────────────────────────────────────────────────────────────
def compute(name, diag_in, ar_w, ar_h, ppi, year):
    diag_mm   = diag_in * 25.4

    # ── Screen geometry (landscape orientation) ──────────────────────────────
    theta     = math.atan2(ar_h, ar_w)           # diagonal angle from horizontal
    W_ls      = diag_mm * math.cos(theta)         # full screen width  (landscape)
    H_ls      = diag_mm * math.sin(theta)         # full screen height (landscape)

    # ── 16:9 video content area (pillarboxed on 19.5:9 screen) ───────────────
    H_169     = H_ls                              # content height = screen height
    W_169     = H_ls * 16.0 / 9.0                # content width
    bar_w     = (W_ls - W_169) / 2.0             # pillarbox bar width each side

    # ── Thin-lens optics ──────────────────────────────────────────────────────
    # Magnification needed to project W_169 → TARGET_WALL_W_MM
    M         = TARGET_WALL_W_MM / W_169
    # Object distance (total folded path from screen to lens)
    d_o       = D_LENS_WALL_MM / M
    # Focal length  1/f = 1/d_o + 1/d_i
    f         = (d_o * D_LENS_WALL_MM) / (d_o + D_LENS_WALL_MM)
    # Verification
    f_check   = 1.0 / (1.0/d_o + 1.0/D_LENS_WALL_MM)

    # ── Wall image dimensions ─────────────────────────────────────────────────
    W_wall    = TARGET_WALL_W_MM
    H_wall    = H_169 * M
    diag_wall_in = math.hypot(W_wall, H_wall) / 25.4

    # ── Mirror-to-lens distance (along folded beam axis) ─────────────────────
    d_mirror_lens = d_o - D_PHONE_MIRROR_MM
    if d_mirror_lens < 10:
        d_mirror_lens = 10.0
        d_o           = D_PHONE_MIRROR_MM + d_mirror_lens
        f             = (d_o * D_LENS_WALL_MM) / (d_o + D_LENS_WALL_MM)

    # ── Beam footprints ───────────────────────────────────────────────────────
    # At mirror: beam is roughly H_169 × W_169 (phone screen content)
    beam_at_mirror_w = W_169
    beam_at_mirror_h = H_169
    # Mirror must intercept this beam at 45° — adds √2 factor to one axis
    mirror_length    = H_169 * math.sqrt(2) * 1.1   # 10% margin, tilted mirror
    mirror_width     = W_169 * 1.1

    # At lens: beam has slightly expanded by diffraction / divergence (approx)
    # For geometric optics, beam at lens ≈ same as at screen (before magnification)
    beam_at_lens_h   = H_169                         # governs aperture
    beam_at_lens_w   = W_169

    # ── Lens physical dimensions (biconvex, equal radii, BK7) ─────────────────
    aperture  = H_169 * APERTURE_MARGIN              # clear aperture
    # Lensmaker's equation for biconvex equal radii:
    # 1/f = (n-1)[1/R - 1/(-R)] = (n-1)(2/R)  →  R = 2(n-1)f
    R         = 2.0 * (N_GLASS - 1.0) * f
    # Sag (sagitta) per surface for given aperture
    h         = aperture / 2.0
    if R > h:
        sag   = R - math.sqrt(R**2 - h**2)
    else:
        sag   = R   # degenerate, shouldn't happen for reasonable designs
    t_centre  = 2.0 * sag + EDGE_THICK_MM           # centre thickness
    od        = aperture + 2.0 * MOUNT_CLEARANCE_MM  # overall diameter with mount ring

    # ── f-number ─────────────────────────────────────────────────────────────
    f_number  = f / aperture

    # ── Housing box (phone + mirror + lens module) ────────────────────────────
    box_depth  = D_PHONE_MIRROR_MM                   # phone to mirror
    box_width  = W_169 * 1.3                         # wider than beam
    box_height = H_169 * 1.3
    tube_len   = d_mirror_lens + t_centre + 20       # mirror→lens + lens + buffer

    return dict(
        name=name, diag_in=diag_in, diag_mm=diag_mm,
        ppi=ppi, year=year, ar_w=ar_w, ar_h=ar_h,
        W_ls=W_ls, H_ls=H_ls,
        W_169=W_169, H_169=H_169, bar_w=bar_w,
        M=M, d_o=d_o, f=f, f_check=f_check,
        W_wall=W_wall, H_wall=H_wall, diag_wall_in=diag_wall_in,
        d_phone_mirror=D_PHONE_MIRROR_MM,
        d_mirror_lens=d_mirror_lens,
        d_lens_wall=D_LENS_WALL_MM,
        total_path=D_PHONE_MIRROR_MM + d_mirror_lens + D_LENS_WALL_MM,
        mirror_length=mirror_length, mirror_width=mirror_width,
        beam_at_mirror_w=beam_at_mirror_w, beam_at_mirror_h=beam_at_mirror_h,
        beam_at_lens_h=beam_at_lens_h, beam_at_lens_w=beam_at_lens_w,
        aperture=aperture, R=R, sag=sag,
        t_centre=t_centre, od=od, f_number=f_number,
        box_depth=box_depth, box_width=box_width,
        box_height=box_height, tube_len=tube_len,
    )

ALL = [compute(*row) for row in IPHONES]

# ─────────────────────────────────────────────────────────────────────────────
# PRINT HELPERS
# ─────────────────────────────────────────────────────────────────────────────
W = 72   # line width

def hr(char='═'): print(char * W)
def hr2(char='─'): print(char * W)
def hdr(text):
    pad = (W - len(text) - 2) // 2
    print('║' + ' ' * pad + text + ' ' * (W - pad - len(text) - 2) + '║')
def row(label, value, unit='', note=''):
    right = f"{value}" + (f" {unit}" if unit else '') + (f"  [{note}]" if note else '')
    dots  = '.' * max(2, W - 4 - len(label) - len(right))
    print(f"  {label}{dots}{right}")
def section(title):
    print()
    print(f"  ┌─ {title} " + '─' * max(2, W - 6 - len(title)) + '┐')
def endsec():
    print(f"  └" + '─' * (W - 3) + '┘')

# ─────────────────────────────────────────────────────────────────────────────
# PER-MODEL FULL BUILD SPEC
# ─────────────────────────────────────────────────────────────────────────────
def print_spec(s):
    hr()
    print(f"  BUILD SPECIFICATION — {s['name'].upper()}")
    print(f"  Generated: {datetime.date.today()}   |   @maxcsmith concept projector")
    hr()

    # ── PHONE SOURCE ─────────────────────────────────────────────────────────
    section("PHONE  (light source)")
    row("Model",          s['name'])
    row("Year",           s['year'])
    row("Screen diagonal",f"{s['diag_in']:.2f}\"",   f"= {s['diag_mm']:.1f} mm")
    row("Native ratio",   f"{s['ar_w']:.1f} : {s['ar_h']:.1f}",  "wide : tall")
    row("PPI",            s['ppi'])
    row("Landscape W",    f"{s['W_ls']:.2f}",   "mm",  "full screen, long side")
    row("Landscape H",    f"{s['H_ls']:.2f}",   "mm",  "full screen, short side")
    row("16:9 content W", f"{s['W_169']:.2f}",  "mm",  "active video area")
    row("16:9 content H", f"{s['H_169']:.2f}",  "mm",  "= landscape H")
    row("Pillarbox bar",  f"{s['bar_w']:.2f}",  "mm",  "each side, black / ignored")
    row("Orientation",    "LANDSCAPE",           "",    "phone rotated 90°, screen up")
    endsec()

    # ── OPTICAL SYSTEM ───────────────────────────────────────────────────────
    section("OPTICAL SYSTEM  (thin-lens model)")
    row("Magnification M",   f"{s['M']:.4f}",   "×",   "image / object")
    row("Object distance d_o",f"{s['d_o']:.2f}","mm",  "phone→lens (folded path)")
    row("Image distance d_i", f"{s['d_lens_wall']:.1f}","mm","lens→wall")
    row("Focal length f",    f"{s['f']:.3f}",   "mm")
    row("Thin-lens verify",
        f"1/d_o + 1/d_i = {1/s['d_o']+1/s['d_lens_wall']:.6f}",
        "",   f"1/f = {1/s['f']:.6f}  ✓" if abs(1/s['d_o']+1/s['d_lens_wall']-1/s['f'])<0.0001 else "MISMATCH")
    endsec()

    # ── COMPONENT PLACEMENTS ─────────────────────────────────────────────────
    section("COMPONENT PLACEMENTS  (all mm, measured along beam path)")
    p0 = 0.0
    p1 = s['d_phone_mirror']
    p2 = p1 + s['d_mirror_lens']
    p3 = p2 + s['d_lens_wall']
    row("[ 0.0 mm ]  Phone screen plane",   "← START / reference zero")
    row(f"[ {p1:.1f} mm ]  Mirror centre",  f"vertical distance above phone")
    row(f"[ {p2:.1f} mm ]  Lens centre",    f"along reflected (horizontal) beam")
    row(f"[ {p3:.1f} mm ]  Wall / screen",  f"= lens + {s['d_lens_wall']:.0f} mm")
    print()
    row("Phone → Mirror",   f"{s['d_phone_mirror']:.1f}", "mm",  "vertical leg")
    row("Mirror → Lens",    f"{s['d_mirror_lens']:.1f}",  "mm",  "horizontal leg")
    row("Lens → Wall",      f"{s['d_lens_wall']:.1f}",    "mm",  "horizontal leg")
    row("Total path length",f"{s['total_path']:.1f}",     "mm",
        f"= {s['total_path']/25.4:.2f}\"")
    endsec()

    # ── MIRROR ───────────────────────────────────────────────────────────────
    section("MIRROR SPECIFICATIONS")
    row("Type",            "Front-surface flat mirror",  "",   "aluminised / silver")
    row("Tilt angle",      f"{MIRROR_ANGLE_DEG:.1f}",  "°",  "from horizontal")
    row("Tilt direction",  "Redirects beam from vertical → horizontal")
    row("Reflective W",    f"{s['mirror_width']:.1f}", "mm",  "covers beam width (+ 10% margin)")
    row("Reflective L",    f"{s['mirror_length']:.1f}","mm",  "tilted dimension (÷ cos45° factor)")
    row("Mirror beam W",   f"{s['beam_at_mirror_w']:.2f}","mm","16:9 content width at mirror")
    row("Mirror beam H",   f"{s['beam_at_mirror_h']:.2f}","mm","16:9 content height at mirror")
    row("Surface quality", "λ/4 flatness or better",   "",   "standard front-surface")
    row("Coating",         "Protected aluminium ≥ 90% R", "", "400–700 nm band")
    row("Mount",           "Kinematic tilt mount",     "",   "±10° adjustment range")
    row("Pivot axis",      "Horizontal, perpendicular to beam plane")
    endsec()

    # ── LENS ─────────────────────────────────────────────────────────────────
    section("LENS SPECIFICATIONS  (order from optical supplier)")
    row("Type",            "Biconvex, plano-convex also acceptable")
    row("Configuration",   "Equal radii  R1 = R2  (symmetric biconvex)")
    row("Clear aperture Ø",f"{s['aperture']:.2f}",    "mm",  "minimum usable area")
    row("Overall diameter",f"{s['od']:.2f}",          "mm",  f"clear + {MOUNT_CLEARANCE_MM:.0f}mm mount ring each side")
    row("Focal length f",  f"{s['f']:.3f}",           "mm",  "EFL — effective focal length")
    row("Radius R1",       f"{s['R']:.3f}",           "mm",  "front surface")
    row("Radius R2",       f"{s['R']:.3f}",           "mm",  "rear surface (same)")
    row("Centre thickness",f"{s['t_centre']:.3f}",    "mm")
    row("Edge thickness",  f"{EDGE_THICK_MM:.1f}",    "mm",  "minimum (at rim)")
    row("Sagitta per face",f"{s['sag']:.3f}",         "mm",  "R - sqrt(R²-(D/2)²)")
    row("f-number  (f/#)", f"f/{s['f_number']:.2f}",  "",    "focal length / aperture")
    row("Glass",           f"BK7 borosilicate",        "",   f"n = {N_GLASS} at 589 nm")
    row("Coating",         "AR coating recommended",   "",   "400–700 nm, both surfaces")
    row("Surface quality", "40-20 scratch-dig or better")
    row("Wavefront error", "λ/4 PV acceptable for this application")
    endsec()

    # ── BEAM FOOTPRINTS ──────────────────────────────────────────────────────
    section("BEAM FOOTPRINTS  (verify clearances)")
    row("At phone screen", f"{s['W_169']:.2f} × {s['H_169']:.2f}", "mm",
        "16:9 source area")
    row("At mirror",       f"{s['beam_at_mirror_w']:.2f} × {s['beam_at_mirror_h']:.2f}", "mm",
        "beam cross-section")
    row("At lens",         f"{s['beam_at_lens_w']:.2f} × {s['beam_at_lens_h']:.2f}", "mm",
        "beam fills lens (geometric approx)")
    row("At wall",         f"{s['W_wall']:.1f} × {s['H_wall']:.1f}", "mm",
        f"= {s['diag_wall_in']:.2f}\" diagonal")
    row("Aspect ratio",    "16 : 9  LANDSCAPE  ✓",    "",   "maintained through system")
    row("Image orientation","LEFT-RIGHT INVERTED",    "",   "mirror reflection flips H")
    endsec()

    # ── HOUSING ──────────────────────────────────────────────────────────────
    section("HOUSING / ENCLOSURE  (suggested dimensions)")
    row("Phone bay opening",
        f"{s['W_169']*1.05:.1f} × {s['H_169']*1.05:.1f}", "mm",
        "slightly larger than screen")
    row("Phone bay depth",  "10–15",   "mm",  "phone rests face-up, screen aimed up")
    row("Mirror chamber",
        f"{s['mirror_width']*1.2:.1f} × {s['mirror_length']*1.2:.1f}", "mm",
        "W × L footprint with clearance")
    row("Mirror chamber H", f"{s['d_phone_mirror']:.1f}", "mm",
        "height from phone bay floor to mirror")
    row("Lens tube length", f"{s['tube_len']:.1f}",  "mm",
        "mirror centre to lens rear face")
    row("Lens tube bore",   f"{s['od']+2:.1f}",      "mm",  "lens OD + 2mm wall clearance")
    row("Projection tube",  "Open or baffled",        "",   f"{s['d_lens_wall']:.0f}mm to wall")
    row("Total unit depth", f"{s['d_phone_mirror']+s['mirror_width']*0.6:.1f}", "mm",
        "approx phone bay + mirror housing")
    endsec()

    # ── ASSEMBLY SEQUENCE ────────────────────────────────────────────────────
    section("ASSEMBLY SEQUENCE")
    steps = [
        ("1", "Phone bay",    f"Place phone face-up in bay. Screen aims vertically upward. "
                              f"Centre of screen at x=0, y=0 reference."),
        ("2", "Mirror mount", f"Position mirror centre at {s['d_phone_mirror']:.0f}mm above phone screen "
                              f"plane. Tilt {MIRROR_ANGLE_DEG:.0f}° from horizontal. "
                              f"Reflecting face aims downward toward phone."),
        ("3", "Beam path",    f"Reflected beam travels horizontally. "
                              f"Align lens tube axis with reflected beam."),
        ("4", "Lens mount",   f"Mount lens at {s['d_mirror_lens']:.1f}mm from mirror centre "
                              f"along the horizontal beam axis. "
                              f"Lens clear aperture Ø{s['aperture']:.1f}mm must be centred on beam."),
        ("5", "Focus check",  f"Place wall or screen at {s['d_lens_wall']:.0f}mm from lens. "
                              f"Expected image: {s['W_wall']:.0f}×{s['H_wall']:.0f}mm ({s['diag_wall_in']:.1f}\" diag)."),
        ("6", "Mirror trim",  f"Adjust mirror tilt (kinematic mount) to centre image on wall. "
                              f"Fine tilt of ±2° shifts image ±{2*s['d_lens_wall']*math.tan(math.radians(2)):.0f}mm vertically."),
        ("7", "Focus trim",   f"Slide lens ±10mm along tube to sharpen focus. "
                              f"Moving lens 10mm toward wall shifts focus ~{10*s['M']**2:.0f}mm."),
        ("8", "Inversion",    "Image will be left-right mirrored. Add a second flat mirror "
                              "in the beam path to correct, or mirror the phone display in settings."),
    ]
    for num, label, desc in steps:
        prefix = f"  │ {num}. {label}: "
        wrap   = W - len(prefix) - 2
        words  = desc.split()
        line   = ''
        first  = True
        for w in words:
            if len(line) + len(w) + 1 > wrap:
                print(prefix + line if first else ' ' * len(prefix) + line)
                first = False
                line  = w
            else:
                line  = (line + ' ' + w).strip()
        if line:
            print(prefix + line if first else ' ' * len(prefix) + line)
    endsec()

    # ── PARTS LIST ───────────────────────────────────────────────────────────
    section("PARTS LIST  (order references)")
    parts = [
        ("Front-surface mirror",
         f"≥{s['mirror_width']:.0f}×{s['mirror_length']:.0f}mm, "
         f"aluminised, protected, λ/4 flat"),
        ("Biconvex lens",
         f"EFL={s['f']:.0f}mm, Ø={s['od']:.0f}mm OD, BK7, AR coated, "
         f"R1=R2={s['R']:.0f}mm"),
        ("Kinematic mirror mount",
         f"±10° tilt range, fits {s['mirror_width']:.0f}mm mirror"),
        ("Lens tube",
         f"Bore Ø{s['od']+2:.0f}mm, length {s['tube_len']:.0f}mm, "
         f"aluminium or PLA"),
        ("Phone holder / bay",
         f"{s['W_169']*1.05:.0f}×{s['H_169']*1.05:.0f}mm opening, "
         f"with USB passthrough for charging"),
        ("Housing body",
         f"L-shaped, vertical + horizontal arms, "
         f"black-painted interior (suppress stray light)"),
        ("Wall / screen",
         f"Matte white surface at {s['d_lens_wall']:.0f}mm from lens"),
    ]
    for part, spec in parts:
        print(f"  │  • {part}")
        print(f"  │      {spec}")
    endsec()
    print()

# ─────────────────────────────────────────────────────────────────────────────
# QUICK-REFERENCE SUMMARY TABLE
# ─────────────────────────────────────────────────────────────────────────────
def print_summary_table():
    hr('═')
    print("  QUICK REFERENCE — ALL MODELS")
    print(f"  Target wall: {TARGET_WALL_W_MM:.0f}mm wide × {TARGET_WALL_W_MM*9/16:.0f}mm tall  "
          f"| Lens→wall: {D_LENS_WALL_MM:.0f}mm "
          f"| Phone→mirror: {D_PHONE_MIRROR_MM:.0f}mm "
          f"| Mirror: {MIRROR_ANGLE_DEG:.0f}°")
    hr('═')

    # header
    cols = [
        ("Model",            18, '<'),
        ("Yr",                4, '>'),
        ("Scr\"",             5, '>'),
        ("16:9 W×H (mm)",    17, '^'),
        ("M×",                5, '>'),
        ("f (mm)",            7, '>'),
        ("LensØ(mm)",         9, '>'),
        ("R (mm)",            7, '>'),
        ("t_c(mm)",           7, '>'),
        ("Mir L (mm)",       10, '>'),
        ("mir→len(mm)",      11, '>'),
        ("Wall\"",            6, '>'),
    ]

    def fmt_row(vals):
        out = ''
        for (_, w, align), v in zip(cols, vals):
            if align == '<': out += f"{str(v):<{w}} "
            elif align == '>': out += f"{str(v):>{w}} "
            else: out += f"{str(v):^{w}} "
        print(out)

    fmt_row([c[0] for c in cols])
    hr2()
    prev_year = None
    for s in ALL:
        if s['year'] != prev_year:
            if prev_year is not None:
                hr2('·')
            prev_year = s['year']
        fmt_row([
            s['name'],
            s['year'],
            f"{s['diag_in']:.2f}",
            f"{s['W_169']:.1f} × {s['H_169']:.1f}",
            f"{s['M']:.3f}",
            f"{s['f']:.1f}",
            f"{s['aperture']:.1f}",
            f"{s['R']:.1f}",
            f"{s['t_centre']:.1f}",
            f"{s['mirror_length']:.1f}",
            f"{s['d_mirror_lens']:.1f}",
            f"{s['diag_wall_in']:.2f}",
        ])
    hr('═')
    print()
    print("  COLUMN GUIDE:")
    print("  M×          = magnification (wall size / phone content size)")
    print("  f           = lens focal length  [mm]")
    print("  LensØ       = lens clear aperture diameter  [mm]")
    print("  R           = lens radius of curvature, both surfaces equal  [mm]")
    print("  t_c         = lens centre thickness  [mm]")
    print("  Mir L       = mirror reflective length (tilted, at 45°)  [mm]")
    print("  mir→len     = mirror-centre to lens-centre distance  [mm]")
    print("  Wall\"       = diagonal of projected image on wall  [inches]")
    hr('═')

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print()
    hr('█')
    print("  PHONE MIRROR PROJECTOR — COMPLETE BUILD SPECIFICATION")
    print("  Phone (landscape) → Mirror (45°) → Biconvex Lens → Side Wall")
    print(f"  System constants:  wall_target={TARGET_WALL_W_MM:.0f}mm wide  "
          f"| lens-wall={D_LENS_WALL_MM:.0f}mm  "
          f"| phone-mirror={D_PHONE_MIRROR_MM:.0f}mm")
    print(f"  Optics:  BK7 glass n={N_GLASS}  "
          f"| mirror θ={MIRROR_ANGLE_DEG}°  "
          f"| aperture margin={APERTURE_MARGIN}×  "
          f"| generated {datetime.date.today()}")
    hr('█')
    print()

    # Print full spec for every phone
    for s in ALL:
        print_spec(s)

    # Print summary table
    print_summary_table()

    print()
    print("  NOTE ON IMAGE INVERSION:")
    print("  A single flat mirror reverses left-right (horizontal flip).")
    print("  To correct: (a) enable display mirroring in iOS Accessibility settings,")
    print("  OR (b) add a second flat mirror before the lens to re-flip the image.")
    print("  Vertical (top-bottom) is NOT flipped by the mirror at 45°.")
    print()
    print("  NOTE ON FOCUS:")
    print("  The thin-lens formula assumes phone screen is the object plane.")
    print("  Real focus position: slide lens ±15mm along tube for fine trim.")
    print("  Moving lens TOWARD wall → image moves away from wall (larger, softer).")
    print("  Moving lens AWAY from wall → image moves toward wall (smaller, sharper).")
    print()
    print("  NOTE ON BRIGHTNESS:")
    print("  Phone brightness directly governs image brightness.")
    print("  Set phone to max brightness. Use in a darkened room.")
    print("  Larger aperture lens collects more light → brighter image.")
    print()
    hr('█')
    print("  END OF BUILD SPECIFICATION  |  @maxcsmith concept projector")
    hr('█')
