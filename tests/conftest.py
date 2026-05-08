import sys
from pathlib import Path

# Ensure src/ is on the path so `import eBay_Crawl` works without `pip install .`
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
