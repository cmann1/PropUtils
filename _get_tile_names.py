import pickle
import json
from SpriteExtractor import SpriteExtractor

sprite_extractor = SpriteExtractor()
tile_data = sprite_extractor.get_tile_names()

with open('tile-data.json', 'w') as f:
	json.dump(tile_data, f, indent='\t')
with open('tile-data', 'wb') as f:
	pickle.dump(tile_data, f)
