"""Top-down robot diagrams (wheels, direction arrows, labels) as inline SVG.

Driven by a small YAML block in the sheet, e.g.

    ```robot
    left: [up, down]        # arrows beside the left wheel: up / down / [up, down]
    right: up
    arrow: forward          # big arrow: forward forward-short backward spin curve-left (omit for none)
    stripes: true           # white speed stripes across the big arrow
    front: true             # 'Robot front' label
    pins: {left-up: Pin 11, left-down: Pin 10, right-up: Pin 8, right-down: Pin 9}
    wheel-names: true       # 'Left Wheel' / 'Right Wheel' boxes
    caption: Motor control pins
    ```
"""
import html
import math

import yaml

# One scale for every diagram, so the robot is the same size wherever it appears.
MM_PER_UNIT = 0.207

BLUE, YELLOW, ORANGE = "#cfe2f3", "#ffff00", "#ff9900"
OUTLINE = 'stroke="#000" stroke-width="1.3" stroke-linejoin="round"'

BODY = (f'<path d="M70,70 L150,42 L230,70 L230,195 C230,240 70,240 70,195 Z" '
        f'fill="{BLUE}" {OUTLINE}/>')


def _wheels():
    parts = []
    for strip, axle, motor in ((40, 60, 82), (240, 218, 180)):
        parts.append(f'<rect x="{motor}" y="95" width="38" height="108" fill="{YELLOW}" {OUTLINE}/>')
        parts.append(f'<rect x="{axle}" y="122" width="22" height="10" fill="#000"/>')
        parts.append(f'<rect x="{strip}" y="80" width="20" height="100" fill="{BLUE}" {OUTLINE}/>')
    return "".join(parts)


def _small_arrow(cx, direction, y0, y1):
    """Outlined block arrow between y0 and y1; the tip is at y0 for 'up', y1 for 'down'."""
    head = 16
    tip, base = (y0, y1) if direction == "up" else (y1, y0)
    sign = 1 if direction == "up" else -1
    neck = tip + sign * 16
    pts = [(cx, tip), (cx + head / 2, neck), (cx + 3, neck), (cx + 3, base),
           (cx - 3, base), (cx - 3, neck), (cx - head / 2, neck)]
    return f'<polygon points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="{BLUE}" {OUTLINE}/>'


def _wheel_arrows(side, spec):
    dirs = [spec] if isinstance(spec, str) else list(spec)
    cx = 22 if side == "left" else 278
    if len(dirs) == 2:  # pin diagram: one short arrow each way
        return (_small_arrow(cx, "up", 82, 125) + _small_arrow(cx, "down", 135, 178))
    return _small_arrow(cx, dirs[0], 80, 180)


def _block_arrow(pts):
    return (f'<polygon points="{" ".join(f"{x},{y}" for x, y in pts)}" '
            f'fill="{ORANGE}" {OUTLINE}/>')


# Curved arrows are drawn at full size, then fitted between the motors (x 120..180, y 95..203).
GAP_CX, GAP_CY, GAP_W = 150, 149, 50
PATH_SHAFT = 13


def _fitted(cmds, head):
    """cmds: ('M'|'L', x, y) / ('A', r, x, y) / ('Q', cx, cy, x, y) in full-size coords; head: triangle.
    -> (scaled path d, scaled head points), centred in the gap and `GAP_W` wide."""
    path_xs = [x for c in cmds for x in c[1::2] if c[0] != "A"]
    ys = [y for c in cmds for y in c[2::2] if c[0] != "A"] + [y for _, y in head]
    head_xs = [x for x, _ in head]
    # the shaft's own half-thickness sticks out beyond its centre line, by a fixed size not a scaled one,
    # so solve for the scale iteratively
    k, pad = 1.0, PATH_SHAFT / 2 + 1.3
    for _ in range(8):
        lo = min(min(path_xs) - pad / k, min(head_xs))
        hi = max(max(path_xs) + pad / k, max(head_xs))
        k = GAP_W / (hi - lo)
    cx, cy = (hi + lo) / 2, (max(ys) + min(ys)) / 2

    def pt(x, y):
        return GAP_CX + (x - cx) * k, GAP_CY + (y - cy) * k

    parts = []
    for c in cmds:
        if c[0] == "A":
            x, y = pt(*c[2:])
            parts.append(f"A{c[1] * k:.2f},{c[1] * k:.2f} 0 0 1 {x:.2f},{y:.2f}")
        else:
            coords = [pt(*c[i:i + 2]) for i in range(1, len(c), 2)]
            parts.append(c[0] + " ".join(f"{x:.2f},{y:.2f}" for x, y in coords))
    return " ".join(parts), [pt(x, y) for x, y in head]


def _path_arrow(cmds, head):
    """Thick curved arrow: black underlay, orange on top, triangular head.

    The underlay starts one outline-width before the orange so the shaft base is outlined too."""
    d, head = _fitted(cmds, head)
    first = d.split(" ", 1)
    x, y = (float(v) for v in first[0][1:].split(","))
    under = f"M{x:.2f},{y + 1.3:.2f} {first[1]}"
    return (f'<path d="{under}" fill="none" stroke="#000" stroke-width="{PATH_SHAFT + 2.6}" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{ORANGE}" stroke-width="{PATH_SHAFT}"/>'
            f'<polygon points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in head)}" fill="{ORANGE}" {OUTLINE}/>')


