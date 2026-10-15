# BUILD-002 — Live Verification (Draft / Not Accepted)

## Goal

Capture **real provider observations**, with reproducible response evidence and
explicit uncertainty. **Observations from DEX Screener are not proof of tokenized
stocks, original underlying stock rights, contract issuer, or PAIR membership.**

## Implemented in first increment

- DEX Screener read-only exploratory search adapter.
- Strict normalization; errors and missing fields are not fabricated.
- Raw upstream response plus request URL and fetched-at diagnostics saved to JSON.
- Append-only SQLite observation ingest via the existing v0.4 collector.
- `stock_symbol` explicitly unset pending contract+issuer verification.
- Offline adapter tests.

## Usage (real API required)

```sh
cd v0.4
python live_adapter.py --db research.sqlite3 --query NVDA --evidence-out evidence-nvda.json
python radar.py --db research.sqlite3 export-ui --out candidate-ui.json
```

The query is broad and may include unrelated assets; do **not** publish its output
as verified stock-paired tokens. API may be unavailable, rate-limited, or different
from documentation. A search query isn't a complete discovery collector. No live
smoke is claimed unless a timestamped evidence artifact is reviewed.

## Outstanding acceptance gates

- [ ] CI PASS for BUILD-002 latest head and integration testing.
- [ ] Live upstream smoke with stored raw evidence and repeatability.
- [ ] Verified chain / token contract / issuer/underlying type with independent sources.
- [ ] Genuine PAIR pool mapping, multipool legs and verified launch timestamps.
- [ ] Rate-limit/backoff and scheduler failure/recovery tests.
- [ ] Data freshness and completeness measurement over a sustained observation window.
- [ ] Human review before accepting, merging or publishing.

No real launch, trades, or production deployment.
