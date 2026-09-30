"""Generate a readable PNG overview from the live Neo4j knowledge graph."""

from pathlib import Path
import json
import csv

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx

from src.graph.connection import Neo4jConnection


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "reports" / "charts" / "neo4j_graph_overview.png"
VISIBLE_LABELS = {"Place", "Station", "Line", "Hotel"}
COLORS = {
    "Place": "#F59E0B",
    "Station": "#2563EB",
    "Line": "#DC2626",
    "Hotel": "#8B5CF6",
}


def _short_name(properties: dict, label: str) -> str:
    raw = (
        properties.get("name_en")
        or properties.get("name_th")
        or properties.get("name")
        or properties.get("station_id")
        or properties.get("place_id")
        or properties.get("line_id")
        or properties.get("hotel_id")
        or label
    )
    return str(raw)[:26]


def generate_overview(output_path: Path = OUTPUT) -> Path:
    driver = Neo4jConnection.get_driver()
    if driver is None:
        raise RuntimeError("Neo4j is unavailable; start the database before generating the image")

    with open(ROOT / "data" / "processed" / "graph_cache.json", encoding="utf-8") as f:
        current_ids = set(json.load(f)["nodes"].keys())
    with open(ROOT / "data" / "processed" / "lines.csv", encoding="utf-8-sig", newline="") as f:
        current_ids.update(row["line_id"] for row in csv.DictReader(f))
    current_ids = sorted(current_ids)

    graph = nx.Graph()
    with driver.session() as session:
        nodes = session.run(
            """
            MATCH (n)
            WHERE any(label IN labels(n) WHERE label IN $visible_labels)
              AND coalesce(n.station_id, n.place_id, n.line_id, n.hotel_id) IN $current_ids
            RETURN elementId(n) AS id, labels(n) AS labels, properties(n) AS props
            """,
            visible_labels=sorted(VISIBLE_LABELS),
            current_ids=current_ids,
        )
        for record in nodes:
            label = next((x for x in record["labels"] if x in VISIBLE_LABELS), "Other")
            graph.add_node(
                record["id"],
                kind=label,
                display=_short_name(record["props"], label),
            )

        relationships = session.run(
            """
            MATCH (a)-[r]->(b)
            WHERE elementId(a) IN $node_ids AND elementId(b) IN $node_ids
            RETURN elementId(a) AS source, elementId(b) AS target, type(r) AS kind
            """,
            node_ids=list(graph.nodes),
        )
        for record in relationships:
            graph.add_edge(record["source"], record["target"], kind=record["kind"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    positions = nx.spring_layout(graph, seed=23, k=1.25, iterations=350)
    fig, ax = plt.subplots(figsize=(18, 13), dpi=220)
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#F8FAFC")

    nx.draw_networkx_edges(
        graph,
        positions,
        ax=ax,
        edge_color="#94A3B8",
        alpha=0.34,
        width=0.9,
    )
    for kind in ("Station", "Place", "Line", "Hotel"):
        selected = [n for n, data in graph.nodes(data=True) if data["kind"] == kind]
        nx.draw_networkx_nodes(
            graph,
            positions,
            nodelist=selected,
            node_color=COLORS[kind],
            node_size=620 if kind == "Line" else 420,
            edgecolors="white",
            linewidths=1.4,
            alpha=0.95,
            label=f"{kind} ({len(selected)})",
            ax=ax,
        )

    labels = {n: data["display"] for n, data in graph.nodes(data=True)}
    nx.draw_networkx_labels(
        graph,
        positions,
        labels=labels,
        font_size=6.2,
        font_color="#0F172A",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.68, "pad": 0.2},
        ax=ax,
    )
    ax.legend(loc="upper left", frameon=True, framealpha=0.95, fontsize=10)
    ax.set_title(
        f"Tokyo Tourism & Transit Knowledge Graph\n"
        f"Live Neo4j query: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} visible relationships",
        fontsize=18,
        fontweight="bold",
        color="#0F172A",
        pad=18,
    )
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Saved Neo4j overview: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_overview()
