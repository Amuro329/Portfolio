#SimpleSerial_001.py
import serial
from time import sleep 
import cv2
import mediapipe as mp
import numpy as np

# Mediapipeの設定
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Webカメラの起動
cap = cv2.VideoCapture(0)

#シリアル通信(PC⇔Arduino)
ser = serial.Serial()
ser.port = "COM5"     #デバイスマネージャでArduinoのポート確認
ser.baudrate = 9600 #Arduinoと合わせる
ser.setDTR(False)     #DTRを常にLOWにしReset阻止
ser.open()            #COMポートを開く

# Mediapipe Handsの初期化
with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 画像の前処理
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        # RGBからBGRへ再変換
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # 手のランドマークが検出された場合
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # ランドマークの描画
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # 人差し指と中指のランドマーク取得
                index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                index_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
                middle_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]

                # 座標の取得
                index_finger = np.array([index_finger_tip.x, index_finger_tip.y])
                middle_finger = np.array([middle_finger_tip.x, middle_finger_tip.y])                
                index_point = np.array([index_finger_mcp.x, index_finger_mcp.y])
                middle_point = np.array([middle_finger_mcp.x, middle_finger_mcp.y])

                # ベクトルの計算
                vec_index = index_finger - index_point
                vec_middle = middle_finger - middle_point

                # 角度の計算
                cos_theta = np.dot(vec_index, vec_middle) / (np.linalg.norm(vec_index) * np.linalg.norm(vec_middle))
                angle = np.degrees(np.arccos(np.clip(cos_theta, -1.0, 1.0)))

                angle_int = int(angle)

                if angle_int > 45:
                    ser.write(bytes('0', encoding='ascii'))
                elif angle_int > 25:
                    ser.write(bytes('1', encoding='ascii'))
                elif angle_int > 10:
                    ser.write(bytes('2', encoding='ascii'))
                else:
                    ser.write(bytes('3', encoding='ascii'))

                # 角度の出力
                cv2.putText(image, f'Angle: {angle_int}degree', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
        # 画像の表示
        cv2.imshow('Hand Peace Angle Detection', image)
        
        # 'q'キーで終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            ser.write(bytes('3', encoding='ascii'))
            break

# リリース
cap.release()
cv2.destroyAllWindows()
ser.close() 
