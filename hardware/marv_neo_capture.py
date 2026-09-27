import asyncio
from bleak import BleakClient


ADDRESS = "F7:64:1C:18:04:39"

FEE3 = "0000fee3-0000-1000-8000-00805f9b34fb"

HEART_RATE = "00002a37-0000-1000-8000-00805f9b34fb"


def fee3_handler(sender, data):

    raw = bytes(data)

    print()
    print("=" * 70)
    print("FEE3 DATA")
    print("=" * 70)
    print("HEX:", raw.hex(" "))
    print("DEC:", list(raw))
    print("=" * 70)


def heart_rate_handler(sender, data):

    raw = bytes(data)

    if len(raw) < 2:
        return

    flags = raw[0]

    if flags & 0x01:

        if len(raw) < 3:
            return

        value = int.from_bytes(
            raw[1:3],
            byteorder="little"
        )

    else:

        value = raw[1]

    print()
    print("HEART RATE:", value, "BPM")


async def main():

    print("=" * 70)
    print("MARV NEO HEALTH DATA CAPTURE")
    print("=" * 70)

    print()
    print("Connecting to:")
    print(ADDRESS)

    async with BleakClient(ADDRESS) as client:

        if not client.is_connected:

            print("Connection failed.")
            return

        print()
        print("MARV NEO CONNECTED")
        print()

        await client.start_notify(
            FEE3,
            fee3_handler
        )

        await client.start_notify(
            HEART_RATE,
            heart_rate_handler
        )

        print("BLE notifications enabled.")

        print()
        print("=" * 70)
        print("CAPTURE STARTED")
        print("=" * 70)

        print()
        print("Do these measurements manually on the watch:")
        print()
        print("1. Measure HEART RATE")
        print("2. Measure SpO2")
        print("3. Measure BLOOD PRESSURE")
        print()
        print("Wait for each measurement to finish.")
        print()
        print("Keep the watch connected.")
        print("Press CTRL+C when finished.")
        print()

        while True:

            await asyncio.sleep(1)


if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print()
        print("Capture stopped.")