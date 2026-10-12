"""Real browser smoke: file import + rendered table + unverified labels.
Run from repository root with: python v0.4/browser_smoke.py
Requires: pip install playwright; Chrome/Chromium browser installed.
"""
from pathlib import Path
import json
import os
import tempfile
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parent.parent
sample = {
    "schema_version": "0.4.0",
    "data_gate": "UNVERIFIED",
    "generated_at": "2026-10-12T06:00:00Z",
    "observations": [{
        "observed_at": "2026-10-12T06:00:00Z",
        "chain": "testnet",
        "pool_address": "pool-browser-test",
        "base_token": "meme-fixture",
        "quote_token": "stock-fixture",
        "stock_symbol": "NVDA",
        "source": "fixture",
        "source_record_id": "browser-test",
        "liquidity_usd": 1234,
        "volume_24h_usd": 456
    }]
}
with tempfile.TemporaryDirectory() as tmp:
    valid = Path(tmp) / "valid.json"
    invalid = Path(tmp) / "invalid.json"
    valid.write_text(json.dumps(sample), encoding="utf-8")
    invalid.write_text(json.dumps({**sample, "data_gate": "VERIFIED"}), encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True, args=["--no-sandbox"])
        try:
            page = browser.new_page()
            page.goto((root / "index.html").as_uri())
            assert page.title() == "MEME LAB Meta Radar v0.3"
            with page.expect_file_chooser() as chooser:
                page.get_by_text("IMPORT COLLECTOR JSON").click()
            chooser.value.set_files(str(valid))
            page.locator("#rows tr").first.wait_for()
            assert page.locator("#mTracked").inner_text() == "1"
            assert page.locator("#modeBadge").inner_text() == "FILE / UNVERIFIED"
            row = page.locator("#rows tr").first
            assert row.locator("td").nth(5).inner_text() == "VERIFY"
            assert row.locator("td").nth(3).inner_text() == "UNVERIFIED"
            assert row.locator("td").nth(11).inner_text() == "UNKNOWN"
            row.click()
            assert "NOT independently verified" in page.locator("#dSub").inner_text()
            page.locator("#close").click()
            with page.expect_file_chooser() as chooser:
                page.get_by_text("IMPORT COLLECTOR JSON").click()
            chooser.value.set_files(str(invalid))
            page.wait_for_function('document.querySelector("#message").textContent.includes("INVALID / VERIFY")')
            assert page.locator("#mTracked").inner_text() == "1"
            page.locator("#search").fill("missing")
            assert page.locator("#rows tr").count() == 0
            print("REAL BROWSER ACCEPTANCE PASS — import/render/labels/reject/search")
        finally:
            browser.close()
