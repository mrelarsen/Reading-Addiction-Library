import sys
from pathlib import Path
paths = [
    "\\\\..",
    "\\\\..\\\\..",
    "\\\\..\\\\..\\\\..",
    "\\\\..\\\\..\\\\..\\\\libraries",
]
for path in paths:
    sys.path.append(str(Path(sys.path[0] + path).resolve()));
