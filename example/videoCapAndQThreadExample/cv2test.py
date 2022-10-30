import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(model_complexity=0,
                       max_num_hands=1,
                       min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    ret, frame = cap.read()  # 讀取影片的每一幀
    if not ret:
        print("Cannot receive frame")  # 如果讀取錯誤，印出訊息
        break
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # 將節點和骨架繪製到影像中
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())
    cv2.imshow('test', frame)  # 如果讀取成功，顯示該幀的畫面
    if cv2.waitKey(1) == ord('q'):  # 每一毫秒更新一次，直到按下 q 結束
        break
cap.release()  # 所有作業都完成後，釋放資源
cv2.destroyAllWindows()
