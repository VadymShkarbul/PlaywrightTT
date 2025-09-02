# PlaywrightTT

Tiny Playwright script that opens an Amazon seller info page, finds the storefront, grabs the first product, and appends country/zip/seller/product/title/price to out.csv.

Setup (local)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
playwright install chromium
```

Run (local)
```bash
python src/main.py --country uk --seller "https://www.amazon.co.uk/sp?seller=A01609602H16VOVDUKH19"
# Output: appends a row to out.csv in current working directory
```

Docker
- The app writes CSV to the path specified by the CSV_FILE env var (default: /data/out.csv).
- Bind-mount a host directory to /data to persist out.csv outside the container.

Build image
```bash
docker build -t playwright-tt .
```

Run with persisted output
```bash
# Create output directory on host
mkdir -p ./out
# Run container, mounting host ./out to /data inside container
# The app will write to /data/out.csv (host: ./out/out.csv)
docker run --rm \
  -v "$(pwd)/out:/data" \
  -e CSV_FILE=/data/out.csv \
  playwright-tt \
  python src/main.py --country uk --seller "https://www.amazon.co.uk/sp?seller=A01609602H16VOVDUKH19"
```

Custom output file path
```bash
docker run --rm -v "$(pwd)/out:/data" -e CSV_FILE=/data/custom.csv playwright-tt
```