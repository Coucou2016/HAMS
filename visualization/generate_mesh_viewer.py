from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES = ["Cylinder", "DeepCwind", "HywindSpar", "Moonpool"]


def numeric_tokens(line: str) -> list[str]:
    out = []
    for token in line.replace(",", " ").split():
        try:
            float(token)
        except ValueError:
            continue
        out.append(token)
    return out


def parse_pnl(path: Path) -> dict:
    lines = path.read_text(errors="replace").splitlines()

    header_index = None
    header = None
    for i, line in enumerate(lines):
        toks = numeric_tokens(line)
        if len(toks) >= 4 and all(float(tok).is_integer() for tok in toks[:4]):
            vals = [int(float(tok)) for tok in toks[:4]]
            if vals[0] > 0 and vals[1] > 0:
                header_index = i
                header = vals
                break
    if header_index is None or header is None:
        raise ValueError(f"Cannot find mesh header in {path}")

    panel_count, node_count, x_sym, y_sym = header

    node_start = next(
        i + 1
        for i, line in enumerate(lines)
        if "Start Definition of Node Coordinates" in line
    )
    nodes = []
    i = node_start
    while len(nodes) < node_count and i < len(lines):
        toks = numeric_tokens(lines[i])
        if len(toks) >= 4:
            nodes.append([float(toks[1]), float(toks[2]), float(toks[3])])
        i += 1

    panel_start = next(
        i + 1 for i, line in enumerate(lines) if "Start Definition of Node Relations" in line
    )
    panels = []
    i = panel_start
    while len(panels) < panel_count and i < len(lines):
        toks = numeric_tokens(lines[i])
        if len(toks) >= 5:
            vertex_count = int(float(toks[1]))
            panels.append([int(float(tok)) - 1 for tok in toks[2 : 2 + vertex_count]])
        i += 1

    if len(nodes) != node_count or len(panels) != panel_count:
        raise ValueError(
            f"Incomplete mesh in {path}: nodes {len(nodes)}/{node_count}, "
            f"panels {len(panels)}/{panel_count}"
        )

    return {
        "raw_nodes": node_count,
        "raw_panels": panel_count,
        "x_symmetry": x_sym,
        "y_symmetry": y_sym,
        "nodes": nodes,
        "panels": panels,
    }


def mirror_combinations(x_sym: int, y_sym: int) -> list[tuple[int, int]]:
    xs = [1, -1] if x_sym else [1]
    ys = [1, -1] if y_sym else [1]
    return [(x, y) for x in xs for y in ys]


def expand_mesh(mesh: dict) -> dict:
    nodes = mesh["nodes"]
    panels = mesh["panels"]
    vertices: list[float] = []
    triangles: list[int] = []
    edges: list[int] = []

    for mx, my in mirror_combinations(mesh["x_symmetry"], mesh["y_symmetry"]):
        offset = len(vertices) // 3
        for x, y, z in nodes:
            vertices.extend([mx * x, my * y, z])

        for panel in panels:
            face = [offset + idx for idx in panel]
            if len(face) == 3:
                triangles.extend(face)
            elif len(face) == 4:
                triangles.extend([face[0], face[1], face[2], face[0], face[2], face[3]])
            else:
                for i in range(1, len(face) - 1):
                    triangles.extend([face[0], face[i], face[i + 1]])

            for i, a in enumerate(face):
                b = face[(i + 1) % len(face)]
                edges.extend([a, b])

    return {
        "rawNodes": mesh["raw_nodes"],
        "rawPanels": mesh["raw_panels"],
        "xSymmetry": mesh["x_symmetry"],
        "ySymmetry": mesh["y_symmetry"],
        "vertices": vertices,
        "triangles": triangles,
        "edges": edges,
    }


def bounds_for(parts: list[dict]) -> dict:
    coords = [[], [], []]
    for part in parts:
        verts = part["vertices"]
        for i in range(0, len(verts), 3):
            coords[0].append(verts[i])
            coords[1].append(verts[i + 1])
            coords[2].append(verts[i + 2])
    return {
        "min": [min(axis) for axis in coords],
        "max": [max(axis) for axis in coords],
    }


def build_data() -> dict:
    cases = []
    for name in CASES:
        case_dir = ROOT / "CertTest" / name / "Input"
        hull = expand_mesh(parse_pnl(case_dir / "HullMesh.pnl"))
        waterplane = expand_mesh(parse_pnl(case_dir / "WaterplaneMesh.pnl"))
        cases.append(
            {
                "name": name,
                "hull": hull,
                "waterplane": waterplane,
                "bounds": bounds_for([hull, waterplane]),
            }
        )
    return {"cases": cases}


def main() -> None:
    out = Path(__file__).with_name("mesh-data.js")
    data = build_data()
    out.write_text(
        "window.HAMS_MESH_DATA = " + json.dumps(data, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    for case in data["cases"]:
        hull = case["hull"]
        water = case["waterplane"]
        print(
            f"{case['name']}: hull panels={hull['rawPanels']} nodes={hull['rawNodes']}; "
            f"waterplane panels={water['rawPanels']} nodes={water['rawNodes']}"
        )
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
