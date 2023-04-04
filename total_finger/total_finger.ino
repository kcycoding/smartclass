#include <Adafruit_Fingerprint.h>
#include <IRremote.h>
#include <Adafruit_NeoPixel.h>
#include <avr/power.h>

// int red = 6;
// int green = 7;
// int blue = 8;

#define PIN 7
#define NUMPIXELS 4
#define BRIGHTNESS 180

Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

IRsend irsend;

#if (defined(__AVR__) || defined(ESP8266)) && !defined(__AVR_ATmega2560__)
SoftwareSerial mySerial(18, 19);  // 18:노랑, 19:검정
#else
#define mySerial Serial1
#endif
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

uint8_t id;

void setup() {
  Serial.begin(115200);
  // pinMode(red, OUTPUT);
	// pinMode(green, OUTPUT);
  // pinMode(blue, OUTPUT);
  strip.setBrightness(BRIGHTNESS);
  strip.begin();
  strip.show();
  while (!Serial);  // For Yun/Leo/Micro/Zero/...
  delay(100);
  finger.begin(57600);
  if (finger.verifyPassword()) {
    Serial.println("Found fingerprint sensor!");
  } else {
    Serial.println("Did not find fingerprint sensor :(");
    while (1) { delay(1); }
  }

  // Serial.println(F("Reading sensor parameters"));
  // finger.getParameters();
  // finger.getTemplateCount();

  // if (finger.templateCount == 0) 
  // {
  //   Serial.print("Sensor doesn't contain any fingerprint data. Please run the 'enroll' example.");
  // }
  // else 
  // {
  //   Serial.println("Waiting for valid finger...");
  //   Serial.print("Sensor contains "); Serial.print(finger.templateCount); Serial.println(" templates");
  //   for (uint16_t i=1; i<=finger.templateCount; i++)
  //   {
  //     uint16_t id = finger.loadModel(i);
  //     if (id != 0xFFFF) 
  //     {
  //       Serial.print("ID #"); Serial.print(id);
  //       Serial.print(": ");
  //       Serial.println("loaded");
  //     }
  //   }
  // } 
}
// enrolllll /////////////////////////////////////////////////////
uint8_t readnumber(void) {
  uint8_t num = 0;

  while (num == 0) {
    while (! Serial.available());
    num = Serial.parseInt();
  }
  return num;
}

