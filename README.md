# PlaywrightTT

Tiny Playwright script that opens an Amazon seller info page, finds the storefront, grabs the first product, and appends country/zip/seller/product/title/price to out.csv.

Setup
```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt
    playwright install chromium
```

Run
```bash
  python src/main.py --country uk --seller "https://www.amazon.co.uk/sp?seller=A01609602H16VOVDUKH19"
  # Output: appends a row to src/out.csv        
```