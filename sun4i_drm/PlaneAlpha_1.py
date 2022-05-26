#!/usr/bin/python3

import pykms
import time

card = pykms.Card()
res = pykms.ResourceManager(card)
conn = res.reserve_connector('')
crtc = res.reserve_crtc(conn)

format = pykms.PixelFormat.XRGB8888
magenta = pykms.RGB(255, 0, 255)

card.disable_planes()

mode = conn.get_default_mode()
modeb = mode.to_blob(card)
req = pykms.AtomicReq(card)
req.add(conn, "CRTC_ID", crtc.id)
req.add(crtc, {"ACTIVE": 1,
               "MODE_ID": modeb.id})
r = req.commit_sync(allow_modeset = True)
assert r == 0, "Initial commit failed: %d" % r

fbX = 1920
fbY = 1080

fbX_2 = 640
fbY_2 = 480

planes=[]

max_planes=16

for i in range(max_planes):
    p = res.reserve_generic_plane(crtc)
    if p == None:
        break
    planes.append(p)

fb = pykms.DumbFramebuffer(card, fbX, fbY, format);
pykms.draw_rect(fb, int(fbX*0.1), int(fbY*0.1), int(fbX*0.8), int(fbY*0.8), magenta)

def PlaneAlphaTest(plane_index):
	print("Testing plane {}".format(plane_index))
	toggle = True
	req = pykms.AtomicReq(card)

	r = req.commit_sync()

	for i in range(0, 255, 3):
		req = pykms.AtomicReq(card)

		

		r = req.commit_sync()
		assert r == 0, "Plane commit failed: %d" % r

	card.disable_planes()

for i in range(0, len(planes)):
	PlaneAlphaTest(i)
