import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


from constrained_generator import build_constrained_corpus
from corpus_builder import build_seed_grids


def build_lineage_graph(
    seed_grids: list[dict], child_grids: list[dict], elite_ids: set[str] | None = None
) -> dict:
    elite_ids = elite_ids or set()
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    orphans: list[str] = []

    for grid in seed_grids:
        nodes[grid["grid_id"]] = _node_for_grid(grid, node_type="seed", elite_ids=elite_ids)

    for grid in child_grids:
        nodes[grid["grid_id"]] = _node_for_grid(
            grid, node_type="candidate", elite_ids=elite_ids
        )

    for grid in child_grids:
        parent_id = grid.get("parent_grid_id")
        if parent_id and parent_id in nodes:
            edges.append(
                {
                    "parent_id": parent_id,
                    "child_id": grid["grid_id"],
                    "generation": grid.get("lineage", {}).get("generation", 0),
                    "mutation_events": grid.get("lineage", {}).get("mutation_events", []),
                    "elite": grid["grid_id"] in elite_ids,
                }
            )
        else:
            orphans.append(grid["grid_id"])

    return {"nodes": nodes, "edges": edges, "orphans": orphans}


def summarize_lineage_graph(graph: dict) -> dict:
    nodes = graph["nodes"]
    edges = graph["edges"]
    generation_counts = Counter(node["generation"] for node in nodes.values())
    parent_counts = Counter(edge["parent_id"] for edge in edges)
    elite_edges = [edge for edge in edges if edge["elite"]]
    dominant_count = max(parent_counts.values(), default=0)
    child_count = sum(1 for node in nodes.values() if node["type"] == "candidate")
    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "orphan_count": len(graph["orphans"]),
        "max_generation": max(generation_counts, default=0),
        "generation_counts": {str(key): value for key, value in sorted(generation_counts.items())},
        "founder_count": sum(1 for node in nodes.values() if node["type"] == "seed"),
        "candidate_count": child_count,
        "distinct_parent_count": len(parent_counts),
        "dominant_parent_id": parent_counts.most_common(1)[0][0] if parent_counts else None,
        "dominant_lineage_children": dominant_count,
        "dominant_lineage_share": round(dominant_count / child_count, 6)
        if child_count
        else 0,
        "elite_count": sum(1 for node in nodes.values() if node["elite"]),
        "elite_parent_count": len({edge["parent_id"] for edge in elite_edges}),
    }


def write_lineage(path: Path, graph: dict, summary: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": summary,
        "nodes": dict(sorted(graph["nodes"].items())),
        "edges": graph["edges"],
        "orphans": graph["orphans"],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def elite_ids_from_archive(path: Path) -> set[str]:
    archive = json.loads(path.read_text(encoding="utf-8"))
    return {
        elite["grid_id"]
        for elite in archive.get("archive", {}).get("elites", {}).values()
    }


def _node_for_grid(grid: dict, *, node_type: str, elite_ids: set[str]) -> dict:
    lineage = grid.get("lineage", {})
    return {
        "grid_id": grid["grid_id"],
        "type": node_type,
        "parent_grid_id": grid.get("parent_grid_id"),
        "generation": lineage.get("generation", 0),
        "ancestor_ids": lineage.get("ancestor_ids", []),
        "mutation_events": lineage.get("mutation_events", []),
        "elite": grid["grid_id"] in elite_ids,
    }


def _load_grids(path: Path) -> list[dict]:
    return [
        json.loads(file.read_text(encoding="utf-8"))
        for file in sorted(path.glob("*.json"))
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=200)
    parser.add_argument("--rng-seed", type=int, default=818)
    parser.add_argument("--archive", type=Path, default=Path("data/archives/map_elites_stage0.json"))
    parser.add_argument("--generated-dir", type=Path, default=Path("data/generated_grids/lineage_constrained"))
    parser.add_argument("--output", type=Path, default=Path("data/lineage/lineage_stage0.json"))
    args = parser.parse_args()

    seeds = build_seed_grids()
    children = build_constrained_corpus(seeds, count=args.count, rng_seed=args.rng_seed)
    args.generated_dir.mkdir(parents=True, exist_ok=True)
    for child in children:
        (args.generated_dir / f"{child['grid_id']}.json").write_text(
            json.dumps(child, indent=2) + "\n", encoding="utf-8"
        )

    elite_ids = elite_ids_from_archive(args.archive) if args.archive.exists() else set()
    graph = build_lineage_graph(seeds, children, elite_ids=elite_ids)
    summary = summarize_lineage_graph(graph)
    write_lineage(args.output, graph, summary)
    print(json.dumps({"summary": summary}, indent=2))


if __name__ == "__main__":
    main()
