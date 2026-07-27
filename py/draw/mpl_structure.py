"""matplotlib structure diagram generator."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO


def draw_sm_diagram(L: float, P: float, mode: str = "sm") -> BytesIO:
    """Draw Shear (S) and Moment (M) diagrams for a simple beam with center point load.

    Args:
        L: span length (mm)
        P: point load (N)
        mode: 's' for shear only, 'm' for moment only, 'sm' for both

    Returns:
        BytesIO PNG buffer.
    """
    fig, axes = plt.subplots(1, 2 if mode == "sm" else 1, figsize=(8, 4))
    if mode == "sm":
        ax_s, ax_m = axes
    elif mode == "s":
        ax_s = axes
        ax_m = None
    else:
        ax_m = axes
        ax_s = None

    # Shear diagram
    if ax_s is not None:
        x = [0, L / 2, L / 2, L]
        s = [P / 2, P / 2, -P / 2, -P / 2]
        ax_s.plot(x, s, drawstyle="steps-post", color="steelblue", linewidth=2)
        ax_s.fill_between(x, s, step="post", alpha=0.2, color="steelblue")
        ax_s.axhline(0, color="black", linewidth=0.5)
        ax_s.set_title("Shear Force Diagram")
        ax_s.set_xlabel("Length (mm)")
        ax_s.set_ylabel("Shear (N)")

    # Moment diagram
    if ax_m is not None:
        x = [0, L / 2, L]
        m = [0, P * L / 4, 0]
        ax_m.plot(x, m, color="crimson", linewidth=2)
        ax_m.fill_between(x, m, alpha=0.2, color="crimson")
        ax_m.axhline(0, color="black", linewidth=0.5)
        ax_m.set_title("Bending Moment Diagram")
        ax_m.set_xlabel("Length (mm)")
        ax_m.set_ylabel("Moment (N·mm)")

    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)
    return buf
