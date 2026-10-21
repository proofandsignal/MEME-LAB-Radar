# BUILD-002 — Factory getPair Evidence Review 007

Date: 2026-10-20
Run: https://github.com/proofandsignal/MEME-LAB-Radar/actions/runs/39361541657
Artifact: build-002-factory-getpair-evidence (ID 12238001160)

## Observed result

- Timestamp: `2026-10-20T02:55:39.484848+00:00`
- Factory: `0x5481864ddd46a2d798df0925c23b7846e776e5e3`
- Pool: `0x0092f73B6821098F66eEa758cf7eeB0F834C2303`
- Anchor: block `0x58cebab`, hash `0xea3f6b1616b62f8ba264fe7ce3cc2e9ec2ea7b641af26b5396b819c669c0682d`
- `eth_chainId`: OK
- `eth_getBlockByNumber`: OK
- First `eth_call` for `getPair(address,address)`: VERIFY, `unreliable RPC result`.
- No successful returned pool address. Second argument-order query was not reached.
- Workflow status: FAILURE (correctly blocking verification).

## Interpretation

This does NOT prove factory mismatch or maliciousness, nor does it prove V2 ABI compatibility. Our generic RPC wrapper currently collapses JSON-RPC error objects into `unreliable RPC result`. We must capture sanitized JSON-RPC error code/message for this method without changing provider or storing secrets, and distinguish revert / unsupported selector / transient RPC provider failures.

## Next actions

1. Improve read-only RPC error diagnostics to retain method and sanitized JSON-RPC error code/message, without retaining sensitive request headers.
2. Add tests for error-object handling and unsupported factory ABI.
3. Repeat pinned factory `getPair` read and archive raw/sanitized evidence.
4. Require verified factory source, creation events and official protocol deployment reference before `FACTORY_PROVENANCE_VERIFIED`.
5. Keep liquidity, BUILD-002 acceptance and PR #3 merge locked.

**Decision: FACTORY GETPAIR VERIFY → ABI/RPC ERROR DIAGNOSIS PENDING → FACTORY PROVENANCE UNKNOWN → LIQUIDITY LOCKED.**
