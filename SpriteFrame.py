from Rectangle import Rectangle


class SpriteFrame:
	def __init__(self, index, palette):
		self.field0 = 0
		self.field4 = 0
		self.field28 = 0
		self.rect1 = Rectangle()
		self.rect2 = Rectangle()
		self.chunk_count = 0
		self.chunks_offset = 0
		self.palette = palette
		self.index = index
