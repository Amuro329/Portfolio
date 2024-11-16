# 指の角度に応じて発光するLEDの数を変更する
　

## python側
mediapipeを使用。
人差し指の先端と根本を通るベクトルと、中指の先端と根本を通るベクトルの2ベクトルがなす角を計算（内積）。

ランドマークの取得(例:人差し指の先端)は、
```python
index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]  
middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]  
index_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]  
middle_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]  
```
で取得することができ、座標は、
```python
index_finger = np.array([index_finger_tip.x, index_finger_tip.y])  
middle_finger = np.array([middle_finger_tip.x, middle_finger_tip.y])                  
index_point = np.array([index_finger_mcp.x, index_finger_mcp.y])  
middle_point = np.array([middle_finger_mcp.x, middle_finger_mcp.y])  
```
で取得できる。得られた座標からベクトルを計算し、角度を求めた。
```python
# ベクトルの計算
vec_index = index_finger - index_point
vec_middle = middle_finger - middle_point
# 角度の計算
cos_theta = np.dot(vec_index, vec_middle) / (np.linalg.norm(vec_index) * np.linalg.norm(vec_middle))
angle = np.degrees(np.arccos(np.clip(cos_theta, -1.0, 1.0)))
angle_int = int(angle)
```

それをシリアル通信でarduinoに値を送信している。
45度以上であれば0、25度以上であれば1、10度以上であれば2、それ以外は3と送信するように設定。
```C++
if angle_int > 45:  
  ser.write(bytes('0', encoding='ascii'))  
elif angle_int > 25:  
  ser.write(bytes('1', encoding='ascii'))  
elif angle_int > 10:  
  ser.write(bytes('2', encoding='ascii'))  
else:  
  ser.write(bytes('3', encoding='ascii'))  
```

カメラの起動では、
```C++
 cap = cv2.VideoCapture(0)
```
としているが、0を1に変更すると外カメラになる。

## Arduino側
arduinoでは指の角度に応じて発光するLEDの数を変化させている。
```C++
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
```
ここで、発光の関数func_ledは以下のように定義している。
```C++
void func_led(char x,char y,char z){  
   digitalWrite(led_1, x);  
   digitalWrite(led_2, y);  
   digitalWrite(led_3, z);  
}
```

