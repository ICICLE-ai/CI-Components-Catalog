#!/usr/bin/env python3
"""Wipe Neo4j and re-import the catalog GraphML via APOC. Config from env (.env locally, secrets in CI)."""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from neo4j import GraphDatabase


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        sys.exit(f"ERROR: {name} is not set.")
    return value


def main() -> int:
    load_dotenv()
    uri = require_env("NEO4J_URI")
    user = require_env("NEO4J_USER")
    password = require_env("NEO4J_PASSWORD")
    graphml_url = require_env("GRAPHML_URL")

    driver = GraphDatabase.driver(uri, auth=(user, password), max_connection_lifetime=30)
    try:
        driver.verify_connectivity()
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            record = session.run(
                "CALL apoc.import.graphml($url, {readLabels: true})", url=graphml_url
            ).single()
            print(f"Imported {graphml_url}: {dict(record) if record else 'done'}")
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
