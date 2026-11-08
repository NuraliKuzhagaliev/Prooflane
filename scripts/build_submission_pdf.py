"""Assemble the validated Artifact Tool renders into the submission PDF.

The editable source remains prooflane-deck.pptx. PDF pages use the rendered slide
images because the bundled Artifact Tool PDF exporter currently cannot resolve
its internal standard-fonts alias on this Windows runtime.
"""
import argparse
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output-dir", type=Path, default=ROOT / "submission" / "agent-rush")
output_dir = parser.parse_args().output_dir
OUTPUT = output_dir / "prooflane-deck.pdf"
RENDERS = output_dir / ".build"
PAGE_SIZE = (1200, 675)

pdf = canvas.Canvas(str(OUTPUT), pagesize=PAGE_SIZE, pageCompression=1)
pdf.setTitle("Prooflane - Evidence for disputed supplier prices")
pdf.setAuthor("Prooflane project")
pdf.setSubject("Vultr Agent Rush. Invoice reconciliation, Docker execution and offline case verification on synthetic data.")
for number in range(1, 7):
    source = RENDERS / f"slide-{number}.png"
    if not source.is_file():
        raise FileNotFoundError(source)
    pdf.drawImage(ImageReader(str(source)), 0, 0, *PAGE_SIZE)
    pdf.showPage()
pdf.save()
reader = PdfReader(str(OUTPUT))
assert len(reader.pages) == 6
assert all(tuple(float(v) for v in p.mediabox[2:]) == PAGE_SIZE for p in reader.pages)
print(f"PDF: {OUTPUT}; pages={len(reader.pages)}; bytes={OUTPUT.stat().st_size}")
