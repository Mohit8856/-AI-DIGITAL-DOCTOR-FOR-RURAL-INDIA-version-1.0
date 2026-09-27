import asyncio
import threading
from bleak import BleakClient


MARV_NEO_ADDRESS = "F7:64:1C:18:04:39"

HEART_RATE_UUID = (
    "00002a37-0000-1000-8000-00805f9b34fb"
)

FEE2_UUID = (
    "0000fee2-0000-1000-8000-00805f9b34fb"
)

FEE3_UUID = (
    "0000fee3-0000-1000-8000-00805f9b34fb"
)


class SmartwatchBLE:

    def __init__(self, address=MARV_NEO_ADDRESS):

        self.address = address

        self.connected = False

        self.latest_data = {
            "connected": False,
            "device": "MARV NEO",
            "heart_rate": None,
            "spo2": None,
            "temperature": None,
            "blood_pressure": None,
            "systolic": None,
            "diastolic": None
        }

        self.client = None
        self.loop = None
        self.thread = None
        self.running = False

    def get_data(self):
        return dict(self.latest_data)

    def _heart_rate_handler(self, sender, data):

        raw = bytes(data)

        if len(raw) < 2:
            return

        flags = raw[0]

        try:

            if flags & 0x01:

                if len(raw) < 3:
                    return

                heart_rate = int.from_bytes(
                    raw[1:3],
                    byteorder="little"
                )

            else:

                heart_rate = raw[1]

            if 30 <= heart_rate <= 240:

                self.latest_data["heart_rate"] = heart_rate

                print(
                    f"❤️ Heart Rate: {heart_rate} BPM"
                )

        except Exception as error:

            print(
                "Heart-rate decoding error:",
                error
            )

    def _fee3_handler(self, sender, data):

        raw = bytes(data)

        print(
            "FEE3:",
            raw.hex(" ")
        )

        self._decode_fee3(raw)

    def _decode_fee3(self, raw):

        if len(raw) < 5:
            return

        if raw[0] != 0xFE:
            return

        if raw[1] != 0xEA:
            return

        command = raw[4]

        payload = raw[5:]

        if command == 0x69:

            self._decode_69(payload)

        elif command == 0x6B:

            self._decode_6b(payload)

        elif command == 0x68:

            self._decode_68(payload)

    def _decode_69(self, payload):

        if len(payload) < 3:
            return

        systolic = payload[1]
        diastolic = payload[2]

        if (
            systolic == 0xFF
            or diastolic == 0xFF
        ):
            return

        if (
            50 <= systolic <= 250
            and
            30 <= diastolic <= 150
            and
            systolic > diastolic
        ):

            self.latest_data["systolic"] = systolic

            self.latest_data["diastolic"] = diastolic

            self.latest_data["blood_pressure"] = (
                f"{systolic}/{diastolic}"
            )

            print(
                "🩸 Blood Pressure:",
                f"{systolic}/{diastolic} mmHg"
            )

    def _decode_6b(self, payload):

        if not payload:
            return

        for value in payload:

            if 70 <= value <= 100:

                self.latest_data["spo2"] = value

                print(
                    f"🫁 SpO₂: {value}%"
                )

                return

    def _decode_68(self, payload):

        if len(payload) < 2:
            return

        systolic = payload[0]
        diastolic = payload[1]

        if (
            70 <= systolic <= 250
            and
            40 <= diastolic <= 150
            and
            systolic > diastolic
        ):

            self.latest_data["systolic"] = systolic

            self.latest_data["diastolic"] = diastolic

            self.latest_data["blood_pressure"] = (
                f"{systolic}/{diastolic}"
            )

            print(
                "🩸 Blood Pressure:",
                f"{systolic}/{diastolic} mmHg"
            )

    async def _run(self):

        while self.running:

            try:

                print()
                print(
                    "Connecting to MARV NEO..."
                )

                async with BleakClient(
                    self.address
                ) as client:

                    self.client = client

                    if not client.is_connected:

                        print(
                            "MARV NEO connection failed."
                        )

                        self.connected = False

                        self.latest_data[
                            "connected"
                        ] = False

                        await asyncio.sleep(5)

                        continue

                    self.connected = True

                    self.latest_data[
                        "connected"
                    ] = True

                    print(
                        "MARV NEO connected."
                    )

                    await client.start_notify(
                        HEART_RATE_UUID,
                        self._heart_rate_handler
                    )

                    await client.start_notify(
                        FEE3_UUID,
                        self._fee3_handler
                    )

                    print(
                        "❤️ Heart-rate notifications enabled."
                    )

                    print(
                        "📡 MARV NEO health notifications enabled."
                    )

                    while (
                        self.running
                        and
                        client.is_connected
                    ):

                        await asyncio.sleep(1)

            except Exception as error:

                print(
                    "MARV NEO error:",
                    error
                )

                self.connected = False

                self.latest_data[
                    "connected"
                ] = False

                self.client = None

                if self.running:

                    await asyncio.sleep(5)

    def _thread_target(self):

        self.loop = asyncio.new_event_loop()

        asyncio.set_event_loop(
            self.loop
        )

        self.loop.run_until_complete(
            self._run()
        )

        self.loop.close()

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self._thread_target,
            daemon=True
        )

        self.thread.start()

        print(
            "MARV NEO background service started."
        )

    def stop(self):

        self.running = False

        self.connected = False

        self.latest_data[
            "connected"
        ] = False

        print(
            "MARV NEO service stopped."
        )


smartwatch = SmartwatchBLE()