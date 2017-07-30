#
# Extracts sprites in a convenient format for generating sprite reference sheets
#

import sys

import json
import pickle
from os import listdir
from os.path import isfile, join

from SpriteExtractor import SpriteExtractor

sprite_extractor = SpriteExtractor()
sprite_extractor.read_textures = True
sprite_extractor.write_textures = True

sprite_extractor.split_sprite_name = False
sprite_extractor.extract_dir = 'extracted_textures_all'
sprite_extractor.composite_dir = 'reference_sprites'

sprite_path = sys.argv[1] if len(sys.argv) > 1 else 'C:/GOG Games/Dustforce DX/content/sprites/'

sprite_data = {}

for sprite_file in listdir(sprite_path):
	if sprite_file[:5] == 'intro':
		continue

	print('>>', sprite_file)
	if isfile(join(sprite_path, sprite_file)):
		sprite_extractor.debug_print = False
		sprites, textures = sprite_extractor.extract(sprite_data, sprite_path, sprite_file, sprite_file)

		if sprites is not None:
			sprite_extractor.debug_print = False
			sprite_extractor.composite_sprites(sprites, textures, ('{}\\{}-{}-{:04d}', ('sprite_set_name', 'group_name', '__palette_index', '__frame_index')))

	pass

# sprite_count = 0
# for sprite_set, set_data in sprite_data.items():
# 	for sprite_name, sprite_data in set_data.items():
# 		sprite_count += 1
#
# print(sprite_count)

with open('sprites-reference-data.json', 'w') as f:
	json.dump(sprite_data, f, indent='\t')
with open('sprites-reference-data', 'wb') as f:
	pickle.dump(sprite_data, f)
