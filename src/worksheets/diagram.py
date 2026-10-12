"""Top-down robot diagrams (wheels, direction arrows, labels) as inline SVG.

Driven by a small YAML block in the sheet, e.g.

    ```robot
    left: [up, down]        # arrows beside the left wheel: up / down / [up, down]
    right: up
    arrow: forward          # big arrow: forward backward spin curve-left (omit for none)
    stripes: true           # white speed stripes across the big arrow
    front: true             # 'Robot front' label
    pins: {left-up: Pin 11, left-down: Pin 10, right-up: Pin 8, right-down: Pin 9}
    wheel-names: true       # 'Left Wheel' / 'Right Wheel' boxes
    caption: Motor control pins
    width: 70mm
    ```
"""
import html

import yaml

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


def _path_arrow(d, head):
    """Thick curved arrow: black underlay, orange on top, triangular head."""
    return (f'<path d="{d}" fill="none" stroke="#000" stroke-width="29" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{ORANGE}" stroke-width="25"/>'
            f'<polygon points="{" ".join(f"{x},{y}" for x, y in head)}" fill="{ORANGE}" {OUTLINE}/>')


BIG_ARROWS = {
    "forward": lambda: _block_arrow(
        [(127, 124), (127, 19), (105, 19), (150, -31), (195, 19), (173, 19), (173, 124)]),
    "backward": lambda: _block_arrow(
        [(128, 96), (128, 190), (104, 190), (150, 245), (196, 190), (172, 190), (172, 96)]),
    "spin": lambda: _path_arrow("M118,200 L118,125 A37,37 0 0 1 192,125 L192,165",
                                [(168, 165), (216, 165), (192, 205)]),
    "curve-left": lambda: _path_arrow("M205,190 L205,130 Q205,72 150,72",
                                      [(150, 42), (150, 102), (100, 72)]),
}


# (y, height): thinner and closer together towards the tail, to suggest the speed building up
SPEED_BARS = [(24, 10), (59, 10), (88, 5), (110, 5)]


def _stripes():
    return "".join(f'<rect x="110" y="{y}" width="80" height="{h}" fill="#fff"/>'
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
        parts.append(_text(150, 62, "Robot front"))
    if spec.get("caption"):
        parts.append(_text(150, 268, spec["caption"]))
    return "".join(parts)


def render_robot(block):
    """YAML block -> <figure> containing the SVG."""
    spec = yaml.safe_load(block) or {}
    labelled = bool(spec.get("pins") or spec.get("wheel-names") or spec.get("caption"))
    x0, w = (-112, 530) if labelled else (0, 300)
    h = 285 if labelled else 255
    # the forward arrow points past the robot's nose, so make room above it
    y0 = -40 if spec.get("arrow") == "forward" else 0
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
    width = spec.get("width", "70mm")
    return (f'<figure class="diagram" style="width:{width}"><svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="{x0} {y0} {w} {h}" width="100%">{inner}</svg></figure>\n')
