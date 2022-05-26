#!/usr/bin/python3

import pykms
import time

card = pykms.Card()
res = pykms.ResourceManager(card)
conn = res.reserve_connector('')
crtc = res.reserve_crtc(conn)

format = pykms.PixelFormat.XRGB8888
green = pykms.RGB(0, 255, 0)

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
fbY = mode.vdisplay

fb_full = pykms.DumbFramebuffer(card, fbX, fbY, format);
pykms.draw_rect(fb_full, int(fbX*0.1), int(fbY*0.1), int(fbX*0.8), int(fbY*0.8), green)

fbX = int(fbX/2)
fbY = int(fbY/2)

fb_half = pykms.DumbFramebuffer(card, fbX, fbY, format);
pykms.draw_rect(fb_half, int(fbX*0.1), int(fbY*0.1), int(fbX*0.8), int(fbY*0.8), green)

planes=[]

max_planes=16

frame_time = 1 / mode.vrefresh
commit_point = frame_time * 0.5

for i in range(max_planes):
    p = res.reserve_generic_plane(crtc)
    if p == None:
        break
    planes.append(p)

def PlaneAlphaTest(plane_index):
	card.disable_planes()
	print("Testing plane {}".format(plane_index))
	for i in range(0, 60):
		time.sleep(commit_point)

		req = pykms.AtomicReq(card)
		req.add_plane(planes[plane_index], fb_full if i%2 else fb_half, crtc, dst=(0, 0, 1920, 1080), zpos=0)
		r = req.commit_sync()
		assert r == 0, "Plane commit failed: %d" % r

print(
"""
	Green rectangle scaling test
	Rectangle must appear on the screen without visible artifacts
	It's ok to see slightly smoothed edges.
""")

for i in range(0, len(planes)):
	PlaneAlphaTest(i)
