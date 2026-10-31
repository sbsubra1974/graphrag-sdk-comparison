"""All Neo4j access lives here: one database holds both the vectors and the graph.

Graph shape:
  (:Document {name})-[:HAS_CHUNK]->(:Chunk {id, text, page, embedding})
  (:Chunk)-[:NEXT]->(:Chunk)                    reading order
  (:Chunk)-[:MENTIONS]->(:Entity {id, name, type, description})
  (:Entity)-[:RELATED_TO {type}]->(:Entity)
"""

from neo4j import GraphDatabase

from graphrag_cmp.settings import settings

VECTOR_INDEX = "chunk_embedding"

_driver = None


def driver():
    # One shared driver per process; it manages its own connection pool.
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
        )
    return _driver


def run(cypher: str, **params) -> list[dict]:
    """Run one Cypher query and return the rows as plain dicts."""
    records, _, _ = driver().execute_query(cypher, params)
    return [record.data() for record in records]


def create_schema() -> None:
    """Constraints for fast MERGEs, plus the vector index used for similarity search."""
    run("CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE")
    run("CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE")
    # Index options cannot be query parameters, so the dimension is formatted in.
    run(f"""
        CREATE VECTOR INDEX {VECTOR_INDEX} IF NOT EXISTS
        FOR (c:Chunk) ON c.embedding
        OPTIONS {{indexConfig: {{
            `vector.dimensions`: {int(settings.embedding_dimensions)},
            `vector.similarity_function`: 'cosine'
        }}}}
    """)


def save_chunks(source: str, chunks: list[dict]) -> None:
    """chunks: [{"id", "text", "page", "chunk_index", "embedding"}, ...]"""
    run("""
        MERGE (d:Document {name: $source})
        WITH d
        UNWIND $chunks AS row
        MERGE (c:Chunk {id: row.id})
        SET c.text = row.text, c.page = row.page, c.chunk_index = row.chunk_index
        // setNodeVectorProperty stores the list as a proper vector for the index
        WITH d, c, row
        CALL db.create.setNodeVectorProperty(c, 'embedding', row.embedding)
        MERGE (d)-[:HAS_CHUNK]->(c)
    """, source=source, chunks=chunks)
    # Link chunks in reading order so retrieval can pull in neighbours.
    run("""
        MATCH (d:Document {name: $source})-[:HAS_CHUNK]->(c:Chunk)
        WITH c ORDER BY c.chunk_index
        WITH collect(c) AS ordered
        UNWIND range(0, size(ordered) - 2) AS i
        WITH ordered[i] AS a, ordered[i + 1] AS b
        MERGE (a)-[:NEXT]->(b)
    """, source=source)


def entity_id(name: str) -> str:
    """Normalise names so "Neo4j" and "neo4j " become the same node."""
    return " ".join(name.lower().split())


def save_graph(chunk_id: str, graph: dict) -> None:
    """Write one chunk's extracted entities and relationships."""
    entities = [
        {"id": entity_id(e["name"]), "name": e["name"], "type": e.get("type", ""),
         "description": e.get("description", "")}
        for e in graph.get("entities", [])
    ]
    relationships = [
        {"source": entity_id(r["source"]), "target": entity_id(r["target"]),
         "type": r["type"].upper().replace(" ", "_")}
        for r in graph.get("relationships", [])
    ]
    run("""
        MATCH (c:Chunk {id: $chunk_id})
        UNWIND $entities AS row
        MERGE (e:Entity {id: row.id})
        // keep the first name/type we saw, but fill in a description if missing
        ON CREATE SET e.name = row.name, e.type = row.type
        SET e.description = coalesce(e.description, row.description)
        MERGE (c)-[:MENTIONS]->(e)
    """, chunk_id=chunk_id, entities=entities)
    run("""
        UNWIND $relationships AS row
        MERGE (a:Entity {id: row.source}) ON CREATE SET a.name = row.source
        MERGE (b:Entity {id: row.target}) ON CREATE SET b.name = row.target
        MERGE (a)-[r:RELATED_TO {type: row.type}]->(b)
    """, relationships=relationships)


def reset() -> None:
    """Delete everything. Handy while experimenting."""
    run("MATCH (n) DETACH DELETE n")
