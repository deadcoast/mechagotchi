from pathlib import Path
import sys, json
from unittest.mock import patch
sys.stdout.reconfigure(encoding='utf-8')
root=Path.cwd(); sys.path[:0]=[str(root/'game/src'),str(root/'packages/mecha_engine/src')]
from mecha_game import packets,campaign
bundle=root/'game/dist/w5-integrated-finish-release/Mechagotchi/_internal'
is_file=Path.is_file; is_dir=Path.is_dir
# Read the actual retained bundle, hiding ancestor-checkout files to model detachment.
def bundled_file(p): return p.is_relative_to(bundle) and is_file(p)
def bundled_dir(p): return p.is_relative_to(bundle) and is_dir(p)
print('Probe: actual packaged data; ancestor checkout discovery hidden (not a native relocated launch).')
with patch.object(packets,'data_search_origins',return_value=[bundle]), patch.object(Path,'is_file',bundled_file), patch.object(Path,'is_dir',bundled_dir):
 for name,call in [('default_fixtures',packets.default_fixture_paths),('default_campaign',campaign.default_campaign_paths),('real_weather',campaign.load_real_weather_source),('callback_weather',campaign.load_callback_weather_source)]:
  try: value=call(); print(name,'OK')
  except Exception as exc: print(name,type(exc).__name__,str(exc))
print('real_weather_payload_bytes', (root/campaign.REAL_INGEST_REPORT).stat().st_size)
print('callback_payload_bytes', (root/campaign.CALLBACK_STATES_PATH).stat().st_size)
print('No repository files written.')
