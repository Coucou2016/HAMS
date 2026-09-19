from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from generate_mesh_viewer import CASES, ROOT, expand_mesh, parse_pnl


OUT_DIR = Path(__file__).with_name("snapshots")


def triangles_as_faces(part: dict) -> list[list[list[float]]]:
    vertices = part["vertices"]
    tris = part["triangles"]
    faces = []
    for i in range(0, len(tris), 3):
        face = []
        for idx in tris[i : i + 3]:
            j = idx * 3
            face.append([vertices[j], vertices[j + 1], vertices[j + 2]])
        faces.append(face)
    return faces


def set_equal_axes(ax, bounds: dict) -> None:
    mins = bounds["min"]
    maxs = bounds["max"]
    centers = [(a + b) / 2 for a, b in zip(mins, maxs)]
    radius = max(b - a for a, b in zip(mins, maxs)) / 2
    radius = radius or 1
    ax.set_xlim(centers[0] - radius, centers[0] + radius)
    ax.set_ylim(centers[1] - radius, centers[1] + radius)
    ax.set_zlim(centers[2] - radius, centers[2] + radius)


def bounds_for(parts: list[dict]) -> dict:
    mins = [float("inf"), float("inf"), float("inf")]
    maxs = [float("-inf"), float("-inf"), float("-inf")]
    for part in parts:
        verts = part["vertices"]
        for i in range(0, len(verts), 3):
            for axis in range(3):
                value = verts[i + axis]
                mins[axis] = min(mins[axis], value)
                maxs[axis] = max(maxs[axis], value)
    return {"min": mins, "max": maxs}


def load_case(name: str) -> tuple[dict, dict, dict]:
    case_dir = ROOT / "CertTest" / name / "Input"
    hull = expand_mesh(parse_pnl(case_dir / "HullMesh.pnl"))
    water = expand_mesh(parse_pnl(case_dir / "WaterplaneMesh.pnl"))
    return hull, water, bounds_for([hull, water])


def draw_case(ax, name: str) -> None:
    hull, water, bounds = load_case(name)

    hull_collection = Poly3DCollection(
        triangles_as_faces(hull),
        facecolor="#287d7a",
        edgecolor="#26322f",
        linewidth=0.08,
        alpha=0.88,
    )
    water_collection = Poly3DCollection(
        triangles_as_faces(water),
        facecolor="#e59a35",
        edgecolor="#6e5435",
        linewidth=0.08,
        alpha=0.34,
    )

    ax.add_collection3d(hull_collection)
    ax.add_collection3d(water_collection)
    set_equal_axes(ax, bounds)
    ax.view_init(elev=22, azim=-42)
    ax.set_title(name, pad=10)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.grid(False)


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)

    fig = plt.figure(figsize=(16, 12), dpi=160)
    for i, name in enumerate(CASES, 1):
        ax = fig.add_subplot(2, 2, i, projection="3d")
        draw_case(ax, name)
    fig.tight_layout()
    overview = OUT_DIR / "hams-mesh-overview.png"
    fig.savefig(overview, bbox_inches="tight")
    plt.close(fig)

    for name in CASES:
        fig = plt.figure(figsize=(9, 7), dpi=160)
        ax = fig.add_subplot(1, 1, 1, projection="3d")
        draw_case(ax, name)
        path = OUT_DIR / f"{name.lower()}-mesh.png"
        fig.tight_layout()
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        print(path)

    print(overview)


if __name__ == "__main__":
    main()
