"""Schrijft custom.txt: de JSON-instellingen als base64, zoals rdgen dat doet.

Gebruik: python custom_txt.py custom-klant.json > pakket/custom.txt
"""

import base64
import json
import sys

with open(sys.argv[1], encoding="utf-8") as f:
    instellingen = json.load(f)
# ensure_ascii: tekens als de middenpunt in "BoonstraWorks · Steven" worden ·.
sys.stdout.write(base64.b64encode(json.dumps(instellingen).encode("ascii")).decode("ascii"))
