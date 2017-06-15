import json
import os
import math
import pickle
import random

import SpriteExtractor
import dustmaker
from PropUtils import PropUtils, Pivot, rad_to_int


def read_prop_origins(prop_utils, map_file_location, map_file, grid_size=8, grid_factor=0.75):
	data = prop_utils.prop_data

	with open(map_file_location + map_file, 'rb') as f:
		map = dustmaker.read_map(f.read())

	half_grid = grid_size * grid_factor

	for id, value in map.props.items():
		layer, x, y, prop = value

		prop_data = prop_utils.get_prop_data(prop)
		frame_data = prop_data['palettes'][0][0]
		centre = prop_utils.get_prop_location(x, y, prop, Pivot.CENTRE, prop_data)

		grid_x = math.floor((centre[0] + half_grid) / grid_size) * grid_size
		grid_y = math.floor((centre[1] + half_grid) / grid_size) * grid_size

		top_left = prop_utils.get_prop_location(x, y, prop, Pivot.TOP_LEFT, prop_data)
		prop_data['origin'] = (abs(top_left[0] - grid_x) / frame_data['w'], abs(top_left[1] - grid_y) / frame_data['h'])

		pass

	return map_file_location, map_file, map, grid_size, grid_factor

	pass


def place_test_props(prop_utils, map_data, test_get=True, test_set=False, test_grid=False, test_placement=False, test_place_flipped=False):
	map_file_location, map_file, map, grid_size, grid_factor = map_data

	test_tile = None
	tile_offset = [(-1, -1, 13), (0, -1, 12), (-1, 0, 12), (0, 0, 13)]
	sample_tile_layer = 13

	props = []
	arrows = []

	if test_get:
		marker1_data = prop_utils.name_prop_map['foliage stain_small']
		m1_data = marker1_data['palettes'][0][0]
		m1o = (m1_data['x'], m1_data['y'])
		m1f = (m1_data['w'], m1_data['h'])
		marker2_data = prop_utils.name_prop_map['machinery light_small']
		m2_data = marker2_data['palettes'][0][0]
		m2o = (m2_data['x'], m2_data['y'])
		m2f = (m2_data['w'], m2_data['h'])
		marker3_data = prop_utils.name_prop_map['symbol arrow']
		m3p = Pivot.RIGHT

		half_grid = grid_size * grid_factor

		for id, value in map.props.items():
			layer, x, y, prop = value
			prop_data = prop_utils.get_prop_data(prop)

			if PropUtils.equals(prop, marker3_data):
				arrows.append((layer, x, y, prop, prop_data))
				continue

			for pivot in [Pivot.TOP_LEFT, Pivot.TOP, Pivot.TOP_RIGHT, Pivot.RIGHT, Pivot.BOTTOM_RIGHT, Pivot.BOTTOM, Pivot.BOTTOM_LEFT, Pivot.LEFT, Pivot.CENTRE]:
				p = prop_utils.get_prop_location(x, y, prop, pivot, prop_data)

				if pivot == Pivot.TOP_LEFT:
					marker_data = marker1_data
					mo = m1o
					mf = m1f
				else:
					marker_data = marker2_data
					mo = m2o
					mf = m2f
				# marker_prop = dustmaker.Prop(19, 0, True, True, 1, marker_data['set_index'], marker_data['group_index'], marker_data['sprite_index'], 0)
				# props.append((20, grid_x - mo[0] - mf[0] / 2, grid_y - mo[1] - mf[1] / 2, marker))
				# props.append((20, p[0] - mo[0] - mf[0] / 2, p[1] - mo[1] - mf[1] / 2, marker_prop))
				marker_prop = PropUtils.from_data(marker_data)
				marker_prop.scale = 0.2
				marker_x, marker_y = prop_utils.set_prop_location(p[0], p[1], marker_prop, Pivot.CENTRE, marker_data)
				props.append((20, marker_x, marker_y, marker_prop))

			if test_grid:
				centre = prop_utils.get_prop_location(x, y, prop, Pivot.CENTRE, prop_data)
				grid_x = math.floor((centre[0] + half_grid) / grid_size) * grid_size
				grid_y = math.floor((centre[1] + half_grid) / grid_size) * grid_size
				marker_prop = dustmaker.Prop(19, 0, True, True, 1, marker3_data['set_index'], marker3_data['group_index'], marker3_data['sprite_index'], 0)
				marker_prop.scale = 0.5
				p = prop_utils.set_prop_location(grid_x, grid_y, marker_prop, m3p, marker3_data)
				props.append((20, p[0], p[1], marker_prop))

			pass

	if test_set:
		# props_to_place = [
		# 	prop_utils.name_prop_map['decoration bust'],
		# 	prop_utils.name_prop_map['backdrops building_small'],
		# 	prop_utils.name_prop_map['lighting torch-side']
		# ]
		# index = 0
		for layer, x, y, prop, prop_data in arrows:
			next_prop_data = prop_utils.name_prop_map[random.choice(list(prop_utils.name_prop_map))]
			# next_prop_data = props_to_place[index % len(props_to_place)]

			pos_x, pos_y = prop_utils.get_prop_location(x, y, prop, Pivot.RIGHT, prop_data)

			for i in range(4):
				prop = PropUtils.from_data(next_prop_data, 19, int(0xffff * (i / 6)))
				x, y = prop_utils.set_prop_location(pos_x, pos_y, prop, Pivot.ATTACHMENT, next_prop_data)
				props.append((layer - 1, x, y, prop))

			# index += 1
			pass
		pass

	if test_placement:
		for id, tile in map.tiles.items():
			layer, x, y = id
			if layer == sample_tile_layer:
				test_tile = tile
				break

		start_y = -10
		start_x = -130
		y = start_y
		gap = 10

		if test_place_flipped:
			flip_list = [(True, True), (True, False), (False, True), (False, False)]
		else:
			flip_list = [(True, True)]

		scales = [0.5, 1, 1.5]
		if not prop_utils.use_scale:
			scales = [1]

		props_list = prop_utils.name_prop_map
		# props_list = ['books stack_1', 'books stack_3', 'foliage flower_red', 'furniture freeman', 'lighting forest_lamp']
		# props_list = ['books stack_1']
		# props_list = ['lighting city_lamp_standing']
		# props_list = ['buildingblocks wooden_pole']

		pivots = [Pivot.TOP_LEFT, Pivot.TOP, Pivot.TOP_RIGHT, Pivot.RIGHT, Pivot.BOTTOM_RIGHT, Pivot.BOTTOM, Pivot.BOTTOM_LEFT, Pivot.CENTRE, Pivot.ATTACHMENT]
		# pivots = [Pivot.ATTACHMENT, Pivot.CENTRE]

		for prop_name in props_list:
			x = start_x

			for pivot in pivots:
				test_prop_data = prop_utils.name_prop_map[prop_name]
				num_props = 10
				rotate_range = 360 / 180 * math.pi
				for flip_x, flip_y in flip_list:
					for i in range(num_props):
						angle = i / num_props * rotate_range

						for scale in scales:
							test_prop = PropUtils.from_data(test_prop_data, 19, rad_to_int(angle), flip_x, flip_y, 0)

							if prop_utils.use_scale:
								test_prop.scale = scale

							p = prop_utils.set_prop_location(x, y, test_prop, pivot)
							props.append((16, p[0], p[1], test_prop))

							if test_tile is not None:
								for o_x, o_y, layer in tile_offset:
									tile_x = x + o_x
									tile_y = y + o_y
									if (layer, tile_x, tile_y) not in map.tiles:
										map.add_tile(layer, tile_x, tile_y, test_tile)

							x += gap
							pass

						pass
					x += gap

				x += gap
				pass

			y -= gap
			pass
		# END for prop_name

	for layer, x, y, prop in props:
		map.add_prop(layer, x, y, prop)
		pass

	map.name(map.name() + '2')
	with open(map_file_location + map_file + '2', 'wb') as f:
		f.write(dustmaker.write_map(map))

	pass  # END func


map_file_location = os.getenv('APPDATA') + '/Dustforce/user/level_src/'
map_file = 'PropOrigins'
grid_size = 8
grid_factor = 0.75

prop_utils = PropUtils('sprite-data', True, True)

## Read and save custom attachment points from the map
# map_data = read_prop_origins(prop_utils, map_file_location, map_file, grid_size, grid_factor)

# with open(prop_utils.data_file, 'wb') as f:
# 	pickle.dump(prop_utils.prop_data, f)
# with open('sprite-data.json', 'w') as f:
# 	json.dump(prop_utils.prop_data, f, indent='\t')

## Run some tests to make sure it works
##
with open(map_file_location + map_file, 'rb') as f:
	map = dustmaker.read_map(f.read())
map_data = (map_file_location, map_file, map, grid_size, grid_factor)
place_test_props(prop_utils, map_data, True, True, True, False)
