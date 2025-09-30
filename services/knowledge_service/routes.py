"""
模块: services.knowledge_service.routes
职责: 提供知识图谱查询 API（按概念或文档ID）。
输入: 文档ID或概念名。
输出: 概念节点与关系（占位）。
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from common.graph.neo4j_client import run_query
from common.security.deps import jwt_auth

router = APIRouter(prefix="/knowledge", tags=["knowledge"]) 


@router.get("/concepts")
async def list_related_concepts(concept: str = Query(..., min_length=1), claims: dict = Depends(jwt_auth)) -> dict:
    """查询与指定概念相关的概念列表（占位）。
    输入: concept 概念名称。
    输出: 相关概念数组。
    作用: 支撑前端展示知识邻接。
    """
    cypher = """
    MATCH (c:Concept {name: $name})-[:RELATED_TO]->(other:Concept)
    RETURN other.name AS name
    LIMIT 50
    """
    names = [row["name"] for row in run_query(cypher, {"name": concept})]
    return {"concept": concept, "related": names}


@router.get("/documents/{document_id}/graph")
async def get_document_graph(document_id: str, claims: dict = Depends(jwt_auth)) -> dict:
    """按文档ID返回图谱子图（概念节点与边）。
    输入: document_id。
    输出: { nodes: [{id,name}], edges: [{source,target}] }。
    作用: 供前端可视化文档关联概念与关系。
    """
    # 查询属于该文档的概念节点
    node_query = """
    MATCH (c:Concept)-[:MENTIONED_IN]->(d:Document {id: $doc})
    RETURN c.name AS name
    LIMIT 200
    """
    nodes = [row["name"] for row in run_query(node_query, {"doc": document_id})]
    if not nodes:
        # 文档不存在或尚未入图
        raise HTTPException(status_code=404, detail="Graph not found for document")

    # 查询这些概念之间的关系边
    edge_query = """
    MATCH (a:Concept)-[:MENTIONED_IN]->(d:Document {id: $doc}),
          (b:Concept)-[:MENTIONED_IN]->(d:Document {id: $doc}),
          (a)-[:RELATED_TO]->(b)
    RETURN a.name AS source, b.name AS target
    LIMIT 1000
    """
    edges = [{"source": r["source"], "target": r["target"]} for r in run_query(edge_query, {"doc": document_id})]
    node_objs = [{"id": n, "name": n} for n in nodes]
    return {"documentId": document_id, "nodes": node_objs, "edges": edges}
