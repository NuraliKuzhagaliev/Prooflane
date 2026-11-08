"""Use installed Hub helpers without writing outside the active project."""
import importlib.util
from pathlib import Path

root = Path(__file__).resolve().parents[1]
helper = Path("D:/projects/CodexEngineeringHub/scripts/hub.py")
spec = importlib.util.spec_from_file_location("installed_engineering_hub", helper)
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)
for mode, objective in {
    "hackathon": "Verify Vultr Agent Rush requirements and prepare a bounded submission",
    "research": "Compare evidence-linked analysis alternatives using primary sources",
    "innovate": "Rank twelve opportunities and select implementable differentiators",
    "build": "Implement and test Prooflane local CSV-to-receipt workflow",
    "audit": "Independently audit execution, verification and provenance boundaries",
}.items():
    packet, output = hub.start_run(mode, root, objective, root=root)
    print(output)
