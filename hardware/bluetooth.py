import serial

class BluetoothDevice:
    def __init__(self, port, baudrate=115200):
        self.connection = serial.Serial(
            port,
            baudrate,
            timeout=1
        )

    def read_data(self):
        if self.connection.in_waiting:
            return self.connection.readline().decode().strip()

        return None

    def close(self):
        self.connection.close()