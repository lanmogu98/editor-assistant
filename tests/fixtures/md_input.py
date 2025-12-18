"""
Real research paper data loading utilities.

Provides sample MDArticle objects for testing from local files.
"""

from pathlib import Path
from typing import List
import pytest
from editor_assistant.data_models import InputType, MDArticle

# Sample data directory
SAMPLE_DATA_DIR = Path(__file__).parent / "sample_data"

# File paths
SHANNON_PAPER_PATH = SAMPLE_DATA_DIR / "A Mathematical Theory of Communication.md"
WEAVER_REPORT_PATH = SAMPLE_DATA_DIR / "Weaver_Warren_1949_The_Mathematics_of_Communication.md"


def load_sample_content(path: Path, fallback: str = "") -> str:
    """Load content from file with fallback."""
    if path.exists():
        return path.read_text(encoding='utf-8')
    return fallback


@pytest.fixture
def shannon_paper() -> MDArticle:
    """
    Load Claude Shannon's "Mathematical Theory of Communication" paper.
    
    Returns:
        MDArticle with paper content
    """
    content = load_sample_content(
        SHANNON_PAPER_PATH,
        fallback=_SHANNON_FALLBACK
    )
    return MDArticle(
        type=InputType.PAPER,
        content=content,
        title="A Mathematical Theory of Communication",
        authors="Claude E. Shannon",
        source_path=str(SHANNON_PAPER_PATH)
    )


@pytest.fixture
def weaver_report() -> MDArticle:
    """
    Load Warren Weaver's communication theory essay.
    
    Returns:
        MDArticle with report content
    """
    content = load_sample_content(
        WEAVER_REPORT_PATH,
        fallback=_WEAVER_FALLBACK
    )
    return MDArticle(
        type=InputType.NEWS,  # Treat as news/essay for testing
        content=content,
        title="The Mathematics of Communication",
        authors="Warren Weaver",
        source_path=str(WEAVER_REPORT_PATH)
    )


@pytest.fixture
def multi_source_articles(shannon_paper, weaver_report) -> List[MDArticle]:
    """
    Provide multiple articles for multi-source testing.
    
    Returns:
        List of MDArticle objects
    """
    return [shannon_paper, weaver_report]


# Fallback content when files are not available
_SHANNON_FALLBACK = """# A Mathematical Theory of Communication

## Abstract
This paper develops the mathematical foundations of information theory, 
introducing concepts of entropy, channel capacity, and optimal coding schemes.

## Introduction
The fundamental problem of communication is that of reproducing at one point 
either exactly or approximately a message selected at another point.

## The Discrete Noiseless Channel
We consider first the case of a channel without noise.

## The Discrete Channel with Noise
We now introduce the effects of noise in the channel.

## Conclusion
This work establishes a mathematical theory of communication that provides 
optimal bounds on data transmission and compression.
"""

_WEAVER_FALLBACK = """# The Mathematics of Communication

## Introduction
The word communication will be used here in a very broad sense to include 
all of the procedures by which one mind may affect another.

## Levels of Communication Problems
In communication there seem to be problems at three levels:
1. Technical - How accurately can symbols be transmitted?
2. Semantic - How precisely do transmitted symbols convey meaning?
3. Effectiveness - How effectively does received meaning affect conduct?

## Conclusion
This analysis provides a framework for understanding communication systems.
"""
