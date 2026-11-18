// Svaraa V0 Wokwi/PlatformIO visual hardware harness (SIM).
// Drives SOS / privacy / NeoPixels / buzzer / haptic proxy / I2C stand-ins.
// NOT product firmware — Lab engine remains SOS authority.
// Unsupported in Wokwi: BLE, I2S, Nicla I2C target, MAX-M10S GNSS.
#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_NeoPixel.h>
#include <Adafruit_BMP085.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

// Product Nano labels → Wokwi ESP32-S3 raw GPIOs (see GPIO_MAP.md)
constexpr int SOS_GPIO = 5;       // D2
constexpr int PIXEL_GPIO = 18;    // D9
constexpr int BUZZER_GPIO = 1;    // A0
constexpr int PRIVACY_GPIO = 21;  // D10
constexpr int HAPTIC_GPIO = 14;   // SIM proxy for product D12/GPIO47
constexpr int PRIVACY_LED_GPIO = 13;  // Orange "privacy active" indicator
constexpr int I2C_SDA = 11;       // A4
constexpr int I2C_SCL = 12;       // A5

Adafruit_NeoPixel pixels(5, PIXEL_GPIO, NEO_GRB + NEO_KHZ800);
Adafruit_BMP085 bmp;
Adafruit_MPU6050 mpu;

bool bmpOk = false;
bool mpuOk = false;

int lastRaw = HIGH, stable = HIGH;
bool armed = false, down = false, fired = false;
uint32_t changed = 0, pressed = 0;
String phase = "Ready";
String lineBuf;
bool privacyDown = false;
bool alarmOn = false;
uint32_t lastSensorMs = 0;

void setAlarm(bool on) {
  alarmOn = on;
  if (on) {
    tone(BUZZER_GPIO, 2400);
    digitalWrite(HAPTIC_GPIO, HIGH);
  } else {
    noTone(BUZZER_GPIO);
    digitalWrite(HAPTIC_GPIO, LOW);
  }
}

void showPhase(const String& p) {
  phase = p;
  uint8_t r = 0, g = 0, b = 0;
  int lit = 1;
  bool alarm = false;
  if (p == "Prealert") {
    r = 40;
    g = 25;
    lit = 2;
  } else if (p == "Pending") {
    alarm = true;
  } else if (p == "ServerAccepted") {
    alarm = true;
  } else if (p == "HumanAck") {
    g = 40;
    lit = 5;
  } else if (p == "Resolved") {
    b = 30;
    lit = 1;
  } else {
    g = 8;
    b = 3;
    lit = 1;
  }
  // SOS with sound → every face light solid red (status + programmable bank)
  if (alarm) {
    r = 50;
    g = 0;
    b = 0;
    lit = 5;
  }
  pixels.clear();
  for (int i = 0; i < lit && i < 5; ++i) {
    pixels.setPixelColor(i, pixels.Color(r, g, b));
  }
  pixels.show();
  setAlarm(alarm);
  Serial.printf(
      "{\"type\":\"phase\",\"phase\":\"%s\",\"alarm\":%s,\"privacy\":%s,\"simulated\":true}\n",
      phase.c_str(), alarm ? "true" : "false", privacyDown ? "true" : "false");
}

void publishSensors() {
  float pressure = NAN, temp = NAN;
  float ax = NAN, ay = NAN, az = NAN;
  if (bmpOk) {
    pressure = bmp.readPressure() / 100.0f;
    temp = bmp.readTemperature();
  }
  if (mpuOk) {
    sensors_event_t a, g, t;
    mpu.getEvent(&a, &g, &t);
    ax = a.acceleration.x;
    ay = a.acceleration.y;
    az = a.acceleration.z;
  }
  Serial.printf(
      "{\"type\":\"sensors\",\"bmp\":{\"ok\":%s,\"hpa\":%.2f,\"c\":%.2f},"
      "\"imu\":{\"ok\":%s,\"ax\":%.3f,\"ay\":%.3f,\"az\":%.3f},"
      "\"stand_in\":true,\"note\":\"BMP180≠BMP390; MPU6050≠Nicla BMI270\"}\n",
      bmpOk ? "true" : "false", pressure, temp, mpuOk ? "true" : "false", ax, ay, az);
}

