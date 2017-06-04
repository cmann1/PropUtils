class Rectangle:
	def __init__(self, left=0, top=0, right=0, bottom=0):
		self.left = left
		self.top = top
		self.right = right
		self.bottom = bottom

	def set(self, left=0, top=0, right=0, bottom=0):
		self.left = left
		self.top = top
		self.right = right
		self.bottom = bottom

	def width(self):
		return self.right - self.left

	def height(self):
		return self.bottom - self.top

	def __repr__(self):
		return '[%i, %i, %i, %i] [%i, %i]' % (self.left, self.top, self.right, self.bottom, self.width(), self.height())
