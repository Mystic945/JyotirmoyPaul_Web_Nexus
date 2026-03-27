import asyncio, json, time
from bleak import BleakClient

BAND_ADDRESS = "74:19:0A:2F:55:12"
CHAR_UUID    = "8ac32d3f-5cb9-4d44-bec2-ee689169f626"

# Set time to 4:44 AM today so we know if it worked
def make_time_packet():
    # Build epoch for today at 4:44:00 AM IST
    import datetime
    now = datetime.datetime.now()
    target = now.replace(hour=4, minute=44, second=0, microsecond=0)
    epoch_ms = int(target.timestamp() * 1000)

    payload = json.dumps({
        "msgType": "MSG_RTC_INFO_SET",
        "data": {
            "PARAM_RTC_INFO_EPOCH_TIME":  epoch_ms,
            "PARAM_RTC_INFO_TIME_ZONE":   "Asia/Kolkata",
            "PARAM_RTC_INFO_LOCALE":      "en_IN",
            "PARAM_RTC_INFO_IS_ROAMING":  False,
            "RTC_INFO_IS_24_HOUR_FORMAT": True,
        }
    }).encode()
    return payload, epoch_ms

async def main():
    print("Galaxy Fit 3 - Set Time to 4:44")
    print(f"Band: {BAND_ADDRESS}\n")

    responses = []
    def on_notify(sender, data):
        responses.append(data)
        print(f"  RESPONSE: {data.hex()}")

    async with BleakClient(BAND_ADDRESS, timeout=20.0) as client:
        print(f"Connected!\n")

        # Subscribe first
        for uuid in [
            "8ac32d3f-5cb9-4d44-bec2-ee689169f626",
            "4af351bb-d6f7-4612-a8e3-8dce6ca13e7b",
            "853bd048-b043-4dcd-b073-de49569e1194",
            "66aeea2f-1edf-445b-bcfb-7ef330268073",
            "797ae4e9-2e58-4fe8-b48d-b5c79599fb9b",
        ]:
            try:
                await client.start_notify(uuid, on_notify)
                print(f"Listening on {uuid[:8]}")
            except Exception as e:
                print(f"Skip {uuid[:8]}: {e}")

        print()
        pkt, epoch_ms = make_time_packet()
        print(f"Sending: time = 4:44 AM (epoch {epoch_ms})")
        print(f"Packet size: {len(pkt)} bytes\n")

        # Try all writable UUIDs
        for wuuid in [
            "8ac32d3f-5cb9-4d44-bec2-ee689169f626",
            "4af351bb-d6f7-4612-a8e3-8dce6ca13e7b",
            "853bd048-b043-4dcd-b073-de49569e1194",
            "66aeea2f-1edf-445b-bcfb-7ef330268073",
            "63e30bad-4206-4596-839f-e47cbf7a4b5d",
        ]:
            try:
                await client.write_gatt_char(wuuid, pkt, response=False)
                print(f"OK (no-response write): {wuuid[:8]}")
            except Exception as e:
                print(f"FAIL {wuuid[:8]}: {e}")

            try:
                await client.write_gatt_char(wuuid, pkt, response=True)
                print(f"OK (response write):    {wuuid[:8]}")
            except Exception as e:
                print(f"FAIL {wuuid[:8]}: {e}")

        print("\nWaiting 5 seconds for response...")
        await asyncio.sleep(5)

    print("\nDid time on band change to 4:44?")
    if responses:
        print(f"Band sent {len(responses)} response(s)!")
        for r in responses:
            print(f"  {r.hex()}")

asyncio.run(main())
