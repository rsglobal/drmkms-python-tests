#!/usr/bin/python3

import pykms
import time

card = pykms.Card()
res = pykms.ResourceManager(card)
conn = res.reserve_connector('')
crtc = res.reserve_crtc(conn)

format = pykms.PixelFormat.ARGB8888

card.disable_planes()

mode = conn.get_default_mode()
modeb = mode.to_blob(card)
req = pykms.AtomicReq(card)
req.add(conn, "CRTC_ID", crtc.id)
req.add(crtc, {"ACTIVE": 1,
               "MODE_ID": modeb.id})
r = req.commit_sync(allow_modeset = True)
assert r == 0, "Initial commit failed: %d" % r

fbX = mode.hdisplay
fbY = 10

black = pykms.RGB(0, 0, 0)
red = pykms.RGB(255, 0, 0)
green = pykms.RGB(0, 255, 0)
white = pykms.RGB(255, 255, 255)

fb=[]

stripe_size=10
num_stripes = int(mode.hdisplay/stripe_size)

for i in range (0, num_stripes):
	fb.append(pykms.DumbFramebuffer(card, fbX, fbY, format));
	pykms.draw_rect(fb[i], 0, 0, fbX, fbY, black)
	pykms.draw_rect(fb[i], i*10, 0, 10, fbY, white)

planes=[]

planes.append(res.reserve_generic_plane(crtc, format))
planes.append(res.reserve_generic_plane(crtc, format))
planes.append(res.reserve_generic_plane(crtc, format))
planes.append(res.reserve_generic_plane(crtc, format))

assert len(planes)>=4, "at least 4 planes required, got %d" % len(planes)

red_fb = pykms.DumbFramebuffer(card, fbX, fbY, format);
pykms.draw_rect(red_fb, 0, 0, fbX, fbY, red)

green_fb = pykms.DumbFramebuffer(card, fbX, fbY, format);
pykms.draw_rect(green_fb, 0, 0, fbX, fbY, green)

mdst = (0, 0, mode.hdisplay, mode.vdisplay)

zpos = 0
fb_ind = 0
toggle=1

while True:
	req = pykms.AtomicReq(card)

	req.add_plane(planes[0], green_fb, crtc, dst=mdst, zpos=0)
	if toggle:
		req.add_plane(planes[1], red_fb, crtc, dst=mdst, zpos=1)
		req.add_plane(planes[1], None, None, zpos=1)
	else:
		req.add_plane(planes[2], red_fb, crtc, dst=mdst, zpos=1)
		req.add_plane(planes[2], None, None, zpos=1)

	req.add_plane(planes[3], fb[fb_ind], crtc, dst=mdst, zpos=2)

	r = req.commit_sync()
	assert r == 0, "Plane commit failed: %d" % r

	zpos = zpos + 1
	if zpos >= 3:
		zpos = 0

	toggle = not toggle

	fb_ind = (fb_ind + 1) % len(fb)
