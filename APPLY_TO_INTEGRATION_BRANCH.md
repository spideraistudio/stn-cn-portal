# Optional Git application

No Git installation is needed to run this package locally. The full working source is already present.

For a developer using a real clone of `spideraistudio/sellers-trust`, use the independently created `integration/stn-cn-2026-10-23` branch at Meet-Dev commit `491d892e5b5b507e87e18393babb0d0ada387607`. Do not apply the patch to the original Meet-Dev branch or to a live deployment checkout.

From a clean independent checkout at that commit:

```
git switch integration/stn-cn-2026-10-23
git apply --check --index PATH/TO/integration_changes.patch
git apply --index PATH/TO/integration_changes.patch
git commit -m "Integrate common company portal and private CN workspaces"
```

The binary-capable patch is included in the ZIP root. It stages the complete integration, including documentation otherwise excluded by STN's existing Markdown ignore rule. Inspect and test before any push. No force push or modification of Meet-Dev is needed.

`integration-history.bundle` contains the local independent snapshot/integration history. Its source snapshot has the exact 284 verified source blobs, but is not a replacement for the original repository's historical ancestry. Use the patch on the real integration branch when preserving that ancestry matters. `integration/source-manifest.json` and `verification/source_snapshot.txt` record the source provenance.
