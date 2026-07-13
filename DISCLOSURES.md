# Disclosures

## What this repository is

This repository is a **public research record** of the model outputs produced by ACIS ("Alpha Centauri Intelligence Systems", operating at alphacentauriai.com). Each entry (a "manifest") is a machine-readable snapshot of a single rebalance event: the target holdings, the model that generated them, the market regime at the time, and — where available — the AI-generated commentary and out-of-sample backtest statistics that motivated the picks.

Every manifest is:

1. **Deterministically serialized** — JSON with sorted keys, no whitespace, UTF-8. Two independent parties producing the same input data will produce byte-identical output.
2. **Cryptographically hashed** — the SHA-256 of the manifest content is recorded inside the manifest itself, and the manifest is committed to this public git repository.
3. **Anchored to Bitcoin via OpenTimestamps** — a `.ots` proof file accompanies each manifest. Once the OpenTimestamps calendar upgrade completes (typically within 24 hours), the manifest hash is provably included in a Bitcoin block, giving a timestamp that no party — including ACIS — can rewrite.

## What the anchor proves

For any manifest with an OTS proof that has been upgraded to a Bitcoin block, the following is cryptographically verifiable by any third party using only public tools (`opentimestamps-client` and a Bitcoin block header archive):

> "The exact bytes of this manifest existed no later than `anchor_date`."

That's it. Specifically, the anchor **does not** prove any of the following:

- That ACIS actually deployed capital according to the manifest.
- That the model outputs represent the *only* model outputs ACIS produced on that date (i.e., the anchor cannot rule out cherry-picking across an ensemble of runs *before* the anchor date — it can only rule out cherry-picking *after* it).
- That the strategies described will replicate their historical statistics going forward.
- Anything about `original_event_date` for entries where `retroactive: true` (see below).

## Retroactive entries

Manifests with `retroactive: true` document rebalances whose `original_event_date` precedes the repository's first live anchor. These are ACIS's own historical records republished in the canonical manifest format. Their cryptographic guarantee begins at `anchor_date`, not `original_event_date` — the OTS proof only shows the manifest existed as of the anchor.

Retroactive entries are labelled to prevent misreading. Nothing about them is falsified; they are simply presented as an internal record rather than a third-party-verifiable pick timing.

Once the first live rebalance is anchored, all subsequent entries carry `retroactive: false` and their `original_event_date` equals their `anchor_date`. These entries carry the full cryptographic guarantee.

## Not investment advice

This repository documents the outputs of proprietary quantitative research models. It is published for research transparency and to establish a verifiable record of model performance. **Nothing in this repository constitutes investment advice, a recommendation to buy or sell any security, or an offer of any investment product.** Past model performance — retroactive or otherwise — does not indicate future results. Individuals should consult a licensed advisor before making investment decisions.

## The manifest chain

Every manifest references the `content_hash` of the previous manifest for the same `(stream, strategy_id)` pair via the `prev_manifest_hash` field. This produces an append-only chain per strategy: any silent rewrite of history requires forging every subsequent entry AND the corresponding OTS/Bitcoin proofs, which is not computationally feasible.

If a manifest is later found to contain a data error — a mis-labeled ticker, an incorrect model version — the correction is published as a **new** manifest with `run_type: "manual_salvage"` referencing the original. The original manifest is never deleted, edited, or unpinned.

## What ACIS can still hide

Full disclosure of what this design does not defend against:

- **Selective publication of streams.** ACIS could operate additional strategies that never appear in this repository. The chain guarantees continuity *within* a published stream, not that all streams are published.
- **Pre-anchor cherry-picking on live entries.** For a live entry with `original_event_date == anchor_date`, ACIS could in principle run many model configurations and only anchor the ones that later look good. This is mitigated by publishing consistent streams on regular cadences (see `README.md` for schedule) — a pattern that would break if entries were being selectively omitted.
- **Off-book execution.** The repository documents *model output*, not fills. A separate paper-trading and live-trading reconciliation record is maintained internally but is not part of this beacon.

These limits are inherent to the design; no cryptographic scheme can defend against them without introducing custodial trust that would undermine the point.

## Contact

Questions about the disclosures or verification: frank@acis-trading.com
