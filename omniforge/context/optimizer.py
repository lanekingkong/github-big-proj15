"""
Context Optimization Engine
Inspired by headroom (6.6K star) with 60-95% compression capabilities.

Strategies:
- Semantic: Preserve meaning, reduce verbosity
- Token: Direct token-level compression
- Hybrid: Combine both for optimal results
"""

import re
import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass

from omniforge.config import ContextConfig

logger = logging.getLogger(__name__)


@dataclass
class CompressionResult:
    """Result of context compression."""
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    preserved_sections: List[str]
    removed_sections: List[str]
    compressed_text: str


class TokenEstimator:
    """Estimate token counts for text content."""

    @staticmethod
    def estimate(text: str) -> int:
        """Estimate token count using multiple heuristics."""
        if not text:
            return 0

        # Simple estimation: ~4 chars per token for English, ~1.5 for Chinese
        english_chars = len(re.findall(r'[a-zA-Z0-9\s]', text))
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]', text))
        other_chars = len(text) - english_chars - chinese_chars

        tokens = (english_chars / 4) + (chinese_chars / 1.5) + (other_chars / 4)
        return max(1, int(tokens))


class SemanticCompressor:
    """Compress text while preserving semantic meaning."""

    FILLER_PATTERNS = [
        r'\b(basically|essentially|literally|actually|just|really|very|quite|rather|simply)\b',
        r'\b(it should be noted that|it is worth mentioning that|it is important to note that)\b',
        r'\b(in order to|for the purpose of|with regard to|in terms of|in the context of)\b',
        r'\b(needless to say|it goes without saying|as a matter of fact)\b',
    ]

    REDUNDANT_PHRASES = [
        ("in order to", "to"),
        ("for the purpose of", "for"),
        ("with regard to", "about"),
        ("in terms of", "in"),
        ("in the context of", "in"),
        ("a number of", "several"),
        ("the majority of", "most"),
        ("due to the fact that", "because"),
        ("at the present time", "now"),
        ("in the near future", "soon"),
        ("has the ability to", "can"),
        ("is able to", "can"),
        ("it is possible that", "may"),
        ("there is a need for", "needs"),
        ("in the event that", "if"),
    ]

    def compress(self, text: str, ratio: float = 0.6) -> CompressionResult:
        """Compress text to target ratio while preserving meaning."""
        original_tokens = TokenEstimator.estimate(text)
        target_tokens = int(original_tokens * (1 - ratio))
        compressed = text

        # Step 1: Remove filler words
        for pattern in self.FILLER_PATTERNS:
            compressed = re.sub(pattern, '', compressed, flags=re.IGNORECASE)

        # Step 2: Replace redundant phrases
        for long_form, short_form in self.REDUNDANT_PHRASES:
            compressed = re.sub(
                re.escape(long_form), short_form,
                compressed, flags=re.IGNORECASE
            )

        # Step 3: Remove repeated sentences
        lines = compressed.split('\n')
        seen = set()
        unique_lines = []
        for line in lines:
            normalized = line.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_lines.append(line)
            elif not normalized:
                unique_lines.append(line)  # Keep empty lines for structure
            else:
                pass  # Skip duplicate

        compressed = '\n'.join(unique_lines)

        # Step 4: Collapse multiple spaces
        compressed = re.sub(r' {2,}', ' ', compressed)
        compressed = re.sub(r'\n{3,}', '\n\n', compressed)

        compressed_tokens = TokenEstimator.estimate(compressed)
        actual_ratio = 1 - (compressed_tokens / original_tokens) if original_tokens > 0 else 0

        return CompressionResult(
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=actual_ratio,
            preserved_sections=["core_content"],
            removed_sections=["fillers", "redundancy"],
            compressed_text=compressed.strip(),
        )


