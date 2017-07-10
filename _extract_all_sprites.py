import json
import pickle
from os import listdir
from os.path import isfile, join

from SpriteExtractor import SpriteExtractor

sprite_extractor = SpriteExtractor()

sprite_extractor.read_textures = True
sprite_extractor.write_textures = True
sprite_extractor.read_textures = False
sprite_extractor.write_textures = False
sprite_extractor.split_sprite_name = False
sprite_extractor.extract_dir = 'extracted_textures_all'
sprite_extractor.composite_dir = 'sprites_all'

sprites_list = []
sprite_data = {}
sprite_path = 'C:/GOG Games/Dustforce DX/content/sprites/'
for sprite_file in listdir(sprite_path):
	if sprite_file[:5] == 'intro':
		continue

	print('>>', sprite_file)
	if isfile(join(sprite_path, sprite_file)):
		sprite_extractor.debug_print = False
		sprites, textures = sprite_extractor.extract(sprite_data, sprite_path, sprite_file, 0)

		if sprites is not None:
			sprites_list.extend(sprites)
		# 	sprite_extractor.debug_print = False
		# 	sprite_extractor.composite_sprites(sprites, textures, ('{0}-{1}-{2:04d}', ('prefix', 'group_name', '__frame_index')))

	pass

sprite_data = {}
for sprite in sprites_list:
	if sprite.prefix not in sprite_data:
		sprite_set_data = sprite_data[sprite.prefix] = {}
	else:
		sprite_set_data = sprite_data[sprite.prefix]

	# palettes = [[] for x in range(sprite.palette_count)]

	# for frame in sprite.frames:
	# 	palettes[frame.palette].append((frame.rect1.left, frame.rect1.top, frame.rect1.width(), frame.rect1.height()))

	for frame in sprite.frames:
		sprite_set_data[sprite.group_name] = (frame.rect1.left, frame.rect1.top, frame.rect1.width(), frame.rect1.height())
		break

# sprite_extractor.calculate_sprite_bounds(sprite_data)

with open('sprites-all-data.json', 'w') as f:
	json.dump(sprite_data, f, indent='\t')
with open('sprite-all-data', 'wb') as f:
	pickle.dump(sprite_data, f)
