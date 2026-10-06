"""Lab-first X5 storage gates using the package's independent synthetic probes."""
import importlib.util
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
for path in (LAB_DIR, ROOT / 'packages/mecha_engine/src'):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
import campaign_store

spec = importlib.util.spec_from_file_location('storage_execution_probes',
    ROOT / 'packages/mecha_engine/tests/helpers/storage_execution_contract_driver.py')
probes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probes)


class LabStorageExecutionTests(probes.StorageExecutionTests):
    store = campaign_store
    impl = campaign_store
