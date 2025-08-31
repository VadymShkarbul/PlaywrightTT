import argparse
import csv
import os
import logging
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright, Page, ViewportSize

# Configuration
SELLER_URL_DEFAULT = "https://www.amazon.co.uk/sp?seller=A01609602H16VOVDUKH19"
ZIP_CODES = {"us": "10001", "uk": "SW1A 1AA", "es": "28001"}
CSV_FILE = "out.csv"
CSV_HEADER = ["country", "zip", "seller_url", "product_url", "title", "price"]

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s") # noqa
logger = logging.getLogger(__name__)


def init_csv() -> None:
    """Create a CSV file with headers"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(CSV_HEADER)


def save_row(row: list[str]) -> None:
    """Append a row to the CSV"""
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)


def set_location(page: Page, zip_code: str) -> bool:
    """Set location on Amazon"""
    try:
        # Click the location control
        page.click("#nav-global-location-popover-link", timeout=1000)
        # Enter postal code
        page.fill("#GLUXZipUpdateInput", zip_code, timeout=1000)
        # Click Apply
        try:
            page.click("button:has-text('Apply')", timeout=1000)
        except:
            page.keyboard.press("Enter")
        # Dismiss confirmation
        try:
            page.click("button:has-text('Continue')", timeout=1000)
        except:
            page.keyboard.press("Enter")

        page.wait_for_timeout(1000)
        logger.info("Location set: %s", zip_code)
        return True
    except Exception as e:
        logger.error("Failed to set location: %s", e)
        return False


def get_storefront_url(page: Page) -> str:
    """Find the storefront URL from the seller page"""
    try:
        element = page.query_selector("#seller-info-storefront-link > span > a")  # "#seller-info-storefront-link a"
        if element:
            href = element.get_attribute("href")
            return urljoin(page.url, href) if href else ""
    except:
        pass
    return ""


def get_first_product_url(page: Page) -> str:
    """Find the first product URL in the storefront"""
    try:
        # Look for the first product with an ASIN
        products = page.query_selector_all("div[data-asin]")
        for product in products:
            asin = product.get_attribute("data-asin")
            if asin and len(asin) == 10:
                return f"/dp/{asin}"
    except:
        pass
    return ""


def get_product_info(page: Page):
    """Get product title and price"""
    title = ""
    price = ""

    try:
        title_element = page.query_selector("#productTitle")
        if title_element:
            title = title_element.text_content().strip()
    except:
        pass

    price_selectors = [
        "#corePrice_feature_div span.a-offscreen",
        "span.a-price span.a-offscreen",
        "#priceblock_ourprice"
    ]

    for selector in price_selectors:
        try:
            price_element = page.query_selector(selector)
            if price_element:
                price = price_element.text_content().strip()
                break
        except:
            continue

    return title, price


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", choices=["us", "uk", "es"], default="uk")
    parser.add_argument("--seller", default=SELLER_URL_DEFAULT)
    args = parser.parse_args()

    country = args.country
    zip_code = ZIP_CODES[country]
    seller_url = args.seller

    logger.info("Country: %s", country)
    logger.info("ZIP: %s", zip_code)
    logger.info("Seller URL: %s", seller_url)

    init_csv()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        )
        viewport = {"width": 1366, "height": 768}
        context = browser.new_context(
            user_agent=user_agent,
            viewport=ViewportSize(**viewport)
        )
        page: Page = context.new_page()

        try:
            logger.info("1. Opening seller page...")
            page.goto(seller_url)
            page.wait_for_load_state("domcontentloaded")

            logger.info("2. Setting location...")
            set_location(page, zip_code)

            logger.info("3. Finding storefront...")
            storefront_url = get_storefront_url(page)
            if not storefront_url:
                logger.warning("Storefront not found")
                return

            logger.info("4. Navigating to storefront: %s", storefront_url)
            page.goto(storefront_url)
            page.wait_for_load_state("domcontentloaded")

            logger.info("5. Searching for the first product...")
            product_href = get_first_product_url(page)
            if not product_href:
                logger.warning("Product not found")
                save_row([country, zip_code, seller_url, "", "", ""])
                return

            product_url = urljoin(page.url, product_href)

            logger.info("6. Navigating to product: %s", product_url)
            page.goto(product_url)
            page.wait_for_load_state("domcontentloaded")

            logger.info("7. Getting product information...")
            title, price = get_product_info(page)

            save_row([country, zip_code, seller_url, product_url, title, price])
            logger.info("Saved: %s... | %s", title[:50], price)

        except Exception as e:
            logger.exception("Error: %s", e)
        finally:
            browser.close()


if __name__ == "__main__":
    main()