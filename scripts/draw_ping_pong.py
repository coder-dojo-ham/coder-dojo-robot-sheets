"""Draw the ultrasonic ping/pong diagram (Obstacle avoiding, Step 1) as SVG.

The Google Docs drawing uses arc and can shapes that scripts/gdocs/odt_drawings.py does not convert, so this
redraws it by hand from the original's proportions. Idempotent: re-running rewrites the same file.

usage: uv run python scripts/draw_ping_pong.py <out.svg>
"""
import math
import sys

BLUE = "#cfe2f3"
BLUE_LIGHT = "#e3eef9"
INK = "#000000"
FONT = "Arimo, Liberation Sans, Arial, sans-serif"


def can(left, top_y, width=182, height=140):
    """A sensor: cylinder body with a lighter top ellipse."""
    rx, ry, right, bottom = width / 2, 22, left + width, top_y + height
    return (
        f'<path d="M{left} {top_y} V{bottom} A{rx} {ry} 0 0 0 {right} {bottom} V{top_y}" '
        f'fill="{BLUE}" stroke="{INK}" stroke-width="3"/>'
        f'<ellipse cx="{left + rx}" cy="{top_y}" rx="{rx}" ry="{ry}" fill="{BLUE_LIGHT}" stroke="{INK}" stroke-width="3"/>'
    )


WAVE_SCALE = 0.8  # sound waves are drawn at this fraction of their original size


WAVE_FIRST = 62  # radius of the innermost wavefront; ping and pong share it so the waves match
PONG_WAVE_DISTANCE = 125  # how far down the pong arrow its waves sit, from the reflection point


def wave_radii(first, count=4, step=25):
    """Radii of `count` wavefronts, the first at `first` from the source, spacing scaled by WAVE_SCALE."""
    return tuple(round(first + i * step * WAVE_SCALE) for i in range(count))


def wavefronts(cx, cy, heading_deg, radii, half_span_deg=42):
    """Concentric arcs around (cx, cy), centred on a heading measured clockwise from straight up."""
    paths = []
    for r in radii:
        points = []
        for a in (heading_deg - half_span_deg, heading_deg + half_span_deg):
            rad = math.radians(a)
            points.append((cx + r * math.sin(rad), cy - r * math.cos(rad)))
        (x1, y1), (x2, y2) = points
        paths.append(f'<path d="M{x1:.1f} {y1:.1f} A{r} {r} 0 0 1 {x2:.1f} {y2:.1f}" fill="none" stroke="{INK}" stroke-width="5"/>')
    return "".join(paths)


def diagram():
    ping_heading = math.degrees(math.atan2(152, 400))
    pong_heading = 180 - math.degrees(math.atan2(116, 400))
    # same arcs as ping, centred further down the pong arrow so they sit where they should
    d = PONG_WAVE_DISTANCE - WAVE_FIRST
    pong_wave_centre = (352 + d * math.sin(math.radians(pong_heading)), 52 - d * math.cos(math.radians(pong_heading)))
    parts = [
        f'<rect x="15" y="-5" width="675" height="52" fill="{BLUE}" stroke="{INK}" stroke-width="3"/>',
        f'<rect x="65" y="615" width="515" height="70" fill="{BLUE}" stroke="{INK}" stroke-width="3"/>',
        can(108, 470),
        can(378, 475),
        # arrows first so the wavefronts and labels sit on top
        f'<line x1="200" y1="450" x2="352" y2="52" stroke="{INK}" stroke-width="3" marker-end="url(#head)"/>',
        f'<line x1="352" y1="52" x2="468" y2="450" stroke="{INK}" stroke-width="3" marker-end="url(#head)"/>',
        wavefronts(200, 450, ping_heading, wave_radii(WAVE_FIRST), 38),
        wavefronts(*pong_wave_centre, pong_heading, wave_radii(WAVE_FIRST), 38),
        f'<text x="135" y="262" font-size="44" font-family="{FONT}">Ping!</text>',
        f'<text x="435" y="318" font-size="44" font-family="{FONT}">Pong!</text>',
    ]
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 700" width="7in" height="7in">'
        '<defs><marker id="head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto">'
        '<path d="M0 0L10 5L0 10z"/></marker></defs>' + "".join(parts) + "</svg>"
    )


def main(out):
    with open(out, "w") as f:
        f.write(diagram())


if __name__ == "__main__":
    main(sys.argv[1])
