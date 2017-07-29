from PIL import Image


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
