"""
Two-stage content validation system.

Educational Note: This implements a clean, practical validation approach:
1. First check: Is this a blocked publisher? → Hard stop
2. Second check: Is content too short? → Show content, let user decide

This design is much more user-friendly than complex multi-level validation.
"""

from .config.constants import MIN_CHARS_WARNING_THRESHOLD

# TODO: implement the core logic here