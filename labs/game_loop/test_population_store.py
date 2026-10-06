"""X8 lab-first population storage contract."""
import importlib.util
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
for path in (Path(__file__).resolve().parent,ROOT/'packages/mecha_engine/src'):sys.path.insert(0,str(path))
import campaign_store
spec=importlib.util.spec_from_file_location('storage_population_probes',ROOT/'packages/mecha_engine/tests/helpers/storage_population_contract_driver.py')
probes=importlib.util.module_from_spec(spec);spec.loader.exec_module(probes)
class LabStoragePopulationTests(probes.StoragePopulationTests):
    store=campaign_store
