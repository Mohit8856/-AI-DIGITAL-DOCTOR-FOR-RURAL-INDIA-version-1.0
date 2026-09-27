import asyncio
from bleak import BleakClient


ADDRESS = "F7:64:1C:18:04:39"

COMMAND_CHARACTERISTIC = (
    "0000fee2-0000-1000-8000-00805f9b34fb"
)

RESPONSE_CHARACTERISTIC = (
    "0000fee3-0000-1000-8000-00805f9b34fb"
)

HEART_RATE_CHARACTERISTIC = (
    "00002a37-0000-1000-8000-00805f9b34fb"
)


def response_handler(sender, data):

    raw = bytes(data)

    print()
    print("FEE3 RESPONSE")
    print("-" * 60)
    print("HEX:", raw.hex(" "))
    print("DEC:", list(raw))
    print("-" * 60)


def heart_rate_handler(sender, data):

    raw = bytes(data)

    if len(raw) < 2:
        return

    flags = raw[0]

    if flags & 0x01:

        if len(raw) < 3:
            return

        heart_rate = int.from_bytes(
            raw[1:3],
            byteorder="little"
        )

    else:

        heart_rate = raw[1]

    print(
        f"HEART RATE: {heart_rate} BPM"
    )


async def send_command(client, command, name):

    packet = bytes([
        0xAB,
        0x00,
        0x04,
        0x00,
        command,
        0x00,
        0xFF
    ])

    print()
    print("=" * 60)
    print("REQUESTING:", name)
    print("COMMAND:", hex(command))
    print("PACKET:", packet.hex(" "))
    print("=" * 60)

    await client.write_gatt_char(
        COMMAND_CHARACTERISTIC,
        packet,
        response=False
    )

    await asyncio.sleep(8)


async def main():

    print("=" * 60)
    print("MARV NEO HEALTH DATA TEST")
    print("=" * 60)

    print()
    print("Connecting...")
    print(ADDRESS)

    async with BleakClient(ADDRESS) as client:

        if not client.is_connected:

            print("Connection failed.")
            return

        print()
        print("MARV NEO CONNECTED")
        print()

        await client.start_notify(
            RESPONSE_CHARACTERISTIC,
            response_handler
        )

        await client.start_notify(
            HEART_RATE_CHARACTERISTIC,
            heart_rate_handler
        )

        print("Notifications enabled.")

        await asyncio.sleep(2)

        await send_command(
            client,
            0x0B,
            "SPO2"
        )

        print()
        print("Now perform SpO2 measurement on the watch.")
        print("Wait for the watch to display the result.")

        await asyncio.sleep(10)

        await send_command(
            client,
            0x0A,
            "HEART RATE"
        )

        await asyncio.sleep(5)

        print()
        print("=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)

        await client.stop_notify(
            RESPONSE_CHARACTERISTIC
        )

        await client.stop_notify(
            HEART_RATE_CHARACTERISTIC
        )


if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print()
        print("Test stopped.")