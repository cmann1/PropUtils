import zlib
import os
import os.path
import pickle

from PIL import Image

from ReadError import ReadError
from Rectangle import Rectangle
from SpriteChunk import SpriteChunk
from SpriteFrame import SpriteFrame
from Sprite import Sprite
from SpriteTexture import SpriteTexture

import dustmaker
from dustmaker.BitReader import BitReader


class SpriteExtractor:
	def __init__(self):
		self.reader = None
		self.print_indent = ''

		self.extract_dir = 'extracted_textures'
		self.composite_dir = 'sprites'

		self.debug_print = True
		self.read_textures = True
		self.write_textures = True
		self.split_sprite_name = True

		self.prop_groups = {}
		self.group_names = [
			"books", "buildingblocks", "chains", "decoration", "facade", "foliage", "furniture", "gazebo",
			"lighting", None, "statues", "storage", "study", "fencing", None, None,
			None, None, "backleaves", "leaves", "trunks", "boulders", "backdrops", "temple",
			"npc", "symbol", "cars", "sidewalk", "machinery"
		]

		for i in range(len(self.group_names)):
			group_name = self.group_names[i]
			if group_name is None:
				continue
			self.prop_groups[group_name] = i

		self.prop_sets = {}
		self.set_names = [None, "mansion", "forest", "city", "laboratory", "tutorial", "nexus"]

		for i in range(len(self.set_names)):
			set_name = self.set_names[i]
			if set_name is None:
				continue
			self.prop_sets[set_name] = i

		pass

	def print(self, *data):
		if self.debug_print:
			print(self.print_indent + ' '.join(str(x) for x in data))

	def print_group(self):
		self.print_indent += '|  '

	def print_ungroup(self):
		self.print_indent = self.print_indent[:-3]

	def expect(self, data):
		for x in data:
			if x != self.reader.read(8):
				raise ReadError('Unexpected data')
		pass

	def read_string(self):
		length = self.reader.read(8)

		string = ''
		for i in range(length):
			string += chr(self.reader.read(8))
		return string

	def read_rect(self, rect=None, size=16, signed=False):
		if rect is None:
			rect = Rectangle()

		top = self.reader.read(size, signed)
		left = self.reader.read(size, signed)
		bottom = self.reader.read(size, signed)
		right = self.reader.read(size, signed)

		rect.set(left, top, right, bottom)

		return rect

	def extract_sprites(self, reader, sprite_set_data, groups, group_count, prop_set=-1):
		for sprite_index in range(group_count):
			self.print('Reading Sprite [%i]\n-------------------------------------' % sprite_index)
			self.print_group()

			sprite = Sprite(prop_set)

			if self.split_sprite_name:
				group_data = self.read_string().split('_')
				sprite.group_name = group_data[0]
				if len(group_data) > 1:
					sprite.index = int(group_data[1])
			else:
				sprite.group_name = self.read_string()

			if sprite.group_name in self.prop_groups:
				sprite.group_index = self.prop_groups[sprite.group_name]
			else:
				sprite.group_index = sprite.group_name

			sprite.prefix = self.read_string()[:-1].replace('/', '_')
			self.print('[%s] %s %s_%s' % (sprite.group_index, sprite.prefix, sprite.group_name, sprite.index))

			if sprite.group_index not in sprite_set_data:
				sprite_group_data = sprite_set_data[sprite.group_index] = {'name': sprite.group_name, 'sprites': {}}
			else:
				sprite_group_data = sprite_set_data[sprite.group_index]

			sprite_data = sprite_group_data['sprites'][sprite.index] = {}

			num_extra = reader.read(32, True)
			reader.skip(num_extra * 8)
			self.print('Skipping %i extra bytes' % num_extra)

			frame_count = sprite.frame_count = reader.read(16, True)
			chunk_count = reader.read(16, True)
			unk11 = reader.read(16, True)
			unk12 = reader.read(16, True)
			unk13 = reader.read(16, True)
			palette_count = sprite.palette_count = reader.read(8)
			palette_frame_count = sprite.frame_count = int(frame_count / sprite.palette_count)

			sprite_data['palette_count'] = palette_count
			sprite_data['frame_count'] = palette_frame_count
			sprite_data['palettes'] = palette_data = [[] for x in range(palette_count)]
			sprite_data['set_index'] = prop_set
			sprite_data['group_index'] = sprite.group_index
			sprite_data['sprite_index'] = sprite.index

			self.print('frames: %i chunks:%i palettes:%i' % (frame_count, chunk_count, palette_count))
			self.print('unk: %i %i %i' % (unk11, unk12, unk13))

			for frame_index in range(frame_count):
				palette_frame_index = int(frame_index % palette_frame_count)
				palette_index = int(frame_index / palette_frame_count)
				self.print('[Reading Sprite Frame %i.%i]' % (palette_index, palette_frame_index))
				self.print_group()

				frame = SpriteFrame(palette_frame_index, palette_index)
				frame.field4 = reader.read(16, True)
				frame.field0 = reader.read(16, True)
				self.read_rect(frame.rect1, 16, True)
				self.read_rect(frame.rect2, 16, True)
				frame.chunks_offset = reader.read(32, True)
				frame.chunk_count = reader.read(16, True)
				frame.field28 = reader.read(8)

				sprite.frames.append(frame)

				x = frame.rect1.left
				y = frame.rect1.top
				w = frame.rect1.right - frame.rect1.left
				h = frame.rect1.bottom - frame.rect1.top
				palette_data[palette_index].append(dict(
					rect=(x, y, w, h),
					rect_uv=(x / 48, y / 48, w / 48, h / 48)
				))

				self.print('field0/4/28 [%i/%i/%i]' % (frame.field0, frame.field4, frame.field28))
				self.print('chunk [offset: %i count:%i]' % (frame.chunks_offset, frame.chunk_count))
				self.print('rect1 %s' % frame.rect1)
				self.print('rect2 %s' % frame.rect2)

				self.print_ungroup()
				pass

			for chunk_index in range(chunk_count):
				# self.print('[Reading Chunk %i]' % chunk_index)
				self.print_group()

				chunk = SpriteChunk()
				chunk.texture_index = reader.read(16, True)
				self.read_rect(chunk.source_rect, 8)
				chunk.x = reader.read(16, True)
				chunk.y = reader.read(16, True)

				# self.print('<%i, %i> %i' % (chunk.x, chunk.y, chunk.texture_index))
				# self.print('source_rect %s' % chunk.source_rect)

				sprite.chunks.append(chunk)

				self.print_ungroup()
				pass

			groups.append(sprite)

			self.print_ungroup()
			pass
		pass

	def extract_textures(self, reader, sprite_set_data, set_name, pixel_data_offset, textures, texture_count):
		reader.pos = (pixel_data_offset + 0x1a) * 8

		for texture_index in range(texture_count):
			self.print('[Reading Texture %i]' % texture_index)
			self.print_group()

			texture = SpriteTexture(set_name, reader.read(8), reader.read(8))

			self.print(texture.path)
			self.print('%i %i' % (texture.unk1, texture.unk2))

			zlen = reader.read(32)

			if self.read_textures:
				pixel_data = reader.read_bytes(zlen)
				pixel_data = zlib.decompress(pixel_data)

				image = texture.image = Image.frombytes('RGBA', (102, 102), pixel_data, 'raw', 'BGRA')

				if self.write_textures:
					image.save(os.path.join(self.extract_dir, texture.path))

				pass

			else:
				reader.skip(zlen * 8)
				pass

			textures.append(texture)

			self.print_ungroup()
			# if texture_index > 2:
			# 	break
			pass
		pass

	def extract(self, sprite_data, location, name, prop_set=-1):
		with open(os.path.join(location, name), 'rb') as f:
			reader = self.reader = BitReader(f.read())
			pass

		if not os.path.exists(self.extract_dir):
			os.makedirs(self.extract_dir)
			pass

		if prop_set not in sprite_data:
			sprite_set_data = sprite_data[prop_set] = {}
		else:
			sprite_set_data = sprite_data[prop_set]

		sprites = []
		textures = []

		try:
			self.expect(b'DF_SPR')
		except ReadError as e:
			print('Ignoring malformed sprite file:' + location + name)
			return None, None

		version = reader.read(16)
		if version != 0x2c:
			raise ReadError('Invalid Data')
		group_count = reader.read(16)
		texture_count = reader.read(16)
		unk3 = reader.read(16)
		unk4 = reader.read(16)
		unk5 = reader.read(16)
		pixel_data_offset = reader.read(32, True)
		pixel_data_length = reader.read(32, True)

		self.print('%s sprites[%i] textures[%i]\nunk3/4/5[%i/%i/%i]\npixel_data[offset:%i, length: %i]\n' % (location + name, group_count, texture_count, unk3, unk4, unk5, pixel_data_offset, pixel_data_length))

		self.extract_sprites(reader, sprite_set_data, sprites, group_count, prop_set)

		self.extract_textures(reader, sprite_set_data, name, pixel_data_offset, textures, texture_count)

		return sprites, textures
		pass

	def composite_sprites(self, sprites, textures, file_name_format=None):
		if not os.path.exists(self.composite_dir):
			os.makedirs(self.composite_dir)
			pass

		for sprite in sprites:
			self.print('Compositing Sprite [%s %s_%i]\n-------------------------------------' % (sprite.prefix, sprite.group_name, sprite.index))
			self.print_group()

			for frame in sprite.frames:
				if file_name_format is None:
					# filename = '%s%s_%i_%i_%04i' % (sprite.prefix.replace('/', '_'), sprite.group_name, sprite.index, frame.palette + 1, frame.index + 1)
					filename = '%s_%i_%s_%i_' % (sprite.group_name, sprite.prop_set, sprite.group_index, sprite.index)
					path = os.path.join(self.composite_dir, filename + '.png')
				else:
					format_string = file_name_format[0]
					format_params_list = file_name_format[1]
					format_params = []
					for param_name in format_params_list:
						if param_name == '__frame_index':
							format_params.append(frame.index + 1)
						elif param_name == '__palette_index':
							format_params.append(frame.palette + 1)
						else:
							format_params.append(sprite.__dict__[param_name])
					path = os.path.join(self.composite_dir, format_string.format(*format_params) + '.png')

				if os.path.isfile(path):
					continue

				sprite_image = Image.new('RGBA', (frame.rect1.width() - 1, frame.rect1.height() - 1), 0x00000000)
				self.print(frame.rect1.left, frame.rect1.top)

				for chunk_index in range(frame.chunk_count):
					chunk = sprite.chunks[frame.chunks_offset + chunk_index]
					texture = textures[chunk.texture_index]

					left = chunk.x - frame.rect1.left
					top = chunk.y - frame.rect1.top

					source_rect = chunk.source_rect
					chunk_region = texture.image.crop((source_rect.left, source_rect.top, source_rect.right, source_rect.bottom))
					# self.print('-', chunk.source_rect.width(), chunk.source_rect.height())

					sprite_image.paste(chunk_region, (
						left + source_rect.left, top + source_rect.top,
						left + source_rect.right, top + source_rect.bottom
					))

				sprite_image.save(path)

				pass
			pass

			self.print_ungroup()
		pass

	def get_sprite_names(self, sprite_data):
		# print(sprite_data)
		sprites = os.listdir(self.composite_dir)

		for sprite_file in sprites:
			sprite_file = sprite_file[:-4].split('_', 4)
			group_name = sprite_file[0]
			prop_set = int(sprite_file[1])
			group_index = int(sprite_file[2])
			prop_index = int(sprite_file[3])
			prop_name = sprite_file[4]
			prop_name_nice = prop_name.replace('_', ' ').title()
			# print(group_name, prop_set, group_index, prop_index, prop_name, '"' + prop_name_nice + '"')
			# print(sprite_data[prop_set][group_index]['sprites'][prop_index])

			sprite = sprite_data[prop_set][group_index]['sprites'][prop_index]
			sprite['name'] = prop_name
			sprite['name_nice'] = prop_name_nice

			pass

		pass

	def calculate_sprite_bounds(self, sprite_data):
		# Save out the images of applying an alpha threshold
		# Purely for testing purposes
		save_alpha_images = False
		alpha_dir = 'sprites_alpha'

		if save_alpha_images:
			if not os.path.exists(alpha_dir):
				os.makedirs(alpha_dir)
				pass

		threshold = 150
		sprites = os.listdir(self.composite_dir)

		# Mostly transparent sprites won't work well, so provide custom bounds for them
		custom_bbox = {
			'backdrops_1_22_4_moon': (3, 3, -1, -1),
			'backdrops_1_22_5_black_water': (3, 3, -1, -1),
			'backdrops_2_22_4_sun': (3, 3, -1, -1),
			'backdrops_3_22_3_ellipse': (3, 3, -1, -1),
			'backdrops_3_22_4_light_beam': (3, 3, -1, -1),
			'decoration_2_3_1_drape': (3, 3, -1, -1),
			'foliage_2_5_16_stain_small': (3, 3, -1, -1),
			'foliage_2_5_17_stain_medium': (3, 3, -1, -1),
			'foliage_2_5_18_stain_large': (3, 3, -1, -1),
		}

		for sprite_file in sprites:
			file_name = sprite_file[:-4]
			sprite_file_data = file_name.split('_', 4)
			group_name = sprite_file_data[0]
			prop_set = int(sprite_file_data[1])
			group_index = int(sprite_file_data[2])
			prop_index = int(sprite_file_data[3])

			prop_data = sprite_data[prop_set][group_index]['sprites'][prop_index]
			frame_data = prop_data['palettes'][0][0]
			x, y, w, h = frame_data['rect']

			# print(sprite_file, prop_set, group_index, prop_index)

			if file_name in custom_bbox:
				bbox = custom_bbox[file_name]
			else:
				sprite_image = Image.open(os.path.join(self.composite_dir, sprite_file))
				data = sprite_image.getdata()
				new_data = []
				a = 0
				for index in range(len(data)):
					r, g, b, a = data[index]
					a += 1
					if a < threshold:
						new_data.append((0, 0, 0, 0))
					else:
						new_data.append((r, g, b, a))
				sprite_image.putdata(new_data)
				bbox = sprite_image.getbbox()

				if save_alpha_images:
					sprite_image.save(os.path.join(alpha_dir, sprite_file))

			if bbox is None:
				bbox = (3, 3, -1, -1)

			left, top, right, bottom = bbox
			if left < 3:
				left = 3
			if top < 3:
				top = 3
			if right < left:
				right = w
			if bottom < top:
				bottom = h

			b_width = right - left
			b_height = bottom - top
			prop_data['bounds'] = (left, top, b_width, b_height)
			prop_data['bounds_uv'] = (left / w, top / h, b_width / w, b_height / h)

			pass
		pass

	def make_prop_thumbnails(self, data_file, size=(32, 32), match_size=True):
		with open(data_file, 'rb') as f:
			prop_data = pickle.load(f)

		thumb_dir = 'prop_thumbnails/'
		if not os.path.exists(thumb_dir):
			os.makedirs(thumb_dir)
			pass

		for set_index, sprite_set in prop_data.items():
			for group_index, sprite_group in sprite_set.items():
				group_name = sprite_group['name']
				for sprite_index, sprite in sprite_group['sprites'].items():
					sprite_file = 'sprites/%s_%i_%i_%i_%s.png' % (group_name, set_index, group_index, sprite_index, sprite['name'])

					if not os.path.isfile(sprite_file):
						print('Cannot find sprite file:', sprite_file)
						continue

					image = Image.open(sprite_file)
					image.thumbnail(size)

					if match_size and (image.size[0] != size[0] or image.size[1] != size[1]):
						new_image = Image.new('RGBA', size, 0x000000)
						new_image.paste(image, (int((size[0] - image.size[0]) / 2), int((size[1] - image.size[1]) / 2)))
						image = new_image

					image.save('%s/%s %s.png' % (thumb_dir, group_name, sprite['name']))

					pass
				pass
			pass

		pass  # END func

	def get_tile_names(self):
		tile_folder = 'tiles/'
		tile_files = os.listdir(tile_folder)

		name_map = dict()
		set_map = dict()
		tile_data = dict(
			sets=set_map,
			names=name_map
		)

		for tile_file in tile_files:
			tile_set, tile_info, name, *palette_name = tile_file[:-4].split('-')
			palette_name = '-' + palette_name[0] if palette_name else ''
			tile_info = tile_info[4:].split('_')
			tile_index = int(tile_info[0])
			palette_index = int(tile_info[1])
			tile_set_index = int(dustmaker.TileSpriteSet[tile_set])

			if tile_set_index not in set_map:
				set_data = set_map[tile_set_index] = dict()
				# print(set_data)
			else:
				set_data = set_map[tile_set_index]

			if tile_index not in set_data:
				tile = set_data[tile_index] = dict(
					set_index=tile_set_index,
					index=tile_index,
					palettes=dict(),
					name=name,
					name_nice=name.replace('_', ' ').title(),
				)
			else:
				tile = set_data[tile_index]

			tile['palettes'][palette_index] = palette_name

			name_map['%s %s%s' % (tile_set, name, palette_name)] = (tile_set_index, tile_index, palette_index)

			# print('  ', tile_set, tile_index, tile_palette, name, palette_name)
			# print('    ', set_data[tile_index])
			pass

		return tile_data
		pass  # END func

	def make_tile_thumbnails(self, tiles_data, size=(32, 32), padding=10):
		tile_folder = 'tiles/'

		thumb_dir = 'tile_thumbnails/'
		if not os.path.exists(thumb_dir):
			os.makedirs(thumb_dir)
			pass

		set_map = tiles_data['sets']

		for set_index, set_data in set_map.items():
			set_name = dustmaker.TileSpriteSet(set_index).name

			for tile_index, tile_data in set_data.items():
				tile_name = tile_data['name']

				for palette_index, palette_name in tile_data['palettes'].items():
					file_name = '%s%s-tile%i_%i_0001-%s%s.png' % (tile_folder, set_name, tile_index, palette_index, tile_name, palette_name)

					if not os.path.isfile(file_name):
						print('Cannot find tile file:', file_name)
						continue

					image = Image.open(file_name)
					middle = image.crop((96, 96, 96 + 96, 96 + 96))
					left = image.crop((0, 96, 0 + 96, 96 + 96))
					right = left.transpose(Image.FLIP_LEFT_RIGHT)
					top = image.crop((96 * 3, 0, 96 * 3 + 96, 0 + 96))
					bottom = image.crop((96 * 3, 96 * 4, 96 * 3 + 96, 96 * 4 + 96))

					tile_image = Image.new('RGBA', (128, 128), 0x00000000)
					left_src = Image.new('RGBA', (128, 128), 0x00000000)
					right_src = Image.new('RGBA', (128, 128), 0x00000000)
					top_src = Image.new('RGBA', (128, 128), 0x00000000)
					bottom_src = Image.new('RGBA', (128, 128), 0x00000000)
					l = t = 16
					r = b = 128 - 16
					tile_image.paste(middle, (l, t,   r, b))
					left_src.paste(left, (l - 48, t), left)
					right_src.paste(right, (r - 48, t), right)
					top_src.paste(top, (l, t - 48), top)
					bottom_src.paste(bottom, (l, b - 48), bottom)

					tile_image = Image.alpha_composite(tile_image, left_src)
					tile_image = Image.alpha_composite(tile_image, right_src)
					tile_image = Image.alpha_composite(tile_image, top_src)
					tile_image = Image.alpha_composite(tile_image, bottom_src)

					tile_image = tile_image.crop((l - padding, t - padding, r + padding, b + padding))
					tile_image.thumbnail(size)
					tile_image.save('%s%s %s%s.png' % (thumb_dir, set_name, tile_name, palette_name))

				# file_name = '%s %s.png' % (set_name, tile_data['name'])
				# print('  %s' % (tile_data['palette_name']))

			pass

		pass  # END func