SPIN_R, SPIN_SHAFT, SPIN_HEAD_W, SPIN_HEAD_LEN = 17, 9, 10.5, 13
SPIN_START, SPIN_SWEEP = 230, 280  # degrees clockwise from 12 o'clock; the gap left is where the head points


def _spin_arrow():
    """Nearly-full clockwise circle in the gap between the motors, with a tangent head at the end."""
    def at(deg, r=SPIN_R):
        a = math.radians(deg)
        return GAP_CX + r * math.sin(a), GAP_CY - r * math.cos(a)

    end = SPIN_START + SPIN_SWEEP
    a = math.radians(end)
    tangent, outward = (math.cos(a), math.sin(a)), (math.sin(a), -math.cos(a))
    bx, by = at(end)
    head = [(bx + outward[0] * SPIN_HEAD_W, by + outward[1] * SPIN_HEAD_W),
            (bx + tangent[0] * SPIN_HEAD_LEN, by + tangent[1] * SPIN_HEAD_LEN),
            (bx - outward[0] * SPIN_HEAD_W, by - outward[1] * SPIN_HEAD_W)]

    def arc(start_deg):
        x0, y0 = at(start_deg)
        x1, y1 = bx, by
        return f"M{x0:.2f},{y0:.2f} A{SPIN_R},{SPIN_R} 0 1 1 {x1:.2f},{y1:.2f}"

    # underlay starts one outline-width earlier so the shaft base is outlined
    under = arc(SPIN_START - math.degrees(1.3 / SPIN_R))
    return (f'<path d="{under}" fill="none" stroke="#000" stroke-width="{SPIN_SHAFT + 2.6}"/>'
            f'<path d="{arc(SPIN_START)}" fill="none" stroke="{ORANGE}" stroke-width="{SPIN_SHAFT}"/>'
            f'<polygon points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in head)}" fill="{ORANGE}" {OUTLINE}/>')


BIG_ARROWS = {
    "forward": lambda: _block_arrow(
        [(127, 124), (127, 19), (105, 19), (150, -31), (195, 19), (173, 19), (173, 124)]),
    # same arrow, shorter: tip just clears the nose (y=42), for tight layouts
    "forward-short": lambda: _block_arrow(
        [(127, 124), (127, 56), (105, 56), (150, 6), (195, 56), (173, 56), (173, 124)]),
    "backward": lambda: _block_arrow(
        [(128, 96), (128, 190), (104, 190), (150, 245), (196, 190), (172, 190), (172, 96)]),
    "spin": lambda: _spin_arrow(),
    "curve-left": lambda: _path_arrow(
        [("M", 205, 190), ("L", 205, 130), ("Q", 205, 72, 150, 72)],
        [(150, 42), (150, 102), (100, 72)]),
}


# (y, height): thinner and closer together towards the tail, to suggest the speed building up
# arrows that point past the robot's nose need room above it: viewBox top for each
ARROW_TOP = {"forward": -40, "forward-short": -8}

SPEED_BARS = [(24, 10), (59, 10), (88, 5), (110, 5)]


# the forward arrow's shaft is x 127..173; stripes span its outer outline edges so they cut it cleanly
STRIPE_X, STRIPE_W = 126.35, 47.3


def _stripes():
    return "".join(f'<rect x="{STRIPE_X}" y="{y}" width="{STRIPE_W}" height="{h}" fill="#fff"/>'
                   for y, h in SPEED_BARS)


def _text(x, y, s, anchor="middle", size=17):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Arimo" '
            f'font-size="{size}" fill="#000">{html.escape(s)}</text>')


def _wheel_name(x, name):
    return (f'<rect x="{x}" y="105" width="66" height="50" rx="8" fill="#f3f3f3"/>'
            + _text(x + 33, 126, name) + _text(x + 33, 146, "Wheel"))


def _labels(spec):
    parts = []
    pins = spec.get("pins", {})
    for key, (x, y, anchor) in {"left-up": (8, 100, "end"), "left-down": (8, 168, "end"),
                                "right-up": (292, 100, "start"),
                                "right-down": (292, 168, "start")}.items():
        if key in pins:
            parts.append(_text(x, y, str(pins[key]), anchor))
    if spec.get("wheel-names"):
        parts.append(_wheel_name(-108, "Left"))
        parts.append(_wheel_name(346, "Right"))
    if spec.get("front"):
        # below the sloped nose lines, above the motors
        parts.append(_text(150, 89, "Robot front"))
    if spec.get("caption"):
        parts.append(_text(150, 268, spec["caption"]))
    return "".join(parts)


def render_robot(block):
    """YAML block -> <figure> containing the SVG."""
    spec = yaml.safe_load(block) or {}
    labelled = bool(spec.get("pins") or spec.get("wheel-names") or spec.get("caption"))
    x0, w = (-112, 530) if labelled else (0, 300)
    h = 285 if spec.get("caption") else 255
    y0 = ARROW_TOP.get(spec.get("arrow"), 0)
    h -= y0
    inner = BODY + _wheels()
    for side in ("left", "right"):
        if side in spec:
            inner += _wheel_arrows(side, spec[side])
    if spec.get("arrow"):
        inner += BIG_ARROWS[spec["arrow"]]()
        if spec.get("stripes"):
            inner += _stripes()
    inner += _labels(spec)
    return (f'<figure class="diagram" style="width:{w * MM_PER_UNIT:.1f}mm"><svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="{x0} {y0} {w} {h}" width="100%">{inner}</svg></figure>\n')
