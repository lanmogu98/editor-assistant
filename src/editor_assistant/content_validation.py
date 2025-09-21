"""
Two-stage content validation system.

Educational Note: This implements a clean, practical validation approach:
1. First check: Is this a blocked publisher? → Hard stop
2. Second check: Is content too short? → Show content, let user decide

This design is much more user-friendly than complex multi-level validation.
"""

MIN_CHARS_WARNING_THRESHOLD = 1000

# TODO: implement the core logic here