uint8_t getFingerprintEnroll() {

  int p = -1;
  Serial.print("Waiting for valid finger to enroll as #"); Serial.println(id);
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Image taken");
      break;
    case FINGERPRINT_NOFINGER:
      Serial.println(".");
      break;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Communication error");
      break;
    case FINGERPRINT_IMAGEFAIL:
      Serial.println("Imaging error");
      break;
    default:
      Serial.println("Unknown error");
      break;
    }
  }
  // OK success!

  p = finger.image2Tz(1);
  switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Image converted");
      break;
    case FINGERPRINT_IMAGEMESS:
      Serial.println("Image too messy");
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Communication error");
      return p;
    case FINGERPRINT_FEATUREFAIL:
      Serial.println("Could not find fingerprint features");
      return p;
    case FINGERPRINT_INVALIDIMAGE:
      Serial.println("Could not find fingerprint features");
      return p;
    default:
      Serial.println("Unknown error");
      return p;
  }

  Serial.println("Remove finger");
  delay(1000);
  p = 0;
  while (p != FINGERPRINT_NOFINGER) {
    p = finger.getImage();
  }
  Serial.print("ID "); Serial.println(id);
  p = -1;
  Serial.println("Place same finger again");
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Image taken");
      break;
    case FINGERPRINT_NOFINGER:
      Serial.print(".");
      break;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Communication error");
      break;
    case FINGERPRINT_IMAGEFAIL:
      Serial.println("Imaging error");
      break;
    default:
      Serial.println("Unknown error");
      break;
    }
  }

  // OK success!

  p = finger.image2Tz(2);
  switch (p) {
    case FINGERPRINT_OK:
      Serial.println("Image converted");
      break;
    case FINGERPRINT_IMAGEMESS:
      Serial.println("Image too messy");
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("Communication error");
      return p;
    case FINGERPRINT_FEATUREFAIL:
      Serial.println("Could not find fingerprint features");
      return p;
    case FINGERPRINT_INVALIDIMAGE:
      Serial.println("Could not find fingerprint features");
      return p;
    default:
      Serial.println("Unknown error");
      return p;
  }

  // OK converted!
  Serial.print("Creating model for #");  Serial.println(id);

  p = finger.createModel();
  if (p == FINGERPRINT_OK) {
    Serial.println("Prints matched!");
  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    Serial.println("Communication error");
    return p;
  } else if (p == FINGERPRINT_ENROLLMISMATCH) {
    Serial.println("Fingerprints did not match");
    return p;
  } else {
    Serial.println("Unknown error");
    return p;
  }

  Serial.print("ID "); Serial.println(id);
  p = finger.storeModel(id);
  if (p == FINGERPRINT_OK) {
    Serial.println("Stored!");
    strip.setPixelColor(0, 0, 0, 255);
    strip.setPixelColor(1, 0, 0, 255);
    strip.show();
    delay(2000);
    strip.setPixelColor(0, 0, 0, 0);
    strip.setPixelColor(1, 0, 0, 0);
    strip.show();
    delay(1000);
    // digitalWrite(8, HIGH);
    // delay(1000);
    // digitalWrite(8, LOW);
  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    Serial.println("Communication error");
    return p;
  } else if (p == FINGERPRINT_BADLOCATION) {
    Serial.println("Could not store in that location");
    return p;
  } else if (p == FINGERPRINT_FLASHERR) {
    Serial.println("Error writing to flash");
    return p;
  } else {
    Serial.println("Unknown error");
    return p;
  }

  return true;
}

// fingerprinttt //////////////////////////////////////////////////
uint8_t getFingerprintID() {
  uint8_t p = finger.getImage();
  switch (p)
  {
    case FINGERPRINT_OK:
      // Serial.println("Image taken");
      break;
    case FINGERPRINT_NOFINGER:
      Serial.println("No finger detected");
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      // Serial.println("Communication error");
      return p;
    case FINGERPRINT_IMAGEFAIL:
      // Serial.println("Imaging error");
      return p;
    default:
      // Serial.println("Unknown error");
      return p;
  }

  // OK success!

  p = finger.image2Tz();
  switch (p)
  {
    case FINGERPRINT_OK:
      // Serial.println("Image converted");
      break;
    case FINGERPRINT_IMAGEMESS:
      // Serial.println("Image too messy");
      return p;
    case FINGERPRINT_PACKETRECIEVEERR:
      // Serial.println("Communication error");
      return p;
    case FINGERPRINT_FEATUREFAIL:
      // Serial.println("Could not find fingerprint features");
      return p;
    case FINGERPRINT_INVALIDIMAGE:
      // Serial.println("Could not find fingerprint features");
      return p;
    default:
      // Serial.println("Unknown error");
      return p;
  }

  // OK converted!
  p = finger.fingerSearch();
  if (p == FINGERPRINT_OK) {
    // Serial.println("Found a print match!");
    strip.setPixelColor(0, 0, 255, 0);
    strip.setPixelColor(1, 0, 255, 0);
    strip.show();
    delay(1000);
    strip.setPixelColor(0, 0, 0, 0);
    strip.setPixelColor(1, 0, 0, 0);
    strip.show();
    // digitalWrite(7, HIGH);
    // delay(600);
    // digitalWrite(7, LOW);
  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    Serial.println("Communication error");
    return p;
  } else if (p == FINGERPRINT_NOTFOUND) {
    Serial.println("Did not find a match");
    strip.setPixelColor(0, 255, 0, 0);
    strip.setPixelColor(1, 255, 0, 0);
    strip.show();
    delay(1000);
    strip.setPixelColor(0, 0, 0, 0);
    strip.setPixelColor(1, 0, 0, 0);
    strip.show();
    // digitalWrite(6, HIGH);
    // digitalWrite(6, LOW);

    return p;
  } else {
    // Serial.println("Unknown error");
    return p;
  }

  // found a match!
  Serial.print("Found ID #"); 
  Serial.println(finger.fingerID);
  // Serial.print(" with confidence of "); Serial.println(finger.confidence);
  // Serial.println("fingerSearch");
  delay(800);

  return finger.fingerID;
}

