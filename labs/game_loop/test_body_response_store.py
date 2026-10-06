"""Lab/package passive body model storage parity."""
import importlib.util,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'packages/mecha_engine/src'))
import campaign_store
spec=importlib.util.spec_from_file_location('body_store_probes',ROOT/'packages/mecha_engine/tests/helpers/storage_body_response_contract_driver.py')
probes=importlib.util.module_from_spec(spec);spec.loader.exec_module(probes)
class LabBodyResponseStoreTests(probes.StorageBodyResponseTests):
    store=campaign_store
