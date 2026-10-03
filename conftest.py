import sys
from pathlib import Path

# Force the project root directory into sys.path
root_dir = Path(__file__).parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))