#!/usr/bin/env bash
set -euo pipefail
/bridge/labctl update
/bridge/labctl shell /work/.odoo-agents/flow-artifacts/preparation-d02/check_copy.py
/bridge/labctl shell /work/changelog/2026-09-09_01_frais-de-preparation-d-02/scripts/recompute_totals.py
/bridge/labctl shell /work/.odoo-agents/flow-artifacts/preparation-d02/check_copy.py
/bridge/labctl shell /work/changelog/2026-09-09_01_frais-de-preparation-d-02/scripts/recompute_totals.py
/bridge/labctl shell /work/.odoo-agents/flow-artifacts/preparation-d02/check_copy.py
/bridge/labctl shell /work/.odoo-agents/flow-artifacts/preparation-d02/cleanup.py
