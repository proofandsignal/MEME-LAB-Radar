# BUILD-002 — USDG Pinned Metadata Review 005

Observed at: `2026-10-19T11:04:29.152213+00:00`
GitHub run: https://github.com/proofandsignal/MEME-LAB-Radar/actions/runs/39241963616
Evidence artifact ID: `12181592376`.

## Actual onchain evidence

- Token: `0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168`
- Chain: Robinhood Chain, `4663` (eth_chainId read PASS).
- Block: `0x58471e1`, hash `0x4cfe0409d42de901f5822945bf3df48f58dc72ae1d77157c9e68e4e5495e4bf5`.
- Seven read steps were successful; block hash checked a second time.
- `symbol()` = `USDG`.
- `decimals()` = `6`.
- `totalSupply()` raw = `697711769550524` (6 decimal token units).
- Outcome: `ONCHAIN_METADATA_MATCH`.

## Trust boundaries

- These are single-RPC, height-pinned observations, not independent infrastructure agreement.
- Symbol/decimals/totalSupply and deployed bytecode do **not** establish collateral backing, issuer audit, price, reserves, proof of solvency or pool liquidity.
- First-party Global Dollar Network confirms USDG is available on Robinhood Chain, but further source-backed contract attestation and implementation provenance remains open: https://globaldollar.com/newsroom/usdg-is-now-available-on-robinhood-chain-as-the-lending-asset-in-robinhood-s-new-earn-product
- Factory address `0x5481864ddd46a2d798df0925c23b7846e776e5e3` lacks verified official protocol deployment identity.
- Durable artifact retention and independent block/provider checks still outstanding.

**Gate: USDG ONCHAIN METADATA MATCH / FACTORY PROVENANCE PENDING / LIQUIDITY LOCKED / BUILD-002 NOT ACCEPTED / PR #3 DRAFT / MERGE LOCKED.**