// returns -1 if failed, otherwise returns ID #
int getFingerprintIDez() {
  uint8_t p = finger.getImage();
  if (p != FINGERPRINT_OK)  return -1;

  p = finger.image2Tz();
  if (p != FINGERPRINT_OK)  return -1;

  p = finger.fingerFastSearch();
  if (p != FINGERPRINT_OK)  return -1;

  // found a match!
  Serial.print("Found ID/ #");
   Serial.println(finger.fingerID);
   Serial.println("getFingerprintIDez");
  // Serial.print(" with confidence of "); Serial.println(finger.confidence);
  return finger.fingerID;
}

// deleteeee //////////////////////////////////////////////////////////
uint8_t deleteFingerprint(uint8_t id) {
  uint8_t p = -1;

  p = finger.deleteModel(id);

  if (p == FINGERPRINT_OK) {
    Serial.println("Deleted!");
  } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
    Serial.println("Communication error");
  } else if (p == FINGERPRINT_BADLOCATION) {
    Serial.println("Could not delete in that location");
  } else if (p == FINGERPRINT_FLASHERR) {
    Serial.println("Error writing to flash");
  } else {
    Serial.print("Unknown error: 0x"); Serial.println(p, HEX);
  }

  return p;
}

// 입력 받기
String readSerial() {  
  String str = "";
  if (Serial.available())
  {
    str = Serial.readString();
  }
  return str;
}

String str;

void loop() {
  // String str = readSerial();  
  // if (str == "");
  // Serial.println(str);
  if (Serial.available())
  {
    str = Serial.readStringUntil('\n');
  
    if (str == "e")
    {
      Serial.println("Ready to enroll a fingerprint!");
      Serial.println("Please type in the ID # (from 1 to 127) you want to save this finger as...");
      id = readnumber();
      if (id == 0) {// ID #0 not allowed, try again!
        return;
      }
      Serial.print("Enrolling ID #");
      Serial.println(id);

      getFingerprintEnroll();
    }
    else if (str == "d")
    {
      Serial.println("Please type in the ID # (from 1 to 127) you want to delete...");
      uint8_t id = readnumber();
      if (id == 0) {// ID #0 not allowed, try again!
        return;
      }

      Serial.print("Deleting ID #");
      Serial.println(id);

      deleteFingerprint(id);
    }
    else if (str == "donn")
    {
      Serial.println("donn");
      irsend.sendNEC(0x1FE48B7, 32);
      irsend.sendNEC(0x1FE48B7, 32);
    }
    else if (str == "doff")
    {
      Serial.println("doff");
      irsend.sendNEC(0x1FE58A7, 32);
      irsend.sendNEC(0x1FE58A7, 32);
    }
    else if (str == "acon")
    {
      Serial.println("acon");
      irsend.sendLG(0x880490D,28);
      irsend.sendLG(0x880490D,28);
    }
    else if (str == "acoff")
    {
      Serial.println("acoff");
      irsend.sendLG(0x88C0051,28);
      irsend.sendLG(0x88C0051,28);
    }
    else if (str == "heater")
    {
      Serial.println("heater");
      irsend.sendLG(0x880490D);
      irsend.sendLG(0x880490D);
    }
    else if (str == "cool")
    {
      Serial.println("cool");
      irsend.sendLG(0x8800909);
      irsend.sendLG(0x8800909);
    }
    else if (str == "brightness")
    {
      Serial.println("brightness");
      irsend.sendNEC(0x1FE7887,32);
      irsend.sendNEC(0x1FE7887,32);
    }
    else if (str == "all_delete")
    {
      finger.emptyDatabase();
      Serial.print("all fingerprint delete");
    }
  }
  getFingerprintID();
  delay(1500);

}
