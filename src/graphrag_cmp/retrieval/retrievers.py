"""SDK-agnostic retrievers. Both SDK folders call these, so comparisons are fair."""

from graphrag_cmp import neo4j_store
from graphrag_cmp.ingestion.embed import embed_query


def vector_search(question: str, k: int = 5) -> list[dict]:
    """Plain semantic search: the k chunks whose embeddings are closest to the question."""
    return neo4j_store.run(f"""
        CALL db.index.vector.queryNodes('{neo4j_store.VECTOR_INDEX}', $k, $embedding)
        YIELD node, score
        RETURN node.id AS id, node.page AS page, node.text AS text, score
        ORDER BY score DESC
    """, k=k, embedding=embed_query(question))


def graph_search(question: str, k: int = 5) -> list[dict]:
    """GraphRAG retrieval: vector search finds entry chunks, then the graph adds context.

    For each matching chunk we also return:
      - the entities it mentions
      - facts (entity relationships) one hop away from those entities
      - the next chunk in reading order, so cut-off sentences are completed
    """
    return neo4j_store.run(f"""
        CALL db.index.vector.queryNodes('{neo4j_store.VECTOR_INDEX}', $k, $embedding)
        YIELD node AS chunk, score
        RETURN chunk.id AS id, chunk.page AS page, chunk.text AS text, score,
               // COLLECT {{}} subqueries keep each expansion separate (no row explosion)
               COLLECT {{
                   MATCH (chunk)-[:MENTIONS]->(e:Entity) RETURN e.name
               }} AS entities,
               COLLECT {{
                   MATCH (chunk)-[:MENTIONS]->(:Entity)-[r:RELATED_TO]-(:Entity)
                   RETURN DISTINCT startNode(r).name + ' ' + r.type + ' ' + endNode(r).name
                   LIMIT 15
               }} AS facts,
               COLLECT {{
                   MATCH (chunk)-[:NEXT]->(n:Chunk) RETURN n.text
               }} AS next_text
        ORDER BY score DESC
    """, k=k, embedding=embed_query(question))


def entity_neighbourhood(name: str, limit: int = 20) -> dict:
    """Look up one entity by name and return its description, facts and source chunks."""
    rows = neo4j_store.run("""
        MATCH (e:Entity) WHERE e.id CONTAINS $id
        WITH e LIMIT 1
        RETURN e.name AS name, e.type AS type, e.description AS description,
               COLLECT {
                   MATCH (e)-[r:RELATED_TO]-(:Entity)
                   RETURN startNode(r).name + ' ' + r.type + ' ' + endNode(r).name LIMIT $limit
               } AS facts,
               COLLECT {
                   MATCH (c:Chunk)-[:MENTIONS]->(e) RETURN c.id LIMIT 5
               } AS chunk_ids
    """, id=neo4j_store.entity_id(name), limit=limit)
    return rows[0] if rows else {"name": name, "error": "entity not found"}


def format_chunks(chunks: list[dict]) -> str:
    """Render retrieved chunks as numbered context blocks for the prompt."""
    blocks = []
    for c in chunks:
        lines = [f"[source: {c['id']} | page {c['page']}]", c["text"]]
        # Graph extras are only present for graph_search results.
        if c.get("entities"):
            lines.append("Entities: " + ", ".join(c["entities"]))
        if c.get("facts"):
            lines.append("Related facts:\n- " + "\n- ".join(c["facts"]))
        if c.get("next_text"):
            lines.append("Continues: " + c["next_text"][0][:300])
        blocks.append("\n".join(lines))
    return "\n\n---\n\n".join(blocks)
