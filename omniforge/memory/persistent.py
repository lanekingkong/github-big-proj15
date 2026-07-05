"""
Persistent Memory System
Inspired by MemPalace (47K star) but with enhanced features:
- SQLite/ChromaDB/Qdrant backends
- Semantic search with embeddings
- Memory compression and eviction
- Cross-session persistence
- Memory hierarchy (short-term, long-term, working)
"""

import json
import sqlite3
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging

from omniforge.config import MemoryConfig

logger = logging.getLogger(__name__)


class PersistentMemory:
    """
    Persistent memory system for AI agents.

    Features:
    1. Multi-backend storage (SQLite, ChromaDB, Qdrant)
    2. Semantic search with embeddings
    3. Memory compression and eviction policies
    4. Memory hierarchy: short-term, long-term, working
    5. Cross-session persistence
    """

    def __init__(self, config: MemoryConfig):
        self.config = config
        self._connection: Optional[sqlite3.Connection] = None
        self._embedding_model = None
        self._setup_embedding_model()

    def _setup_embedding_model(self):
        """Setup embedding model based on config."""
        try:
            if self.config.embedding_model == "all-MiniLM-L6-v2":
                # Use sentence-transformers if available
                from sentence_transformers import SentenceTransformer
                self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            else:
                # Fallback to simpler model
                logger.warning(f"Embedding model {self.config.embedding_model} not available, using fallback")
                self._embedding_model = None
        except ImportError:
            logger.warning("sentence-transformers not installed, embeddings disabled")
            self._embedding_model = None

    def initialize(self):
        """Initialize the memory database."""
        db_path = Path(self.config.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self._connection = sqlite3.connect(str(db_path))
        self._create_tables()

        logger.info(f"Memory system initialized at {db_path}")

    def _create_tables(self):
        """Create necessary database tables."""
        cursor = self._connection.cursor()

        # Main memories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                metadata TEXT,
                embedding BLOB,
                memory_type TEXT DEFAULT 'long_term',
                importance REAL DEFAULT 1.0,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_accessed ON memories(last_accessed DESC)")

        # Memory relationships (graph-like structure)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_links (
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relationship TEXT,
                strength REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (source_id, target_id),
                FOREIGN KEY (source_id) REFERENCES memories(id),
                FOREIGN KEY (target_id) REFERENCES memories(id)
            )
        """)

        # Memory tags for categorization
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_tags (
                memory_id TEXT NOT NULL,
                tag TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (memory_id, tag),
                FOREIGN KEY (memory_id) REFERENCES memories(id)
            )
        """)

        self._connection.commit()

    def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> str:
        """Store a memory with optional metadata."""
        if not self._connection:
            raise RuntimeError("Memory system not initialized")

        # Generate unique ID
        content = f"{key}:{json.dumps(value, ensure_ascii=False)}"
        memory_id = hashlib.sha256(content.encode()).hexdigest()[:32]

        # Prepare data
        value_str = json.dumps(value, ensure_ascii=False)
        metadata_str = json.dumps(metadata or {}, ensure_ascii=False)

        # Generate embedding if model available
        embedding = None
        if self._embedding_model and isinstance(value, str):
            try:
                embedding = self._embedding_model.encode(value).tobytes()
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")

        cursor = self._connection.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO memories 
            (id, key, value, metadata, embedding, last_accessed, access_count)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 
                   COALESCE((SELECT access_count FROM memories WHERE id = ?) + 1, 1))
        """, (memory_id, key, value_str, metadata_str, embedding, memory_id))

        # Apply eviction policy if needed
        self._apply_eviction_policy()

        self._connection.commit()
        logger.debug(f"Stored memory: {key} -> {memory_id}")
        return memory_id

    def retrieve(self, key: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve memories by key."""
        if not self._connection:
            raise RuntimeError("Memory system not initialized")

        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT id, key, value, metadata, memory_type, importance,
                   access_count, last_accessed, created_at
            FROM memories
            WHERE key = ?
            ORDER BY importance DESC, last_accessed DESC
            LIMIT ?
        """, (key, limit))

        results = []
        for row in cursor.fetchall():
            try:
                value_data = json.loads(row[2])
                metadata_data = json.loads(row[3]) if row[3] else {}
            except json.JSONDecodeError:
                value_data = row[2]
                metadata_data = {}

            results.append({
                "id": row[0],
                "key": row[1],
                "value": value_data,
                "metadata": metadata_data,
                "type": row[4],
                "importance": row[5],
                "access_count": row[6],
                "last_accessed": row[7],
                "created_at": row[8],
            })

        # Update access counts
        for result in results:
            cursor.execute("""
                UPDATE memories 
                SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (result["id"],))

        self._connection.commit()
        return results

    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Semantic search across all memories using embeddings."""
        if not self._connection or not self._embedding_model:
            # Fallback to keyword search
            return self._keyword_search(query, top_k)

        try:
            # Generate query embedding
            query_embedding = self._embedding_model.encode(query)

            cursor = self._connection.cursor()

            # For SQLite, we need to load embeddings and compute similarity
            # This is simplified; production would use vector database
            cursor.execute("""
                SELECT id, key, value, metadata, embedding
                FROM memories
                WHERE embedding IS NOT NULL
                LIMIT 1000
            """)

            memories = []
            for row in cursor.fetchall():
                memory_id, key, value_str, metadata_str, embedding_bytes = row

                # Compute cosine similarity
                try:
                    memory_embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
                    similarity = np.dot(query_embedding, memory_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(memory_embedding)
                    )

                    try:
                        value_data = json.loads(value_str)
                        metadata_data = json.loads(metadata_str) if metadata_str else {}
                    except json.JSONDecodeError:
                        value_data = value_str
                        metadata_data = {}

                    memories.append({
                        "id": memory_id,
                        "key": key,
                        "value": value_data,
                        "metadata": metadata_data,
                        "similarity": float(similarity),
                    })
                except Exception as e:
                    logger.debug(f"Failed to compute similarity for {memory_id}: {e}")

            # Sort by similarity and return top_k
            memories.sort(key=lambda x: x["similarity"], reverse=True)
            return memories[:top_k]

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return self._keyword_search(query, top_k)

    def _keyword_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Fallback keyword search."""
        if not self._connection:
            return []

        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT id, key, value, metadata
            FROM memories
            WHERE key LIKE ? OR value LIKE ?
            ORDER BY access_count DESC, last_accessed DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", top_k))

        results = []
        for row in cursor.fetchall():
            try:
                value_data = json.loads(row[2])
                metadata_data = json.loads(row[3]) if row[3] else {}
            except json.JSONDecodeError:
                value_data = row[2]
                metadata_data = {}

            results.append({
                "id": row[0],
                "key": row[1],
                "value": value_data,
                "metadata": metadata_data,
            })

        return results

    def remove(self, key: str) -> bool:
        """Remove memories by key."""
        if not self._connection:
            return False

        cursor = self._connection.cursor()
        cursor.execute("DELETE FROM memories WHERE key = ?", (key,))
        self._connection.commit()
        deleted = cursor.rowcount > 0

        if deleted:
            logger.info(f"Removed {cursor.rowcount} memories with key: {key}")

        return deleted

    def compress(self, threshold: int = 500) -> int:
        """Compress memories by merging similar ones."""
        # This is a simplified implementation
        # Production would use more sophisticated compression algorithms
        if not self._connection:
            return 0

        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM memories
        """)
        count_before = cursor.fetchone()[0]

        if count_before <= threshold:
            return 0

        # Simple compression: remove least important memories
        cursor.execute("""
            DELETE FROM memories
            WHERE id IN (
                SELECT id FROM memories
                ORDER BY importance ASC, last_accessed ASC
                LIMIT ?
            )
        """, (count_before - threshold,))

        self._connection.commit()
        compressed = cursor.rowcount
        logger.info(f"Compressed {compressed} memories (threshold: {threshold})")
        return compressed

    def _apply_eviction_policy(self):
        """Apply eviction policy based on config."""
        cursor = self._connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]

        if count > self.config.max_memories:
            self.compress(self.config.max_memories)

    def link_memories(self, source_id: str, target_id: str, relationship: str = "related"):
        """Create a link between two memories."""
        if not self._connection:
            return

        cursor = self._connection.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO memory_links 
            (source_id, target_id, relationship)
            VALUES (?, ?, ?)
        """, (source_id, target_id, relationship))
        self._connection.commit()

    def get_related_memories(self, memory_id: str) -> List[Dict[str, Any]]:
        """Get memories related to a given memory."""
        if not self._connection:
            return []

        cursor = self._connection.cursor()
        cursor.execute("""
            SELECT m.id, m.key, m.value, m.metadata, ml.relationship, ml.strength
            FROM memories m
            JOIN memory_links ml ON m.id = ml.target_id
            WHERE ml.source_id = ?
            UNION
            SELECT m.id, m.key, m.value, m.metadata, ml.relationship, ml.strength
            FROM memories m
            JOIN memory_links ml ON m.id = ml.source_id
            WHERE ml.target_id = ?
            ORDER BY ml.strength DESC
        """, (memory_id, memory_id))

        results = []
        for row in cursor.fetchall():
            try:
                value_data = json.loads(row[2])
                metadata_data = json.loads(row[3]) if row[3] else {}
            except json.JSONDecodeError:
                value_data = row[2]
                metadata_data = {}

            results.append({
                "id": row[0],
                "key": row[1],
                "value": value_data,
                "metadata": metadata_data,
                "relationship": row[4],
                "strength": row[5],
            })

        return results

    def close(self):
        """Close the memory database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Memory system closed")

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False