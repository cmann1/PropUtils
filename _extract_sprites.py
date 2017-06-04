import json
import pickle

from SpriteExtractor import SpriteExtractor

sprite_extractor = SpriteExtractor()

sprite_extractor.read_textures = False
sprite_extractor.write_textures = False

sprite_data = {}
for prop_set in range(1, 7):
	sprite_extractor.debug_print = False
	sprites, textures = sprite_extractor.extract(sprite_data, 'C:/GOG Games/Dustforce DX/content/sprites/', 'props%i' % prop_set, prop_set)

	sprite_extractor.debug_print = False
	sprite_extractor.composite_sprites(sprites, textures)

	pass

sprite_extractor.get_sprite_names(sprite_data)

with open('sprite-data.json', 'w') as f:
	json.dump(sprite_data, f, indent='\t')
with open('sprite-data', 'wb') as f:
	pickle.dump(sprite_data, f)
