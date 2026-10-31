"""Registry of the six variants: "<sdk>.<style>" -> answer(question) function."""

import importlib

SDKS = ["anthropic_sdk", "agent_sdk"]
STYLES = ["rag", "agentic_rag", "graphrag"]
VARIANTS = [f"{sdk}.{style}" for sdk in SDKS for style in STYLES]


def get_answer_fn(variant: str):
    """Import lazily so running one variant doesn't load the other SDK."""
    if variant not in VARIANTS:
        raise ValueError(f"Unknown variant {variant!r}. Choose from: {', '.join(VARIANTS)}")
    return importlib.import_module(f"graphrag_cmp.{variant}").answer
