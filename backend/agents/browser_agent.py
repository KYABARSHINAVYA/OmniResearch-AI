from urllib.parse import urlparse


def browse_url(url, selector=None, max_chars=6000):
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return {"url": url, "title": "", "text": "", "error": "Only http and https URLs are supported."}

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        return {
            "url": url,
            "title": "",
            "text": "",
            "error": f"Playwright is not installed or browsers are missing: {exc}",
        }

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            target = page.locator(selector).first() if selector else page.locator("body")
            text = target.inner_text(timeout=5000)
            title = page.title()
            browser.close()
            return {"url": url, "title": title, "text": text[:max_chars], "error": ""}
    except Exception as exc:
        return {"url": url, "title": "", "text": "", "error": str(exc)}
