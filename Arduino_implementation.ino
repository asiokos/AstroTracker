#include <LiquidCrystal.h>
#include<math.h>

//pin configuration
LiquidCrystal lcd = LiquidCrystal(2, 3, 4, 5, 6, 7);
int const time_pin = A1; // analog input for exposure time
const int start_pin = 13; // start button
const int reset_pin = 12; // reset button
int pins[4] = {8,9,10,11};

//tracker specs

double radius = 192.0; // mm 
double angular_velocity = 0.00007292115761437; // rad/sec
double thread_pitch=0.7; // mm
double gear_ratio = 63.68395*30/13;
double exposure_time;
int minutes_exp,seconds_exp,mapped_time_seconds;
int start,reset; 
double rps = angular_velocity*radius*gear_ratio/thread_pitch;
double step_angle = 11.25/2;
double step_per_rev = 360./step_angle;
double step_per_sec = step_per_rev*rps;
unsigned long number_of_steps;
char str[16],str1[16],str2[16];
double delay_stepper = 1000./step_per_sec;
double error = 0;

int sequence[8][4]= { {HIGH, LOW, LOW, LOW},
                      {HIGH, HIGH, LOW, LOW},
                      {LOW, HIGH, LOW, LOW},
                      {LOW, HIGH, HIGH, LOW},
                      {LOW, LOW, HIGH, LOW},
                      {LOW, LOW, HIGH, HIGH},
                      {LOW, LOW, LOW, HIGH},
                      {HIGH, LOW, LOW, HIGH}
                      };


void setup() {
  pinMode(start_pin, INPUT);
  pinMode(reset_pin, INPUT);
  for(int p=0;p<4;p++)
  {
     pinMode(pins[p],OUTPUT);
     digitalWrite(pins[p],LOW);  
  }
  lcd.begin(16, 2);
}

void loop() {
  start = digitalRead(start_pin);
  reset = digitalRead(reset_pin);
  if(start == LOW && reset == LOW)
    {
      exposure_time = analogRead(time_pin);
      mapped_time_seconds = map(exposure_time,0,1023,0,30*60);
      minutes_exp = mapped_time_seconds/60;
      seconds_exp = mapped_time_seconds%60;
      sprintf(str1,"Time: %02d:%02d", minutes_exp, seconds_exp);
      lcd.setCursor(0, 0);
      lcd.print("Set exposure");
      lcd.setCursor(0, 1);
      lcd.print(str1);
    }
  else if(start == HIGH && reset == LOW)
    {
      exposure_time = analogRead(time_pin);
      mapped_time_seconds = map(exposure_time,0,1023,0,30*60);
      number_of_steps = ceil(mapped_time_seconds*step_per_sec);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Tracking stars");
      int minutes=0,seconds=0;
      unsigned long startMillis = millis();
      long int step_motion=0;
      while(step_motion<number_of_steps)
          {
            for( int seq_step=0;seq_step<8;seq_step++)
            {
                    for (int p=0;p<4;p++)
                    {
                          digitalWrite(pins[p],sequence[seq_step][p]);
                    }
                    delay(delay_stepper-error/100.*delay_stepper);
                    step_motion = step_motion+1;
                    if(step_motion>=number_of_steps)
                    {
                      break;
                    }   
            }
            unsigned long currentMillis = millis();
            minutes = ((currentMillis-startMillis)/1000)/60;
            seconds = ((currentMillis-startMillis)/1000)%60;
            lcd.setCursor(0,1);
            sprintf(str,"Time: %02d:%02d", minutes, seconds);
            lcd.print(str);
          }
        lcd.clear();
      }
  else if(start == LOW && reset == HIGH)
  {
      exposure_time = analogRead(time_pin);
      mapped_time_seconds = map(exposure_time,0,1023,0,30*60);
      number_of_steps = ceil(mapped_time_seconds*step_per_sec);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Resetting");
      int minutes=0,seconds=0;
      unsigned long startMillis = millis();
      long int step_motion=0;
      while(step_motion<number_of_steps)
          {
            for( int seq_step=7;seq_step>=0;seq_step--)
            {
                    for (int p=0;p<4;p++)
                    {
                          digitalWrite(pins[p],sequence[seq_step][p]);
                    }
                    delay(delay_stepper-error/100.*delay_stepper);
                    step_motion = step_motion+1;
                    if(step_motion>=number_of_steps)
                    {
                      break;
                    }   
            }
            unsigned long currentMillis = millis();
            minutes = ((currentMillis-startMillis)/1000)/60;
            seconds = ((currentMillis-startMillis)/1000)%60;
            lcd.setCursor(0,1);
            sprintf(str,"Time: %02d:%02d", minutes, seconds);
            lcd.print(str);
          }
        lcd.clear();
      }
}
