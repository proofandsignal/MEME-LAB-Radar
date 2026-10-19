# BUILD-002 — Pool RPC Review 002 (Transient HTTP 403 / Retry)

Date: 2026-10-19

## Evidence

- Initial failed observation: [workflow 39196092996](https://github.com/proofandsignal/MEME-LAB-Radar/actions/runs/39196092996) — `VERIFY / HTTP Error 403`.
- Diagnostic retry: [workflow 39196767913](https://github.com/proofandsignal/MEME-LAB-Radar/actions/runs/39196767913); artifact `build-002-pool-rpc-evidence`, ID `12162118057`.
- Observation timestamp: `2026-10-19T03:53:06.174890+00:00`.
- Same pool: `0x0092f73B6821098F66eEa758cf7eeB0F834C2303`.
- Provider base: `0xd0601CE157Db5bdC3162BbaC2a2C8aF5320D9EEC`.
- Provider quote: `0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168`.
- RPC outcome: **V2_LEGS_MATCH**. Read-only chain ID, pool bytecode and `token0/token1` calls returned successfully in the retry.
- Recovered onchain legs (unordered): `0x5fc5360d0400a0fd4f2af552add042d716f1d168`, `0xd0601ce157db5bdc3162bbac2a2c8af5320d9eec`.

## Interpretation

- The initial 403 was **not reproduced** in the diagnostic repeat. Cause remains **UNKNOWN**; there is no basis to claim rate-limit, policy or outage.
- Evidence indicates token-leg consistency with provider data at the time of this RPC query; it does **not** verify contract implementation, protocol/factory identity, code audit, liquidity, reserves, issuer or equity rights.
- Query used block tag `latest`, with no explicit block-number/hash anchoring or independent RPC cross-check.
- No issuer deployment match for the selected pair's two token legs has been established in this review.
- GitHub job PASS reflects successful evidence capture; a future unsupported ABI would remain a `VERIFY` observation.

## Next acceptance gates

1. Compare **both** pool token legs against a timestamped official issuer asset registry; preserve negative and unknown outcomes.
2. Validate pool protocol/factory implementation and pool creation evidence against independently verifiable records.
3. Pin block number/hash for consistent `eth_call` and `eth_getCode`; independent RPC cross-check only after provider independence review.
4. Record provider/RPC error rate and recheck consistency across multiple runs.
5. Verify liquidity/reserves only with appropriate ABI and token decimals; no notional valuation without trustworthy pricing inputs.

**Gate: POOL V2 TOKEN LEGS MATCH / IDENTITY & LIQUIDITY NOT VERIFIED / PR #3 DRAFT / MERGE LOCKED.**
