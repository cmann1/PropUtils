import os
import math
import pickle

from PIL import Image, ImageFont, ImageDraw

from DrawWithAlpha import draw_with_alpha

sprite_dir = 'reference_sprites'
out_dir = 'files/sprite_reference'
thumb_size = 72
font_size = 12
quality = 90
padding = 30
section_size = thumb_size + padding * 2


if not os.path.exists(out_dir):
	os.makedirs(out_dir)
	pass

with open('sprites-reference-data', 'rb') as f:
	sprite_data = pickle.load(f)

frame_indices = dict(
	fonts=dict(
		Caracteres=72,
		ProximaNovaReg=74,
		ProximaNovaThin=74,
		envy_bold=72,
		sans_bold=72
	),
	tile=dict(

	)
)

total_count = 0
for sprite_set, set_data in sprite_data.items():
	print(sprite_set)
	sorted_sprites = []
	for sprite_name, sprite_data in set_data.items():
		sorted_sprites.append((sprite_name, sprite_data))
	sorted_sprites = sorted(sorted_sprites, key=lambda item: (int(item[0].partition(' ')[0]) if item[0][0].isdigit() else float('inf'), item))

	if len(sorted_sprites) == 0:
		continue

	sorted_sprites = sorted_sprites[0:50]
	count = len(sorted_sprites)
	total_count += count
	num_cols = math.ceil(math.sqrt(count))
	num_rows = math.ceil(count / num_cols)

	col_size = section_size

	sheet_image = Image.new('RGBA', (1, 1), (0, 0, 0))
	font = ImageFont.truetype('files/DejaVuSans.ttf', font_size)
	draw = ImageDraw.Draw(sheet_image)

	for sprite_name, sprite_data in sorted_sprites:
		w, h = draw.textsize(sprite_name, font=font)
		if w > col_size:
			col_size = w
		pass

	size = (col_size * num_cols, section_size * num_rows + 15)
	sheet_image = Image.new('RGBA', size, (0, 0, 0))

	pad_x = int((col_size - thumb_size) / 2)
	pad_y = padding
	col = 0
	row = 0
	for sprite_name, sprite_data in sorted_sprites:
		x = col * col_size + pad_x
		y = row * section_size + pad_y

		# print('   '+sprite_name)

		frame_index = 1
		if sprite_set[0:4] == 'tile':
			if sprite_name == 'filth' or sprite_name == 'spikes':
				frame_index = 2
		elif sprite_set in frame_indices:
			set_indices = frame_indices[sprite_set]
			f = sprite_name
			if f not in set_indices:
				f = f.rpartition('_')[0]

			if f in set_indices:
				frame_index = set_indices[f]

		path = '{}/{}/{}-1-{:04d}.png'.format(sprite_dir, sprite_set, sprite_name, frame_index)
		if not os.path.exists(path):
			print('  Skipping ' + path)
			continue

		thumb = Image.open(path)
		thumb.thumbnail((thumb_size, thumb_size))
		if thumb.size[0] != thumb_size or thumb.size[1] != thumb_size:
			new_image = Image.new('RGBA', (thumb_size, thumb_size), 0x000000)
			new_image.paste(thumb, (int((thumb_size - thumb.size[0]) / 2), int((thumb_size - thumb.size[1]) / 2)))
			thumb = new_image

		draw_with_alpha(sheet_image, thumb, x, y)

		draw = ImageDraw.Draw(sheet_image)
		w, h = draw.textsize(sprite_name, font=font)
		draw.text((x + (thumb_size - w) / 2, y + thumb_size - h + padding / 2), sprite_name, (255, 255, 255), font=font)

		data = sprite_data['sprites'][-1]
		info_text = 'p:{} f:{}'.format(data['palette_count'], data['frame_count'])
		w, h = draw.textsize(info_text, font=font)
		draw.text((x + (thumb_size - w) / 2, y + thumb_size + padding / 2 + 5), info_text, (255, 255, 255), font=font)

		col += 1
		if col == num_cols:
			col = 0
			row += 1

		pass

	sheet_image.save('%s/%s.png' % (out_dir, sprite_set), quality=quality, optimize=True, progressive=True)

	# if total_count >= 50:
	# 	break

	pass
