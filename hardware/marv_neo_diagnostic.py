import asyncio
from bleak import BleakClient


ADDRESS = "F7:64:1C:18:04:39"


def notification_handler(sender, data):
    raw = bytes(data)

    print()
    print("=" * 70)
    print("NOTIFICATION")
    print("=" * 70)
    print("Characteristic:", sender)
    print("Length:", len(raw))
    print("HEX:", raw.hex(" "))
    print("DEC:", list(raw))
    print("=" * 70)


async def main():

    print("=" * 70)
    print("MARV NEO BLE DIAGNOSTIC")
    print("=" * 70)

    print()
    print("Connecting to:")
    print(ADDRESS)
    print()

    async with BleakClient(ADDRESS) as client:

        if not client.is_connected:
            print("Connection failed.")
            return

        print("SUCCESS! MARV NEO connected.")
        print()

        print("=" * 70)
        print("SERVICES")
        print("=" * 70)

        for service in client.services:

            print()
            print("SERVICE:", service.uuid)

            for characteristic in service.characteristics:

                print()
                print("CHARACTERISTIC:", characteristic.uuid)
                print("PROPERTIES:", characteristic.properties)

                if "read" in characteristic.properties:

                    try:

                        value = await client.read_gatt_char(
                            characteristic.uuid
                        )

                        print(
                            "READ:",
                            bytes(value).hex(" ")
                        )

                    except Exception as error:

                        print(
                            "READ ERROR:",
                            error
                        )

                if "notify" in characteristic.properties:

                    try:

                        await client.start_notify(
                            characteristic.uuid,
                            notification_handler
                        )

                        print(
                            "NOTIFICATIONS: ENABLED"
                        )

                    except Exception as error:

                        print(
                            "NOTIFICATION ERROR:",
                            error
                        )

        print()
        print("=" * 70)
        print("LISTENING FOR DATA")
        print("=" * 70)
        print()
        print("Now perform measurements on the watch.")
        print()
        print("1. Open Heart Rate on the watch")
        print("2. Start the measurement")
        print("3. Wait for the result")
        print("4. Open SpO2 and measure")
        print("5. Open Blood Pressure and measure")
        print()
        print("Keep the watch close to the laptop.")
        print("Press CTRL+C when finished.")
        print()

        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:

        print()
        print("Diagnostic stopped.")