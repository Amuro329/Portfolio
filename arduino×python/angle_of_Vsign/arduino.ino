int led_1 = 8,led_2 = 4,led_3 = 2;

void func_led(char x,char y,char z){
   digitalWrite(led_1, x);
   digitalWrite(led_2, y);
   digitalWrite(led_3, z);
}

void setup(){
  Serial.begin(9600);
  pinMode(led_1, OUTPUT);
  pinMode(led_2, OUTPUT);
  pinMode(led_3, OUTPUT);

  digitalWrite(led_1, LOW);
  digitalWrite(led_2, LOW);
  digitalWrite(led_3, LOW);
}

void loop(){
  int input = Serial.read();
  if(input != -1){
  Serial.println(input);
    switch(input){
      case '0':
        func_led(HIGH,HIGH,HIGH);
        break;
      case '1':
        func_led(HIGH,HIGH,LOW);
        break;
      case '2':
        func_led(HIGH,LOW,LOW);
        break;
      case '3':
        func_led(LOW,LOW,LOW);
        break;
      default:
        break;
  }
  while(Serial.available())Serial.read();
  }
}
