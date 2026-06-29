"""Compatibility shim for the extracted LLM client."""

import sys

import llm_exec_core.client as _client

sys.modules[__name__] = _client
