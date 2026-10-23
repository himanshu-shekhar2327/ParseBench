
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

OUTPUT_DIR = Path("documents/digital_pdf")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

API_URL = "https://export.arxiv.org/api/query"
params = {
    "search_query": "cat:cs.CL",
    "start": 0,
    "max_results": 25,
    "sortBy": "submittedDate",
    "sortOrder": "descending",
}

url = API_URL + "?" + urllib.parse.urlencode(params)
request = urllib.request.Request(
    url,
    headers={"User-Agent": "Learn-Parser-Benchmark/1.0"},
)

print("Fetching public paper metadata from arXiv...")

with urllib.request.urlopen(request, timeout=60) as response:
    root = ET.fromstring(response.read())

namespace = {"atom": "http://www.w3.org/2005/Atom"}
entries = root.findall("atom:entry", namespace)

print(f"Found {len(entries)} papers.")

for index, entry in enumerate(entries, start=1):
    paper_url = entry.findtext("atom:id", namespaces=namespace)
    if not paper_url:
        continue

    paper_id = paper_url.rstrip("/").split("/")[-1].split("v")[0]
    destination = OUTPUT_DIR / f"{paper_id.replace('/', '_')}.pdf"

    if destination.exists() and destination.stat().st_size > 0:
        print(f"[{index}/{len(entries)}] Already downloaded: {paper_id}")
        continue

    pdf_url = f"https://arxiv.org/pdf/{paper_id}"
    request = urllib.request.Request(
        pdf_url,
        headers={"User-Agent": "Learn-Parser-Benchmark/1.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            content = response.read()

        if not content.startswith(b"%PDF-"):
            raise ValueError("Downloaded response is not a PDF.")

        destination.write_bytes(content)
        print(
            f"[{index}/{len(entries)}] Downloaded {paper_id} "
            f"({len(content) / 1024:.1f} KB)"
        )

    except Exception as exc:
        print(f"[{index}/{len(entries)}] FAILED {paper_id}: {exc}")

    time.sleep(1)

print(f"\nDataset location: {OUTPUT_DIR.resolve()}")
print(f"PDF files downloaded: {len(list(OUTPUT_DIR.glob('*.pdf')))}")
