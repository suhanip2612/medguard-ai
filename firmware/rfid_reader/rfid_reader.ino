// MedGuard AI - ESP32 + RC522 RFID reader
// Library needed: "MFRC522" by GithubCommunity (Arduino IDE > Library Manager)
// Board: "ESP32 Dev Module"   Serial Monitor baud: 115200
//
// Wiring (RC522 -> ESP32):  SDA->GPIO5  SCK->GPIO18  MOSI->GPIO23  MISO->GPIO19
//                           RST->GPIO22 3.3V->3V3 (NOT 5V)  GND->GND  IRQ->not connected
#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN  5
#define RST_PIN 22

MFRC522 rfid(SS_PIN, RST_PIN);
String lastUid = "";
unsigned long lastTapTime = 0;

void setup() {
  Serial.begin(115200);
  SPI.begin(18, 19, 23, 5);  // SCK, MISO, MOSI, SS
  rfid.PCD_Init();
  Serial.println("READY");
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;

  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();

  // Ignore the same card for 2 seconds (debounce)
  if (uid != lastUid || millis() - lastTapTime > 2000) {
    Serial.println("UID:" + uid);
    lastUid = uid;
    lastTapTime = millis();
  }

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}
