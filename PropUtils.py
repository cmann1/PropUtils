import math
import pickle

import dustmaker


def rotate(origin_x, origin_y, point_x, point_y, angle):
	"""
	Rotate a point counterclockwise by a given angle around a given origin.

	The angle should be given in radians.
	"""

	qx = origin_x + math.cos(angle) * (point_x - origin_x) - math.sin(angle) * (point_y - origin_y)
	qy = origin_y + math.sin(angle) * (point_x - origin_x) + math.cos(angle) * (point_y - origin_y)
	return qx, qy


def int_to_rad(angle):
	return angle / 65536.0 * 2 * math.pi


def rad_to_int(angle):
	return int(65536 * ((angle % (math.pi * 2)) / 2 / math.pi))


def get_prop_scale(scale):
	scale_lg = int(round(math.log(scale) / math.log(50.0) * 24.0)) + 32
	x_scale = (scale_lg // 7) ^ 0x4
	y_scale = (scale_lg % 7) ^ 0x4
	x_scale = (x_scale & 0x7) ^ 0x4
	y_scale = (y_scale & 0x7) ^ 0x4
	scale_lg = x_scale * 7 + y_scale
	return pow(50.0, (scale_lg - 32.0) / 24.0)


class Pivot:
	TOP_LEFT = (0, 0)
	TOP = (0.5, 0)
	TOP_RIGHT = (1, 0)
	RIGHT = (1, 0.5)
	BOTTOM_RIGHT = (1, 1)
	BOTTOM = (0.5, 1)
	BOTTOM_LEFT = (0, 1)
	LEFT = (0, 0.5)
	CENTRE = (0.5, 0.5)
	ATTACHMENT = 0
	pass


class PropUtils:
	def __init__(self, data_file='sprite-data', use_scale=False, use_pixel_bounds=True):
		with open(data_file, 'rb') as f:
			self.prop_data = pickle.load(f)

		self.name_prop_map = name_prop_map = {}
		for set_index, sprite_set in self.prop_data.items():
			for group_index, sprite_group in sprite_set.items():
				group_name = sprite_group['name']
				for sprite_index, sprite in sprite_group['sprites'].items():
					name_prop_map[group_name + ' ' + sprite['name']] = sprite
					pass
				pass
			pass

		self.data_file = data_file
		self.use_scale = use_scale
		self.use_pixel_bounds = use_pixel_bounds
		pass

	def get_prop_data(self, prop):
		return self.prop_data[prop.prop_set][prop.prop_group]['sprites'][prop.prop_index]

	def get_prop_offset(self, prop, pivot=Pivot.CENTRE, prop_data=None):
		if prop_data is None:
			prop_data = self.get_prop_data(prop)

		frame_data = prop_data['palettes'][0][0]

		if pivot == Pivot.ATTACHMENT:
			if 'origin' in prop_data:
				pivot = prop_data['origin']
			else:
				pivot = (0.5, 0.5)
		elif self.use_pixel_bounds:
			x, y, w, h = prop_data['bbox']
			pivot = (
				x + pivot[0] * w,
				y + pivot[1] * h,
			)
			pass

		x = frame_data['x']
		y = frame_data['y']
		w = frame_data['w']
		h = frame_data['h']
		dx = w * pivot[0]
		dy = h * pivot[1]
		flip_x = 1 if prop.flip_x else -1
		flip_y = 1 if prop.flip_y else -1

		if self.use_scale:
			scale = get_prop_scale(prop.scale)
			flip_x *= scale
			flip_y *= scale

		return rotate(0, 0, (x + dx) * flip_x, (y + dy) * flip_y, int_to_rad(prop.rotation))
		pass

	def get_prop_location(self, x, y, prop, pivot=Pivot.CENTRE, prop_data=None):
		offset_x, offset_y = self.get_prop_offset(prop, pivot, prop_data)
		return x + offset_x, y + offset_y
		pass

	def set_prop_location(self, x, y, prop, pivot=Pivot.CENTRE, prop_data=None):
		offset_x, offset_y = self.get_prop_offset(prop, pivot, prop_data)
		return x - offset_x, y - offset_y
		pass

	@staticmethod
	def equals(prop, prop_data):
		return prop.prop_set == prop_data['set_index'] and\
		       prop.prop_group == prop_data['group_index'] and\
		       prop.prop_index == prop_data['sprite_index']

	@staticmethod
	def from_data(prop_data, layer_sub=19, rotation=0, flip_x=True, flip_y=True, palette=0, scale=1):
		return dustmaker.Prop(layer_sub, rotation, flip_x, flip_y, scale,
			prop_data['set_index'],
			prop_data['group_index'],
			prop_data['sprite_index'],
			palette
		)
		pass
