# ACIS Track Record — Public Beacon

A public, cryptographically-anchored record of every production rebalance produced by ACIS ("Alpha Centauri Intelligence Systems", [alphacentauriai.com](https://alphacentauriai.com)).

Each rebalance is published as a canonical JSON **manifest**: the target holdings, the model that generated them, the market regime at the time, the AI commentary, and the walk-forward backtest statistics motivating the strategy. Manifests are:

1. **Deterministically serialized** — sort_keys, no whitespace, UTF-8; two independent parties producing the same input produce byte-identical output.
2. **Hashed** — SHA-256 of the manifest content is embedded inside the manifest itself.
3. **Anchored to Bitcoin via [OpenTimestamps](https://opentimestamps.org/)** — every manifest ships with a `.ots` proof, upgraded to a Bitcoin block within 24h. Once upgraded, no party — including ACIS — can rewrite the timestamp.
4. **Chained** — every manifest embeds the `content_hash` of the previous manifest for the same `(stream, strategy_id)` pair. Silent rewrites of history require forging every downstream entry and every OTS proof, which is not computationally feasible.

Please read **[DISCLOSURES.md](DISCLOSURES.md)** before drawing any conclusions from this repository. In particular: the anchor proves the manifest existed by a given date; it does not prove execution, exclusive publication, or future performance.

## Repository layout

```
manifests/
├── equity/            # 8 equity strategies, rebalanced quarterly (Option C: Jan/Apr/Jul/Oct 1)
├── sector_rotation/   # 11-sector ETF vol-targeted rotation, rebalanced daily
└── options/           # Options master pipeline configs, rebalanced daily
schema/
└── manifest_v1.schema.json    # JSON Schema for the manifest format
verify/
└── verify_manifest.py         # Self-contained CLI verifier (Python 3.10+)
index.jsonl                    # Append-only index of every published manifest
```

Each manifest file is named `{YYYYMMDD_HHMMSS}Z_{content_hash_prefix}.json` and is accompanied by `{same}.json.ots` (the OpenTimestamps proof).

## Rebalance cadence

| Stream          | Cadence            | Strategies              |
| --------------- | ------------------ | ----------------------- |
| Equity          | Quarterly (Jan/Apr/Jul/Oct 1, 20:00 America/Los_Angeles) | 8 strategies |
| Sector rotation | Daily EOD          | 1 strategy (vol-targeted 15%) |
| Options         | Daily EOD          | Multiple configs        |

Off-cadence rebalances (manual salvage, config changes) are also published; each carries an explicit `run_type` field distinguishing scheduled from ad-hoc.

## Verifying a manifest

Any third party can verify a manifest with only public tools. Install once:

```
pip install opentimestamps-client
```

Then, for any manifest file `<file>.json`:

```
# 1. Recompute the content hash
python verify/verify_manifest.py <file>.json

# 2. Verify the OpenTimestamps proof (needs a Bitcoin block header source; --no-bitcoin uses public calendars)
ots verify --no-bitcoin <file>.json.ots
```

The verify script:
- Recomputes SHA-256 of the manifest with `content_hash` field removed, using deterministic serialization.
- Confirms the computed hash matches the `content_hash` embedded in the manifest.
- Validates the manifest against `schema/manifest_v1.schema.json`.
- Follows `prev_manifest_hash` back through the chain to confirm append-only integrity.

## Retroactive entries

The repository launch date is embedded in the earliest live-anchor manifest. Manifests dated before that are marked `retroactive: true` and represent ACIS's historical records republished in canonical format. Their cryptographic anchor proves existence *no later than the anchor date* — it does NOT vouch for the pick timing. Live entries carry `retroactive: false` and `anchor_date == original_event_date`; those are third-party-verifiable.

## Reporting an issue

Data-integrity concerns, verification failures, or corrections: file an issue on this repository, or email frank@acis-trading.com.

Nothing in this repository is investment advice. See DISCLOSURES.md.
