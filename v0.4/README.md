# MEME LAB Meta Radar v0.4 — Foundation

**Status:** initial scaffold / unverified live integrations. Python 3.11+, stdlib-only.
This is a standalone prototype, **not** evidence that the legacy v0.3 application has been migrated.

## What is implemented

- Append-only SQLite observation records with canonical raw JSON + SHA256, de-duplicated by source/record/time/hash.
- Explicit source provenance, collector run audit and reject-on-invalid fields.
- Candidate stock token registry: entries enter REVIEW, never auto-VERIFIED.
- Snapshot-based pool heatmap (latest per pool, prevents snapshot double-counting).
- 5m/15m/30m/1h/6h/24h/7d survival observation states with PENDING and UNKNOWN distinct from confirmed data.
- CLI and offline unit tests.

## Run locally

\`\`\`bash
cd v0.4
python radar.py --db radar.sqlite3 init
python radar.py --db radar.sqlite3 ingest --file examples/observations.json --source fixture
python radar.py --db radar.sqlite3 heatmap
python radar.py --db radar.sqlite3 survival --chain testnet --pool 0xPOOL
python -m unittest -v test_radar
\`\`\`

**No external API credentials required for the fixture.** This build does not yet claim Robinhood/PAIR/DEX live coverage.

## Data contracts

Observation array JSON fields:
\`observed_at\` (ISO 8601 + timezone), \`chain\`, \`pool_address\`,
\`base_token\`, \`quote_token\`, \`source\`, \`source_record_id\`.
Optional: \`stock_symbol\`, \`price_usd\`, \`liquidity_usd\`,
\`volume_24h_usd\`, \`txns_24h\`.

Do not treat first_seen as a verified creation block, volume as buy pressure,
or positive liquidity as proof of safety. A missing horizon snapshot is UNKNOWN.
Liquidity and volume can be spoofed. A registry claim is not a verified tokenized stock.

## Roadmap

1. **v0.4.1**: inspect original v0.3 distribution, reconcile schema and UI.
2. **v0.4.2**: chain/provider adapters with rate limits, retries, error logging and live upstream smoke tests.
3. **v0.4.3**: contract/issuer allowlist with independently evidenced mappings; pools and multipool legs.
4. **v0.4.4**: backfilled block times, contract creation dates, rugged/censored outcome labels.
5. **v0.5**: narrative-event annotations, cross-pair heatmap, signal audit, Paper 20 benchmarks.

### Launch Gate

No executable trading, private keys, token launch, or creator-revenue claims.
Research-only until live-data quality, contract verification, backtesting,
jurisdictional review and transparent risk disclosures pass.
