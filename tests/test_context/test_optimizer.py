import pytest
from omniforge.context.optimizer import ContextOptimizer


def test_optimizer_creation():
    """Test optimizer initialization."""
    optimizer = ContextOptimizer()
    assert optimizer is not None


def test_semantic_compression():
    """Test semantic compression removes redundancy."""
    optimizer = ContextOptimizer()
    
    text = "This is a text that has a lot of redundant words and phrases. This text contains many words that are not necessary."
    compressed = optimizer.compress(text, strategy="semantic")
    
    # Should reduce length while preserving meaning
    assert len(compressed) < len(text)
    assert "text" in compressed.lower()


def test_token_compression():
    """Test token-based compression."""
    optimizer = ContextOptimizer()
    
    text = "The quick brown fox jumps over the lazy dog. This is a standard test sentence."
    compressed = optimizer.compress(text, strategy="token")
    
    assert isinstance(compressed, str)
    assert len(compressed) > 0


def test_hybrid_compression():
    """Test hybrid compression strategy."""
    optimizer = ContextOptimizer()
    
    long_text = "This is a comprehensive test of the context optimization system. " * 5
    compressed = optimizer.compress(long_text, strategy="hybrid")
    
    assert len(compressed) < len(long_text)
    assert "optimization" in compressed.lower()


def test_optimization_preserves_key_info():
    """Test that compression preserves key information."""
    optimizer = ContextOptimizer()
    
    text = "The project deadline is December 25th. We need to submit report number 12345 to email test@example.com."
    compressed = optimizer.compress(text)
    
    # Key information should be preserved
    assert "December 25th" in compressed
    assert "12345" in compressed
    assert "test@example.com" in compressed


def test_token_estimation():
    """Test token counting functionality."""
    optimizer = ContextOptimizer()
    
    text = "Hello world"
    token_count = optimizer.estimate_tokens(text)
    
    # "Hello world" should be approximately 2-3 tokens
    assert token_count >= 2
    assert token_count <= 5


def test_batch_optimization():
    """Test optimizing multiple texts."""
    optimizer = ContextOptimizer()
    
    texts = [
        "First piece of text to compress",
        "Second piece of text to optimize",
        "Third piece with more content to reduce",
    ]
    
    results = optimizer.batch_compress(texts)
    assert len(results) == 3
    
    for result in results:
        assert isinstance(result, str)
        assert len(result) > 0


def test_compression_ratio():
    """Test compression ratio tracking."""
    optimizer = ContextOptimizer()
    
    text = "This is a long text that needs to be compressed. " * 10
    compressed = optimizer.compress(text)
    
    # Get compression ratio
    ratio = optimizer.get_compression_ratio(text, compressed)
    assert 0 < ratio < 1  # Should achieve some compression


def test_optimizer_config():
    """Test optimizer with different configurations."""
    optimizer = ContextOptimizer()
    
    # Test with custom threshold
    text = "Short text"
    compressed = optimizer.compress(text, min_length=100)
    
    # Should return original if below threshold
    assert compressed == text


def test_large_text_handling():
    """Test optimizer handles large texts."""
    optimizer = ContextOptimizer()
    
    # Generate a large text
    large_text = "Paragraph " + " ".join(["word"] * 500)
    
    compressed = optimizer.compress(large_text)
    
    # Should handle large text without errors
    assert isinstance(compressed, str)
    assert len(compressed) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])