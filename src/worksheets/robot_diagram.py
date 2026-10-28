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


# Curved arrows are anchored on the middle of the robot: halfway between the wheel axles (y 127).
MID_X, MID_Y = 150, 127


def _arc_arrow(d, d_under, head, shaft):
    """Curved arrow: black underlay, orange shaft on top, triangular head.

    `d_under` starts one outline-width before `d` so the shaft base is outlined too."""
    return (f'<path d="{d_under}" fill="none" stroke="#000" stroke-width="{shaft + 2.6}"/>'
            f'<path d="{d}" fill="none" stroke="{ORANGE}" stroke-width="{shaft}"/>'
            f'<polygon points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in head)}" fill="{ORANGE}" {OUTLINE}/>')


def _head(base, tangent, half_width, length):
    """Triangle whose base is centred on `base` and whose tip lies along unit `tangent`."""
    nx, ny = -tangent[1], tangent[0]
    bx, by = base
    return [(bx + nx * half_width, by + ny * half_width),
            (bx + tangent[0] * length, by + tangent[1] * length),
            (bx - nx * half_width, by - ny * half_width)]


SPIN_R, SPIN_SHAFT, SPIN_HEAD_W, SPIN_HEAD_LEN = 17, 9, 10.5, 13
SPIN_START, SPIN_SWEEP = 230, 280  # degrees clockwise from 12 o'clock; the gap left is where the head points


def _spin_arrow():
    """Nearly-full clockwise circle in the gap between the motors, with a tangent head at the end."""
    def at(deg, r=SPIN_R):
        a = math.radians(deg)
        return MID_X + r * math.sin(a), MID_Y - r * math.cos(a)

    end = SPIN_START + SPIN_SWEEP
    a = math.radians(end)
    bx, by = at(end)
    head = _head((bx, by), (math.cos(a), math.sin(a)), SPIN_HEAD_W, SPIN_HEAD_LEN)

    def arc(start_deg):
        x0, y0 = at(start_deg)
        return f"M{x0:.2f},{y0:.2f} A{SPIN_R},{SPIN_R} 0 1 1 {bx:.2f},{by:.2f}"

    return _arc_arrow(arc(SPIN_START), arc(SPIN_START - math.degrees(1.3 / SPIN_R)), head, SPIN_SHAFT)


# Gentle left curve: an arc of a vertical ellipse (taller than wide) that starts at the robot's middle
# heading straight up and turns CURVE_TURN degrees on its way out of the front, so there is no straight
# run in the shaft.
CURVE_RX, CURVE_RY, CURVE_TURN, CURVE_SHAFT = 90, 130, 30, 15
CURVE_HEAD_W, CURVE_HEAD_LEN = 14, 24


def _curve_left_arrow():
    # heading from vertical at parameter t is atan((rx sin t) / (ry cos t))
    t = math.atan(math.tan(math.radians(CURVE_TURN)) * CURVE_RY / CURVE_RX)

    def at(u):
        return MID_X - CURVE_RX + CURVE_RX * math.cos(u), MID_Y - CURVE_RY * math.sin(u)

    end = at(t)
    tangent = (-CURVE_RX * math.sin(t), -CURVE_RY * math.cos(t))
    norm = math.hypot(*tangent)
    head = _head(end, (tangent[0] / norm, tangent[1] / norm), CURVE_HEAD_W, CURVE_HEAD_LEN)

    def arc(u0):
        x0, y0 = at(u0)
        return f"M{x0:.2f},{y0:.2f} A{CURVE_RX},{CURVE_RY} 0 0 0 {end[0]:.2f},{end[1]:.2f}"

    # the underlay starts one outline-width earlier so the shaft base is outlined
    return _arc_arrow(arc(0), arc(-1.3 / CURVE_RY), head, CURVE_SHAFT)


BIG_ARROWS = {
    "forward": lambda: _block_arrow(
        [(127, 124), (127, 19), (105, 19), (150, -31), (195, 19), (173, 19), (173, 124)]),
    # same arrow, shorter: tip just clears the nose (y=42), for tight layouts
    "forward-short": lambda: _block_arrow(
        [(127, 124), (127, 56), (105, 56), (150, 6), (195, 56), (173, 56), (173, 124)]),
    "backward": lambda: _block_arrow(
        [(128, 96), (128, 190), (104, 190), (150, 245), (196, 190), (172, 190), (172, 96)]),
    "spin": lambda: _spin_arrow(),
    "curve-left": lambda: _curve_left_arrow(),
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
