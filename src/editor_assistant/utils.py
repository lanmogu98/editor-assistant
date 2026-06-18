"""
Utility functions for Editor Assistant.
"""

from .config.constants import CHAR_TOKEN_RATIO_EN, CHAR_TOKEN_RATIO_ZH


def estimate_tokens(text: str) -> int:
    """
    Estimate token count based on text content, adjusting for language.
    
    Uses different ratios for Chinese vs English text based on character analysis.
    - English/ASCII: ~3.5 characters per token
    - Chinese/CJK: ~1.5 characters per token (each Chinese char ≈ 2-3 tokens)
    
    Args:
        text: The text to estimate token count for.
        
    Returns:
        Estimated number of tokens.
    """
    if not text:
        return 0
    
    # Count Chinese characters (CJK Unified Ideographs range)
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    total_chars = len(text)
    
    if total_chars == 0:
        return 0
    
    # Calculate Chinese ratio
    chinese_ratio = chinese_chars / total_chars
    
    # Blend ratios based on content composition
    # If >20% Chinese, start using Chinese ratio proportionally
    if chinese_ratio > 0.2:
        blended_ratio = (
            chinese_ratio * CHAR_TOKEN_RATIO_ZH + 
            (1 - chinese_ratio) * CHAR_TOKEN_RATIO_EN
        )
    else:
        blended_ratio = CHAR_TOKEN_RATIO_EN
    
    return int(total_chars / blended_ratio)

