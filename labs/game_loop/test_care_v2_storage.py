"""Care-v2 lab storage uses the same passive-ledger refusal probes as package."""
import importlib.util
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
for path in (Path(__file__).resolve().parent, ROOT / 'packages/mecha_engine/src'):
    sys.path.insert(0, str(path))
import campaign_store
spec = importlib.util.spec_from_file_location('storage_care_v2_probes',
    ROOT / 'packages/mecha_engine/tests/helpers/storage_care_v2_contract_driver.py')
probes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probes)


class LabStorageCareV2Tests(probes.StorageCareV2Tests):
    store = campaign_store
