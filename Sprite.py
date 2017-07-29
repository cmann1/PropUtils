class Sprite:
	def __init__(self, sprite_set_name, prop_set=-1):
		self.sprite_set_name = sprite_set_name
		self.prefix = ''
		self.index = -1
		self.group_name = ''
		self.group_index = -1
		self.prop_set = prop_set
		self.frame_count = 0
		self.palette_count = 0
		self.frames = []
		self.chunks = []
