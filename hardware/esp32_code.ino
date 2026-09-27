#include <BluetoothSerial.h>

BluetoothSerial SerialBT;

float heartRate = 75.0;
float spo2 = 98.0;
float temperature = 36.7;

void setup() {
  Serial.begin(115200);
  SerialBT.begin("AI_Digital_Doctor");
}

void loop() {
  String data = "{";
  data += "\"heart_rate\":";
  data += String(heartRate);
  data += ",";
  data += "\"spo2\":";
  data += String(spo2);
  data += ",";
  data += "\"temperature\":";
  data += String(temperature);
  data += "}";

  SerialBT.println(data);
  Serial.println(data);

  delay(5000);
}