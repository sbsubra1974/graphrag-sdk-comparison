"""Regenerate .mcp.json from config/mcp_servers.yaml."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from graphrag_cmp.mcp_config import claude_code_json

out = Path(__file__).resolve().parents[1] / ".mcp.json"
out.write_text(json.dumps(claude_code_json(), indent=2) + "\n")
print(f"Wrote {out}")
