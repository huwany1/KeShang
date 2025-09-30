"""
模块: common.graph.neo4j_client
职责: 提供 Neo4j 驱动连接工厂与最小查询工具。
输入: settings 中的 Neo4j 配置。
输出: get_neo4j_driver, run_query。
"""

from typing import Any, Dict, Iterable
from neo4j import GraphDatabase, Driver

from common.config.settings import settings


def get_neo4j_driver() -> Driver:
    """创建 Neo4j 驱动。
    输入: 无。
    输出: neo4j.Driver 实例。
    作用: 统一获取图数据库连接。
    """
    return GraphDatabase.driver(settings.neo4jUri, auth=(settings.neo4jUser, settings.neo4jPassword))


def run_query(cypher: str, parameters: Dict[str, Any] | None = None) -> Iterable[Dict[str, Any]]:
    """执行只读查询并返回结果迭代器。
    输入: Cypher 字符串与参数。
    输出: 结果字典的可迭代对象。
    作用: MVP 查询接口占位；写操作由具体服务封装。
    """
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run(cypher, parameters or {})
        for record in result:
            yield dict(record)
