# BUILD-002 — Live Evidence Review 001

**Observed:** 2026-10-16 04:11:13 UTC
**GitHub Actions:** https://github.com/proofandsignal/MEME-LAB-Radar/actions/runs/38849297815
**Artifact ID:** 12023963600
**Endpoint:** https://api.dexscreener.com/latest/dex/search?q=NVDA
**Artifact SHA-256 (dexscreener.json):** `0729157e3685db692cd831a2218535810e8b97481964a33a98d1b098b273f8b5`

## Reproducible summary

- Returned search results: **30**; normalized: **30**; rejected by structural parser: **0**.
- SQLite ingest in run: **30 inserted, 0 rejected**.
- Chain distribution: robinhood **28**, solana **1**, avalanche **1**.
- Base symbol NVDA in **all 30** results, **not** independently verified stock-token identity.
- **3/30** provider results lack `pairCreatedAt`.
- Raw JSON, SQLite, result and manifest were all retained in GitHub Actions artifact.

## Critical caveats

1. Ticker/name matches cannot establish issuer, underlying equity rights, legitimate PAIR pool, or trusted token contract.
2. This is a **single search response**, not population sampling or an exhaustive launch feed.
3. `observed_at` in the normalized records is collector wall-clock time. Source `pairCreatedAt` must be independently vetted and kept distinct from verified on-chain creation time.
4. Upstream quote/price/liquidity values are third-party observations: data provenance is verified to provider, **not** independently cross-verified on-chain.
5. Artifact retention is 14 days. For durable replay, independent archival/restore is still required.
6. DEX search input NVDA may select unrelated assets. Stock mapping is intentionally null/UNVERIFIED in collector records.

## Gate outcome

**LIVE PROVIDER FETCH PASS / NORMALIZATION PASS / EVIDENCE CAPTURE PASS / ASSET VERIFICATION PENDING.**

## Next tasks

- Independent chain RPC validation for **specific selected pools**, pair contracts, and stock-issuer allowlist sourced from first-party issuer documentation.
- Distinguish `provider_observed_at`, `fetched_at`, `pairCreatedAt` and on-chain verified creation block.
- Verify source `chainId` mapping, API freshness, pool identity, and duplicates.
- Add failure/retry/rate-limit tests and an immutable durable archive restore test.
- Only after verification: scheduled observation series and survival/quality measurements.

No merge, deployment, or other repository changes. `DATA FIRST → REVENUE SECOND → TOKEN OPTIONAL`.
