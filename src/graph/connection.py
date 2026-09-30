"""
Neo4j Graph Database Connection Manager
จัดการการเชื่อมต่อ Neo4j ผ่าน Bolt Protocol
พร้อมระบบ Graceful Fallback (NetworkX In-Memory Graph) กรณี Neo4j ออฟไลน์
"""
import os
import socket
from urllib.parse import urlparse
from typing import Optional, Tuple
from dotenv import load_dotenv
from neo4j import GraphDatabase, Driver

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
# แปลง localhost เป็น 127.0.0.1 เพื่อความเสถียรบน Windows IPv4
if "localhost" in NEO4J_URI:
    NEO4J_URI = NEO4J_URI.replace("localhost", "127.0.0.1")

NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "yuE5Qlvzd_8FkZKM26rZtnSQjOmdIdTq")

def _configured_endpoint() -> Tuple[str, int]:
    """Return the host and Bolt port from the configured local or Aura URI."""
    parsed = urlparse(NEO4J_URI)
    return parsed.hostname or "127.0.0.1", parsed.port or 7687


def is_neo4j_port_open(
    host: Optional[str] = None,
    port: Optional[int] = None,
    timeout: float = 1.0,
) -> bool:
    """ตรวจสอบว่า Port ของ Neo4j เปิดพร้อมรับการเชื่อมต่อหรือไม่"""
    try:
        configured_host, configured_port = _configured_endpoint()
        host = host or configured_host
        port = port or configured_port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

class Neo4jConnection:
    """
    Singleton Class สำหรับจัดการ Neo4j Driver Connection
    """
    _driver: Optional[Driver] = None
    _checked: bool = False

    @classmethod
    def get_driver(cls) -> Optional[Driver]:
        """ดึง instance ของ Driver หากยังไม่มีจะทำการสร้างใหม่"""
        if cls._driver is not None:
            return cls._driver
        if cls._checked:
            return None

        cls._checked = True
        if not is_neo4j_port_open(timeout=0.2):
            return None

        try:
            cls._driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
                connection_timeout=3.0,
                max_connection_lifetime=300
            )
            # ตรวจสอบความถูกต้องของการ Authentication
            with cls._driver.session() as session:
                session.run("RETURN 1").single()
            return cls._driver
        except Exception as e:
            print(f"[Neo4jConnection] Warning: Could not connect to Neo4j ({e}). Switching to in-memory fallback.")
            cls._driver = None
            return None

    @classmethod
    def close(cls):
        """ปิดการเชื่อมต่อ Driver"""
        if cls._driver is not None:
            cls._driver.close()
            cls._driver = None

    @classmethod
    def is_connected(cls) -> bool:
        """ตรวจสอบว่าเชื่อมต่อกับ Neo4j สำเร็จหรือไม่"""
        driver = cls.get_driver()
        return driver is not None