void setup() {
  Serial.begin(115200);
  delay(200);

  pinMode(SOS_GPIO, INPUT_PULLUP);
  pinMode(PRIVACY_GPIO, INPUT_PULLUP);
  pinMode(HAPTIC_GPIO, OUTPUT);
  pinMode(PRIVACY_LED_GPIO, OUTPUT);
  digitalWrite(HAPTIC_GPIO, LOW);
  digitalWrite(PRIVACY_LED_GPIO, LOW);
  pinMode(BUZZER_GPIO, OUTPUT);

  lastRaw = stable = digitalRead(SOS_GPIO);
  armed = stable == HIGH;
  changed = millis();
  privacyDown = digitalRead(PRIVACY_GPIO) == LOW;
  digitalWrite(PRIVACY_LED_GPIO, privacyDown ? HIGH : LOW);

  pixels.begin();
  pixels.setBrightness(28);

  Wire.begin(I2C_SDA, I2C_SCL);
  bmpOk = bmp.begin(0x77);
  mpuOk = mpu.begin(0x68);
  if (mpuOk) {
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  }

  showPhase("Ready");
  Serial.println(
      "{\"type\":\"boot\",\"msg\":\"SVARAA_WOKWI_HARNESS\",\"board\":\"esp32-s3-devkitc-1\","
      "\"limits\":\"no_BLE_no_I2S_no_Nicla_target_no_GNSS\","
      "\"bmp\":" +
      String(bmpOk ? "true" : "false") + ",\"imu\":" + String(mpuOk ? "true" : "false") + "}");
  publishSensors();
}

void handleLine(const String& line) {
  if (line.indexOf("\"cmd\":\"ping\"") >= 0) {
    Serial.println("{\"type\":\"pong\",\"phase\":\"" + phase + "\"}");
    return;
  }
  if (line.indexOf("\"cmd\":\"sensors\"") >= 0) {
    publishSensors();
    return;
  }
  int idx = line.indexOf("\"phase\":\"");
  if (idx >= 0) {
    int start = idx + 9;
    int end = line.indexOf('"', start);
    if (end > start) {
      showPhase(line.substring(start, end));
    }
  }
}

void loop() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n') {
      handleLine(lineBuf);
      lineBuf = "";
    } else if (c != '\r') {
      lineBuf += c;
      if (lineBuf.length() > 240) lineBuf = "";
    }
  }

  uint32_t now = millis();

  bool priv = digitalRead(PRIVACY_GPIO) == LOW;
  if (priv != privacyDown) {
    privacyDown = priv;
    digitalWrite(PRIVACY_LED_GPIO, privacyDown ? HIGH : LOW);
    if (!alarmOn) {
      digitalWrite(HAPTIC_GPIO, LOW);
    }
    Serial.printf("{\"type\":\"privacy\",\"down\":%s,\"simulated\":true}\n",
                  privacyDown ? "true" : "false");
  }

  int raw = digitalRead(SOS_GPIO);
  if (raw != lastRaw) {
    lastRaw = raw;
    changed = now;
  }
  if (now - changed >= 20) stable = raw;
  if (stable == HIGH) {
    armed = true;
    down = false;
    fired = false;
  }
  if (armed && stable == LOW) {
    if (!down) {
      down = true;
      pressed = now;
      showPhase("Prealert");
      Serial.println("{\"type\":\"hold\",\"down\":true}");
    }
    if (!fired && now - pressed >= 2000) {
      fired = true;
      showPhase("Pending");
      Serial.println(
          "{\"type\":\"mock_sos\",\"phase\":\"Pending\",\"sent\":false,"
          "\"note\":\"visual_only_Lab_engine_is_authority\"}");
    }
  }

  if (now - lastSensorMs >= 2000) {
    lastSensorMs = now;
    publishSensors();
  }
  delay(1);
}
