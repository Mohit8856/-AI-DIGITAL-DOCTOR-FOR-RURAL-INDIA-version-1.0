import asyncio
from bleak import BleakClient


ADDRESS = "F7:64:1C:18:04:39"

FEE2 = "0000fee2-0000-1000-8000-00805f9b34fb"
FEE3 = "0000fee3-0000-1000-8000-00805f9b34fb"
HEART_RATE = "00002a37-0000-1000-8000-00805f9b34fb"


def fee3_handler(sender, data):

    raw = bytes(data)

    print()
    print("FEE3")
    print("HEX:", raw.hex(" "))
    print("DEC:", list(raw))


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


async def send_packet(client, packet, name):

    print()
    print("=" * 60)
    print(name)
    print("=" * 60)
    print("SEND:", packet.hex(" "))

    await client.write_gatt_char(
        FEE2,
        packet,
        response=False
    )

    await asyncio.sleep(5)


async def main():

    print("=" * 60)
    print("MARV NEO MEASUREMENT TEST")
    print("=" * 60)

    async with BleakClient(ADDRESS) as client:

        if not client.is_connected:
            print("Connection failed.")
            return

        print()
        print("MARV NEO CONNECTED")

        await client.start_notify(
            FEE3,
            fee3_handler
        )

        await client.start_notify(
            HEART_RATE,
            heart_rate_handler
        )

        await asyncio.sleep(2)

        await send_packet(
            client,
            bytes.fromhex("FE EA 10 06 6B 00"),
            "SPO2 START"
        )

        print()
        print("Measure SpO2 on the watch now.")
        print("Wait until the watch displays the result.")

        await asyncio.sleep(10)

        await send_packet(
            client,
            bytes.fromhex("FE EA 10 06 68 00"),
            "BLOOD PRESSURE START"
        )

        print()
        print("Measure Blood Pressure on the watch now.")
        print("Wait until the watch displays the result.")

        await asyncio.sleep(10)

        await send_packet(
            client,
            bytes.fromhex("FE EA 10 06 6F 00"),
            "ONE-TIME HEART RATE"
        )

        await asyncio.sleep(5)

        print()
        print("=" * 60)
        print("TEST FINISHED")
        print("=" * 60)

        await client.stop_notify(FEE3)
        await client.stop_notify(HEART_RATE)


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print()
        print("Stopped.")