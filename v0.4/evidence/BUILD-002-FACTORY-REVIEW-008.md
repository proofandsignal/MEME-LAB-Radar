# BUILD-002 — Factory RPC Diagnostic Review 008

Review date: 2026-10-21
Source: https://github.com/proofandsignal/MEME-LAB-Radar/actions/runs/39372398475
Artifact: `build-002-factory-getpair-evidence` (ID `12242101934`).

## Confirmed observed failure

- Observed at `2026-10-20T04:58:44.425032+00:00`.
- Factory `0x5481864ddd46a2d798df0925c23b7846e776e5e3`.
- Target pool `0x0092f73B6821098F66eEa758cf7eeB0F834C2303`.
- Anchor block `0x58dffd1`, hash `0x7aefff270ca8a8f853a47063f319acc51f17b5d8899b5b42c92c912e1df6bd43`.
- `eth_chainId`: OK.
- `eth_getBlockByNumber`: OK.
- First `eth_call` to presumed V2 factory `getPair(address,address)`: **RPC_JSON_ERROR method=eth_call code=3 category=execution_reverted**.
- No decoded pool address from factory; reversed token-order call not reached.
- Run concludes failure, as it should.

## What is and is not proven

**Proven:** The Robinhood RPC returned an execution-reverted JSON-RPC error for the attempted selector and arguments in this read. This is **not an HTTP 403** and cannot be classified as transient endpoint refusal.

**Not proven:** That the factory supports the assumed Uniswap-V2 `getPair` ABI, that the factory is legitimately deployed by a named protocol, that the pool is factory-created, or that pool reserves/liquidity are trustworthy.

## Next technical steps (no ABI guesses)

1. Retrieve verified source / verified ABI for the exact factory contract through official explorer contract verification records. If unavailable, record `ABI_UNKNOWN`.
2. Identify protocol from first-party deployment records; confirm exact factory address, code provenance, and creation transaction/logs.
3. Only if ABI evidence establishes method support, rerun `getPair` and compare both token orders at anchored height.
4. Capture sanitized RPC `code=3` classification in regression fixtures; no raw error bodies or keys.
5. Do not read/interpret reserves for economic signals while factory provenance remains unverified.

**Decision:** `FACTORY_GETPAIR_EXECUTION_REVERTED → ABI_UNKNOWN → FACTORY_PROVENANCE_UNKNOWN → LIQUIDITY_LOCKED → BUILD-002_NOT_ACCEPTED → PR_3_DRAFT`.

No merge, deployment, trading, RPC provider switch, or other repository changes.