class ContextOptimizer:
    """
    Context optimization engine for AI agent interactions.
    Reduces token usage while preserving meaning quality.
    """

    def __init__(self, config: ContextConfig):
        self.config = config
        self._semantic_compressor = SemanticCompressor()
        self._chunk_cache: Dict[str, List[str]] = {}

    def optimize(self, content: str, preserve_sections: Optional[List[str]] = None) -> str:
        """Optimize content for AI agent context."""
        if not self.config.enabled or not content:
            return content

        preserve_sections = preserve_sections or []

        if self.config.strategy == "semantic":
            result = self._optimize_semantic(content, preserve_sections)
        elif self.config.strategy == "token":
            result = self._optimize_token(content, preserve_sections)
        else:  # hybrid
            result = self._optimize_hybrid(content, preserve_sections)

        return result

    def _optimize_semantic(self, content: str, preserve_sections: List[str]) -> str:
        """Semantic compression that preserves meaning."""
        # Split into sections
        sections = self._split_sections(content)

        compressed_sections = []
        for section in sections:
            # Check if section should be preserved
            should_preserve = any(
                ps.lower() in section["title"].lower()
                for ps in preserve_sections
            ) if preserve_sections else False

            if should_preserve:
                compressed_sections.append(section["content"])
            else:
                result = self._semantic_compressor.compress(
                    section["content"],
                    self.config.compression_ratio
                )
                compressed_sections.append(result.compressed_text)

        return '\n\n'.join(compressed_sections)

    def _optimize_token(self, content: str, preserve_sections: List[str]) -> str:
        """Pure token-level optimization."""
        # Remove empty lines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        # Remove trailing whitespace
        content = '\n'.join(line.rstrip() for line in content.split('\n'))

        # Truncate if needed
        tokens = self.estimate_tokens(content)
        if tokens > self.config.max_tokens:
            # Keep first portion as it's usually most important
            lines = content.split('\n')
            kept_lines = []
            kept_tokens = 0
            target = int(self.config.max_tokens * 0.8)
            for line in lines:
                line_tokens = self.estimate_tokens(line)
                if kept_tokens + line_tokens > target:
                    break
                kept_lines.append(line)
                kept_tokens += line_tokens
            content = '\n'.join(kept_lines)

        return content

    def _optimize_hybrid(self, content: str, preserve_sections: List[str]) -> str:
        """Combine semantic and token optimization."""
        result = self._optimize_semantic(content, preserve_sections)
        result = self._optimize_token(result, preserve_sections)
        return result

    def _split_sections(self, content: str) -> List[Dict[str, str]]:
        """Split content into logical sections."""
        sections = []

        # Split by headings or large separators
        parts = re.split(r'\n(#{1,3}\s+.+)\n', content)

        if len(parts) > 1:
            for i in range(1, len(parts), 2):
                title = parts[i].strip()
                content_part = parts[i + 1] if i + 1 < len(parts) else ""
                sections.append({"title": title, "content": content_part})
        else:
            # Single section
            sections.append({"title": "main", "content": content})

        return sections

    def estimate_tokens(self, content: str) -> int:
        """Estimate token count for content."""
        return TokenEstimator.estimate(content)

    def chunk(self, content: str, chunk_size: Optional[int] = None) -> List[str]:
        """Split content into manageable chunks."""
        chunk_size = chunk_size or self.config.chunk_size
        overlap = self.config.overlap

        words = content.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)

        return chunks

    def analyze(self, content: str) -> Dict[str, Any]:
        """Analyze content for optimization potential."""
        tokens = self.estimate_tokens(content)
        sections = self._split_sections(content)

        # Calculate redundancy metrics
        words = content.lower().split()
        unique_words = set(words)
        redundancy = 1 - (len(unique_words) / len(words)) if words else 0

        # Estimate potential savings
        test_result = self._semantic_compressor.compress(content, 0.6)

        return {
            "token_count": tokens,
            "sections": len(sections),
            "word_count": len(words),
            "unique_words": len(unique_words),
            "redundancy_ratio": round(redundancy, 3),
            "potential_savings": test_result.compression_ratio,
            "estimated_savings_tokens": test_result.original_tokens - test_result.compressed_tokens,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get optimizer statistics."""
        return {
            "strategy": self.config.strategy,
            "compression_ratio": self.config.compression_ratio,
            "max_tokens": self.config.max_tokens,
            "enabled": self.config.enabled,
        }