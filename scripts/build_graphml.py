#!/usr/bin/env python3
"""Convert release_catalog.yml (LinkML) to release_catalog.graphml for Neo4j/APOC import."""

from __future__ import annotations

import argparse
import sys

import networkx as nx
import requests
import yaml


def load_yaml(source: str) -> dict:
    if source.startswith(("http://", "https://")):
        resp = requests.get(source, timeout=30)
        resp.raise_for_status()
        return yaml.safe_load(resp.content)
    with open(source, "r", encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def build_graph(data: dict) -> nx.Graph:
    G = nx.Graph()

    # Nodes first so edges can resolve forward references to any component id.
    id_to_node: dict[str, int] = {}
    for node_id, component in enumerate(data["components"], start=1):
        attrs = component.copy()
        attrs["labels"] = ":Component"
        attrs.pop("hasDependentComponents", None)
        for key, value in attrs.items():
            if value is None:
                attrs[key] = ""  # GraphML cannot serialize None
        G.add_node(node_id, **attrs)
        id_to_node[component["id"]] = node_id

    # Edges by exact id; collect any dangling references and fail with the full list.
    dangling: list[str] = []
    for node_id, component in enumerate(data["components"], start=1):
        for rel in component.get("hasDependentComponents") or []:
            target = id_to_node.get(rel["related_to"])
            if target is None:
                dangling.append(f"{component['id']} -> {rel['related_to']}")
            elif rel["relationship_type"] == "DependsOn":
                G.add_edge(node_id, target, label=rel["relationship_type"])

    if dangling:
        raise KeyError("Unknown component id(s) referenced:\n  " + "\n  ".join(dangling))

    return G


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="release_catalog.yml")
    parser.add_argument("--output", default="release_catalog.graphml")
    args = parser.parse_args(argv)

    graph = build_graph(load_yaml(args.data))
    nx.write_graphml(graph, args.output, named_key_ids=True)
    print(f"Wrote {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
