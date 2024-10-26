import cv2
import mediapipe as mp
import time

def findDistance(p1x, p1y, p2x, p2y, length=640, height=480):
    return ((p2x - p1x) ** 2 + (p2y - p1y) ** 2) ** 0.5

def determineType(hand):
    refPoints = [[8,5],[12,9],[16,13],[20,17],[0,5]] #ORDER: index finger to pinky, palm
    handDistList = [0,0,0,0,0]
    for i in range(5):
        dist = findDistance(hand.landmark[(refPoints[i][0])].x, hand.landmark[(refPoints[i][0])].y, hand.landmark[(refPoints[i][1])].x, hand.landmark[(refPoints[i][1])].y)
        handDistList[i] = (dist)
    ratios = []
    for i in range(4):
        ratios.append(handDistList[i]/handDistList[-1])

    prediction = ""
    theoretical = [.9,1,.9,.7]
    state = []
    for n, index in enumerate(ratios):
        difference = abs(abs(index)-theoretical[n])
        if difference < 0.3:
            state.append(True)
        else:
            state.append(False)
    if state == [True, True, True, True]:
        prediction = "paper"
    elif state == [False, False, False, False]:
        prediction = "rock"
    else:
        prediction = "scissors"
    return prediction

start = time.time()

cap = cv2.VideoCapture(2)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils
fingerLandmarks = [4, 8, 12, 16, 20]


colourList = [(255,0,0),(0,0,255)]
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        predictionsList = []


        for handNum, handLms in enumerate(results.multi_hand_landmarks):

            # visual landmarks
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                if id in fingerLandmarks:
                    cv2.circle(img, (cx, cy), 15, colourList[handNum], cv2.FILLED)
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            prediction = determineType(handLms)
            predictionsList.append(prediction)
            # print(handNum+1, "state is", prediction)

            # if handNum == 0:
            #         placement = (0,50)
            # else:
            #     placement = (300,50)
            # cv2.putText(img, prediction, placement, cv2.FONT_HERSHEY_PLAIN, 3,
            #             (255, 0, 255), 3)

        # if len(predictionsList) == 2:
        #     print("player 1:",round(results.multi_hand_landmarks[0].landmark[9].x,2))
        #     print("player 2:",round(results.multi_hand_landmarks[1].landmark[9].x,2))
        if len(predictionsList) == 2:
            if results.multi_hand_landmarks[0].landmark[9].x <= results.multi_hand_landmarks[1].landmark[9].x:
                player1 = results.multi_hand_landmarks[0]
                player2 = results.multi_hand_landmarks[1]
            else:
                player1 = results.multi_hand_landmarks[1]
                player2 = results.multi_hand_landmarks[0]

        
            cv2.putText(img, "player1", (round(player1.landmark[9].x*640),30), cv2.FONT_HERSHEY_PLAIN, 3,(255, 0, 255), 3)
            cv2.putText(img, predictionsList[0], (round(player1.landmark[9].x*640),60), cv2.FONT_HERSHEY_PLAIN, 3,(255, 0, 255), 3)


            cv2.putText(img, "player2", (round(player2.landmark[9].x*640),30), cv2.FONT_HERSHEY_PLAIN, 3,(255, 0, 255), 3)
            cv2.putText(img, predictionsList[1], (round(player2.landmark[9].x*640),60), cv2.FONT_HERSHEY_PLAIN, 3,(255, 0, 255), 3)

        


    cv2.imshow("Image", img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()

cv2.destroyAllWindows()