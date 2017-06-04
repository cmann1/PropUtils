import pickle
from SpriteExtractor import SpriteExtractor

with open('tile-data', 'rb') as f:
	tile_data = pickle.load(f)

sprite_extractor = SpriteExtractor()
sprite_extractor.make_tile_thumbnails(tile_data, (42, 42))
