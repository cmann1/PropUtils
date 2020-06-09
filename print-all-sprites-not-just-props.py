from SpriteExtractor import SpriteExtractor
import os


SPRITES_PATH = 'C:/GOG Games/Dustforce DX/content/sprites/'


sprite_extractor = SpriteExtractor()

sprite_extractor.read_textures = False
sprite_extractor.write_textures = False
sprite_extractor.debug_print = True

sprite_data = {}

for sprite_file_name in os.listdir(SPRITES_PATH):
	sprite_extractor.extract(sprite_data, SPRITES_PATH, sprite_file_name)
	# sprite_file = os.path.join(SPRITES_PATH, sprite_file_name)
	# print(sprite_file)
