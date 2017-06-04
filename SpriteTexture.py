class SpriteTexture:
	def __init__(self, name, unk1, unk2):
		self.set_name = name
		self.unk1 = unk1
		self.unk2 = unk2
		self.path = '%s_%02X_%02X.png' % (name, unk1, unk2)
		self.image = None
		pass
