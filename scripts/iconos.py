from PIL import Image, ImageDraw

for n in (180, 192, 512):
    im = Image.new("RGB", (n, n), "#0b1f33")
    d = ImageDraw.Draw(im)
    m = n * 0.14
    d.ellipse([m, m, n - m, n - m], fill="#16a34a")
    s = n / 100
    rayo = [(55, 22), (33, 55), (48, 55), (42, 80), (67, 43), (52, 43), (58, 22)]
    d.polygon([(x * s, y * s) for x, y in rayo], fill="#ffffff")
    im.save("icon-%d.png" % n)
