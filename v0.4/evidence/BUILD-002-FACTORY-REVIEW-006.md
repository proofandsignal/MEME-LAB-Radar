# BUILD-002 — Factory Provenance Review 006

Review date: 2026-10-19
Target chain: Robinhood Chain (4663)
Pool: `0x0092f73B6821098F66eEa758cf7eeB0F834C2303`
Factory returned at pinned block: `0x5481864ddd46a2d798df0925c23b7846e776e5e3`

## Evidence already established

- Provider pair returned token legs consistent with V2 ABI RPC reads.
- Pool `factory()` call returned the target address and bytecode exists at that address.
- Reads were pinned to block 92380270 with stable block hash.
- NVDA base address matched Robinhood issuer deployment and USDG quote onchain metadata matched.
- None of these proves factory code provenance or protocol legitimacy.

## Public deployment provenance review

The following primary/public references were examined:
- Robinhood Chain official developer overview (permissionless network): https://docs.robinhood.com/chain/
- Robinhood Chain contract verification procedure: https://docs.robinhood.com/chain/deploy-smart-contracts/
- Robinhood Chain Topaz DEX official contract list: https://www.topazdex.com/docs/contracts
- hood.dev public deployment address list: https://hood.dev/docs/addresses

No **reliable, official protocol deployment record tying the target factory address to a named DEX** was established by this review. Lack of a match in reviewed references is NOT proof the factory is malicious or absent.

**Factory provenance status: UNKNOWN / NOT VERIFIED.**

## Necessary independent gates

1. Obtain the verified contract page for the exact factory address from Robinhood Chain Blockscout and examine verified source, code identity and creation transaction (if available).
2. Cross-check exact factory address against the purported DEX's first-party deployment list; if protocol cannot be identified, do not infer one from V2 ABI.
3. Read factory `getPair(token0,token1)` where supported and confirm it returns exact pool; where unsupported, record UNKNOWN and investigate protocol-specific factory ABI.
4. Prove a factory-created pool via creation logs/transaction and factory source code; a `factory()` return value can be forged by arbitrary code.
5. Reproduce critical results at anchored blocks and qualify independent RPC provider before use.
6. Hold liquidity/reserves valuation until verified factory/protocol ABI, token decimals and independent source cross-check.

No forced protocol label, issuer endorsement, trading signal, merge or deployment.

**Gate: NVDA ISSUER MATCH → V2 LEGS MATCH → BLOCK ANCHOR PASS → USDG METADATA MATCH → FACTORY PROVENANCE UNKNOWN → LIQUIDITY LOCKED → PR #3 DRAFT**
