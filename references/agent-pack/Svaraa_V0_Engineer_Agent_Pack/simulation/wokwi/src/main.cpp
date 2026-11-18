// Visual starter, NOT the integrated safety firmware. No actual event is sent.
#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
constexpr int SOS_GPIO=5,PIXEL_GPIO=18;
Adafruit_NeoPixel pixels(5,PIXEL_GPIO,NEO_GRB+NEO_KHZ800);
int lastRaw=HIGH,stable=HIGH;bool armed=false,down=false,fired=false;
uint32_t changed=0,pressed=0;
void setup(){
 Serial.begin(115200);pinMode(SOS_GPIO,INPUT_PULLUP);
 lastRaw=stable=digitalRead(SOS_GPIO);armed=stable==HIGH;changed=millis();
 pixels.begin();pixels.setBrightness(24);pixels.clear();pixels.show();
 Serial.println("SIM ONLY: hold 2 seconds. No backend or real notification.");
}
void loop(){
 uint32_t now=millis();int raw=digitalRead(SOS_GPIO);
 if(raw!=lastRaw){lastRaw=raw;changed=now;}
 if(now-changed>=20)stable=raw;
 if(stable==HIGH){armed=true;down=false;fired=false;}
 if(armed&&stable==LOW){
  if(!down){down=true;pressed=now;}
  if(!fired&&now-pressed>=2000){
   fired=true;for(int i=0;i<5;++i)pixels.setPixelColor(i,pixels.Color(50,0,0));
   pixels.show();Serial.println("MOCK SOS PENDING - NOT SENT");
  }
 }
 delay(1);
}
