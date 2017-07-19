import os
import math
import pickle

from PIL import Image, ImageFont, ImageDraw

out_dir = 'files/tiles_reference'
thumb_dir = 'tile_thumbnails'
set_names = [None, 'mansion', 'forest', 'city', 'laboratory', 'tutorial', 'nexus']
font_size = 12
font = ImageFont.truetype('files/DejaVuSans.ttf', font_size)
title_font = ImageFont.truetype('files/DejaVuSans.ttf', 15)
quality = 98

thumb_size = 42
thumb_spacing = 25
col_spacing = 50
row_spacing = 70
padding_top = 20
row_title_height = 20

with open('tile-data', 'rb') as f:
	tile_data = pickle.load(f)


def draw_with_alpha(dst, img, x, y, src_mask=None):
	src2 = None

	if src_mask is not None:
		src2 = Image.new(img.mode, img.size, 0x00000000)
		src2.paste(img, (0, 0), src_mask)
		src = src2

	x, y = int(x), int(y)
	base = dst.crop((int(x), int(y), x + img.width, y + img.height))
	base = Image.alpha_composite(base, img)
	dst.paste(base, (x, y))

	if src2 is not None:
		src2.close()

	base.close()

	pass

for set_index, tiles in tile_data['sets'].items():
	set_name = set_names[set_index]
	count = len(tiles)
	num_rows = int(math.ceil(math.sqrt(count)))
	num_cols = int(math.ceil(count / num_rows))

	# print(set_index, set_name, num_cols, num_rows)

	i = 0
	column_width = 0
	set_image = None
	column_tiles = []

	tile_count = len(tiles)
	for tile_index, tile_data in tiles.items():
		i += 1
		column_width = max(column_width, len(tile_data['palettes']) * (thumb_size + thumb_spacing) + thumb_spacing + col_spacing)
		column_tiles.append((tile_index, tile_data))

		if i % num_rows == 0 or i == tile_count:
			column_image = Image.new('RGBA', (column_width, num_rows * (thumb_size + row_title_height + row_spacing) + padding_top), (0, 0, 0, 255))
			draw = ImageDraw.Draw(column_image)

			y = row_title_height + padding_top
			for col_tile_index, col_tile_data in column_tiles:
				tile_name = col_tile_data['name']
				# print(col_tile_index, col_tile_data)
				x = thumb_spacing
				tile_title = '%s [%i]' % (tile_name, col_tile_index)
				draw.text((x - 10, y - row_title_height), tile_title, (255, 255, 255), font=title_font)
				for palette_index, palette_name in col_tile_data['palettes'].items():
					thumb = Image.open('%s/%s %s%s.png' % (thumb_dir, set_name, tile_name, palette_name))
					# column_image.paste(thumb, (x, y))
					draw_with_alpha(column_image, thumb, x, y)

					palette_text = '%s [%i]' % (palette_name[1:], palette_index)
					w, h = draw.textsize(palette_text, font=font)
					draw.text((x + (thumb_size - w) / 2, y + thumb_size + 7 - h / 2), palette_text, (200, 200, 200), font=font)

					x += thumb_size + thumb_spacing

					pass
				pass

				y += thumb_size + row_spacing + row_title_height

			column_tiles = []
			column_width = 0

			if set_image is None:
				set_image = column_image
			else:
				new_image = Image.new('RGBA', (set_image.width + column_image.width, set_image.height), (0, 0, 0, 0))
				new_image.paste(set_image, (0, 0))
				new_image.paste(column_image, (set_image.width, 0))
				set_image = new_image

	if set_image is not None:
		set_image.save('%s/%i-%s.png' % (out_dir, set_index, set_name), quality=quality, optimize=True, progressive=True)
		pass

	# for i in range(num_cols):
	# 	pass
