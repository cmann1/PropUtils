import os
import math

from PIL import Image, ImageFont, ImageDraw

# Some settings

sprite_dir = 'sprites'
out_dir = 'files/name_sheets'
thumb_size = 72
font_size = 12
quality = 90
padding = 20
section_size = thumb_size + padding * 2
section_mid = section_size / 2

# Get sprites by group

sprites = os.listdir(sprite_dir)
sprite_groups = dict()
for sprite_file in sprites:
	sprite_array = sprite_file[:-4].split('_', 4)
	group_name = sprite_array[0]
	prop_set = int(sprite_array[1])
	group_index = int(sprite_array[2])
	prop_index = int(sprite_array[3])
	prop_name = sprite_array[4]

	if group_name not in sprite_groups:
		group = sprite_groups[group_name] = []
	else:
		group = sprite_groups[group_name]

	# group.append(prop_name)
	group.append((prop_name, sprite_file))
	# print(group_name, prop_set, group_index, prop_index, prop_name)

# Render

for group_name, sprites in sprite_groups.items():
	sorted_sprites = sorted(sprites, key=lambda item: (int(item[0].partition(' ')[0]) if item[0][0].isdigit() else float('inf'), item))
	count = len(sorted_sprites)
	num_cols = math.ceil(math.sqrt(count))
	num_rows = math.ceil(count / num_cols)

	col_size = section_size

	sheet_image = Image.new('RGBA', (1, 1), (0, 0, 0))
	font = ImageFont.truetype('files/DejaVuSans.ttf', font_size)
	draw = ImageDraw.Draw(sheet_image)

	for name, file in sorted_sprites:
		w, h = draw.textsize(name, font=font)
		if w > col_size:
			col_size = w

	size = (col_size * num_cols, section_size * num_rows)
	sheet_image = Image.new('RGBA', size, (0, 0, 0))

	composite_image = Image.new('RGBA', size, (0, 0, 0, 0))
	composite_draw = ImageDraw.Draw(composite_image)

	pad_x = int((col_size - thumb_size) / 2)
	pad_y = padding
	col = 0
	row = 0
	for name, file in sorted_sprites:
		x = col * col_size + pad_x
		y = row * section_size + pad_y
		thumb = Image.open(sprite_dir + '/' + file)
		thumb.thumbnail((thumb_size, thumb_size))
		if thumb.size[0] != thumb_size or thumb.size[1] != thumb_size:
			new_image = Image.new('RGBA', (thumb_size, thumb_size), 0x000000)
			new_image.paste(thumb, (int((thumb_size - thumb.size[0]) / 2), int((thumb_size - thumb.size[1]) / 2)))
			thumb = new_image

		composite_image.paste(thumb, (x, y))

		# sheet_image.paste(thumb, (x, y))
		sheet_image = Image.alpha_composite(sheet_image, composite_image)
		draw = ImageDraw.Draw(sheet_image)
		w, h = draw.textsize(name, font=font)
		draw.text((x + (thumb_size - w) / 2, y + thumb_size - h + padding / 2), name, (255, 255, 255), font=font)

		composite_draw.rectangle(((0, 0), size), (0, 0, 0, 0))

		col += 1
		if col == num_cols:
			col = 0
			row += 1

	# sheet_image.save('%s/%s.png' % (out_dir, group_name), optimize=True, compress_level=9)
	sheet_image.save('%s/%s.jpg' % (out_dir, group_name), quality=quality, optimize=True, progressive=True)
