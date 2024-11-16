# 指の角度に応じて発光するLEDの数を変更するプログラム
指の角度に応じてLEDの発光数を変化させるプログラム。Pythonを用いて角度を計測し、Arduinoを介してLEDを制御している。

## 特徴
- Mediapipeを使用して手のランドマークを取得し、指の角度を計算。
- シリアル通信を通じてArduinoに角度情報を送信。
- 角度に応じてLEDの発光数を制御。

## 使用技術
- Python 3.x
  - Mediapipe
  - OpenCV
  - NumPy
  - PySerial
- Arduino
  - C++

## 必要なハードウェア
- Arduino Unoまたは互換ボード
- LED（3個以上）
- 抵抗
- ブレッドボード
- ジャンパーワイヤー

## 動作方法
カメラが起動し、手のランドマークが検出。人差し指と中指の角度が計算され、その値に応じてArduinoにデータが送信される。Arduinoが受信したデータに応じて、LEDの発光数が変化する。  

## 角度とLED発光の対応
- 45度以上: 全LED点灯  
- 25度以上: 2個点灯  
- 10度以上: 1個点灯  
- 10度未満: 全消灯  

___

## python側
mediapipeを使用。

### 角度計算
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
### シリアル通信
計算した角度を閾値（45度、25度、10度）で分類し、対応する値（0～3）をArduinoに送信。
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
### カメラの設定
OpenCVを用いてカメラを起動。0を1に変更すると外カメラになる。
```C++
 cap = cv2.VideoCapture(0)
```

___

## Arduino側
### シリアル通信の受信
arduinoではPython側から送られた値（0～3）を受信し、その値に応じてLEDの発光数を切り替える制御を行う。
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
### LED制御
指定された状態に応じて複数のLEDの発光を制御する関数を以下のように定義。
```C++
void func_led(char x,char y,char z){  
   digitalWrite(led_1, x);  
   digitalWrite(led_2, y);  
   digitalWrite(led_3, z);  
}
```

