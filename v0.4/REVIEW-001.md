# BUILD-001 Technical Review — 2026-10-12

## Summary

**Status: FIXES IN REVIEW / ACCEPTANCE BLOCKED.** PR #1 must remain Draft until review issues are addressed and CI green on latest head.

## Compatibility findings — BLOCKER

- `main/index.html` references `styles.css` and `app.js`, which are absent from the main repository tree.
- The v0.3 README points to `v0.3/README.md`, but no v0.3 directory is present in main.
- The v0.4 Python SQLite collector is a standalone CLI and has **no verified browser UI adapter**.
- Do not imply an integrated working v0.3 UI until the missing assets are recovered or a replacement is reviewed.

## Data integrity findings

1. **FIXED in current branch:** ingest with an explicit provider source rejects observations that declare a different source. Default manual ingestion still retains reporter-provided provenance without verification.
2. **FIXED in current branch:** past horizons without nearby observations report UNKNOWN rather than indefinitely PENDING. A horizon without evidence never counts as survival success.
3. **FIXED in current branch:** heatmap labels stock symbol mappings as UNVERIFIED; aggregation is exploratory, not proof of stock-token exposure.
4. **KNOWN LIMITATION:** snapshots carry first-seen times, not verified on-chain launch times. Horizon observations are proximity-based and are not a lifecycle/survival ground truth.
5. **KNOWN LIMITATION:** no live chain-backed contract/issuer verification; no RPC block anchoring, holder verification, real provider fixtures or independent data source agreement.
6. **KNOWN LIMITATION:** SQLite append-only behavior is a software convention (INSERT-only paths), not DB-level immutable audit protection.

## Integration gate

- [ ] Recover or replace missing browser assets and test end-to-end UI workflow.
- [ ] Confirm actual v0.3 schema and migration strategy; do not claim backward compatibility before evidence.
- [ ] Run offline unit tests and a reproducible CLI demo.
- [ ] Confirm PR head CI PASS after review patches.
- [ ] Add observed live provenance with verified chain/contract mapping only in BUILD-002 after BUILD-001 acceptance.

## Acceptance decision

**NOT ACCEPTED** until compatibility, baseline reproducibility, and the three review areas have documented, reproducible evidence. No merge. No trading or token launch.


## Final technical verification — 2026-10-14

Latest reviewed PR head before this documentation-only update: `dfe3b6d40a295ac33531e37409d83126afbdc5d3`.

- [x] Replacement `app.js` and `styles.css` added on build branch; this is **not** restoration of the original v0.3 implementation.
- [x] Unit and JSON contract tests pass.
- [x] SQLite → JSON smoke passes.
- [x] DOM validation and real headless Chrome import/render test pass.
- [x] PR-head GitHub Actions push and pull_request runs both conclude success.
- [ ] v0.3 schema backward compatibility is **not demonstrated**. Scope: standalone v0.4 replacement browser with manual JSON import, not a migration of local v0.3 IndexedDB data.
- [ ] Human final acceptance and merge approval remain pending.

### Acceptance recommendation

**Technical acceptance candidate, with documented scope restrictions.** The initial compatibility blocker is resolved for the *new v0.4 standalone export/import UI path*. It is not evidence that a complete v0.3 product or its historical user data can be migrated. No verified live-market claims are permitted. Demo/testnet fixture values are not live signals.

**Gate:** Human approval is required before marking BUILD-001 ACCEPTED or merging PR #1. BUILD-002 Live Verification is still blocked until acceptance and controlled merge.
