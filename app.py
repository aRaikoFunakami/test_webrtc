import asyncio
import os
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription

ROOT = os.path.dirname(__file__)
pcs = set()

async def index(request):
    return web.FileResponse(os.path.join(ROOT, "static/client.html"))

async def offer(request):
    params = await request.json()
    print("✅ SDP Offer 受信")
    # 必要ならSDP全文出力
    # print(params["sdp"])

    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("track")
    def on_track(track):
        print(f"✅ Audio track received: {track.kind}")
        if track.kind == "audio":
            # そのままループバック
            pc.addTrack(track)
            print("✅ Audio track loopback 完了")

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    print("✅ Answer生成 完了")

    return web.json_response({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})

async def on_shutdown(app):
    print("✅ サーバーシャットダウン")
    for pc in pcs:
        await pc.close()
    pcs.clear()

app = web.Application()
app.on_shutdown.append(on_shutdown)
app.router.add_get("/", index)
app.router.add_post("/offer", offer)
app.router.add_static("/static/", os.path.join(ROOT, "static"))

if __name__ == "__main__":
    print("✅ WebRTC Echo Server起動 (ループバックモード)")
    web.run_app(app, port=8080)
