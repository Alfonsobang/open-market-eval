"""Minimal audit adapter used only to verify the JSON-over-stdio protocol."""

import json
import sys


json.load(sys.stdin)
json.dump({"findings": []}, sys.stdout)
