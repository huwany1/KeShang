"""
模块: common.graph.neo4j_writer
职责: 提供最小的写接口：创建 Document 节点、Concept 节点与简单关系。
输入: 文档ID、概念名称列表与关系三元组。
输出: 无（写入图数据库）。
"""

from typing import Iterable, Tuple
from neo4j import Driver

from common.graph.neo4j_client import get_neo4j_driver


def ensure_document_and_concepts(document_id: str, concepts: Iterable[str]) -> None:
    """创建 Document 节点与 Concept 节点，并建立 MENTIONED_IN 关系。
    输入: document_id, 概念名称迭代器。
    输出: None。
    作用: MVP 入图占位，后续可扩展属性与权重。
    """
    driver: Driver = get_neo4j_driver()
    with driver.session() as session:
        session.execute_write(_create_doc_and_concepts_tx, document_id, list(concepts))


def _create_doc_and_concepts_tx(tx, document_id: str, concepts: list[str]) -> None:
    tx.run(
        "MERGE (d:Document {id: $doc}) RETURN d",
        doc=document_id,
    )
    for name in concepts:
        tx.run(
            "MERGE (c:Concept {name: $name})",
            name=name,
        )
        tx.run(
            "MATCH (c:Concept {name: $name}), (d:Document {id: $doc}) MERGE (c)-[:MENTIONED_IN]->(d)",
            name=name,
            doc=document_id,
        )


def create_related_edges(pairs: Iterable[Tuple[str, str]]) -> None:
    """为概念对建立 RELATED_TO 关系（无向，用双向有向边表示）。
    输入: 概念对迭代器 (a, b)。
    输出: None。
    作用: 可视化邻接示例。
    """
    driver: Driver = get_neo4j_driver()
    with driver.session() as session:
        for a, b in pairs:
            session.run(
                "MATCH (a:Concept {name: $a}), (b:Concept {name: $b}) MERGE (a)-[:RELATED_TO]->(b) MERGE (b)-[:RELATED_TO]->(a)",
                a=a,
                b=b,
            )
