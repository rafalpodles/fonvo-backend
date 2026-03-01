"""Thin wrappers around OpenAI API for reuse across routers.

Currently the router calls OpenAI directly. This module exists as a hook
for future shared logic (rate limiting, usage tracking, retries).
"""
