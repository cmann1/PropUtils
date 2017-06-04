class Sprite:
	def __init__(self, prop_set=-1):
		self.prefix = ''
		self.index = -1
		self.group_name = ''
		self.group_index = -1
		self.prop_set = prop_set
		self.frame_count = 0
		self.palette_count = 0
		self.frame_count = 0
		self.frames = []
		self.chunks = []
