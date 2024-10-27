import cv2
import time
import math

import mediapipe as mp
import keyboard


def findDistance(p1x, p1y, p2x, p2y):
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

def determineWinner(predictions):
    [p1, p2] = predictions
    p1Win = [["paper", "rock"], ["scissors", "paper"], ["rock", "scissors"]]
    p2Win = [["rock", "paper"], ["paper", "scissors"], ["scissors", "rock"]]
    if [p1, p2] in p1Win:
        return "Player 1 Win!"
    elif [p1, p2] in p2Win:
        return "Player 2 Win!"
    else:
        return "tie"


tempTimer = time.time()
start = time.time()
gameDone = True
cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=2)
mpDraw = mp.solutions.drawing_utils
fingerLandmarks = [4, 8, 12, 16, 20]
predictionsList = []

cDownT = 5
gameData = [0,0,0]
roundStart = False


temp = True

colourList = [(255,0,0),(0,0,255)]
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    height, width, c = img.shape
    if results.multi_hand_landmarks:
        predictionsList = []


        for handNum, handLms in enumerate(results.multi_hand_landmarks):

            # visual landmarks
            for id, lm in enumerate(handLms.landmark):
                
                cx, cy = int(lm.x * width), int(lm.y * height)
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
            #             (31, 209, 79), 3)

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

        
            cv2.putText(img, "player1", (round(player1.landmark[9].x*width),30), cv2.FONT_HERSHEY_PLAIN, 3,(31, 209, 79), 3)
            cv2.putText(img, predictionsList[0], (round(player1.landmark[9].x*width),60), cv2.FONT_HERSHEY_PLAIN, 3,(31, 209, 79), 3)


            cv2.putText(img, "player2", (round(player2.landmark[9].x*width),30), cv2.FONT_HERSHEY_PLAIN, 3,(31, 209, 79), 3)
            cv2.putText(img, predictionsList[1], (round(player2.landmark[9].x*width),60), cv2.FONT_HERSHEY_PLAIN, 3,(31, 209, 79), 3)
    
    if keyboard.is_pressed('s') and gameDone:
        gameDone = False

    if gameDone:
        message = "Press 's' to Start"
        msgSize = 3

    else:
        if not roundStart:
            if 3 in gameData[0:1]:
                
                if gameData[0] == 3:
                    message = "Game Over, Player 1 Wins!"
                else:
                    message = "Game Over, Player 2 Wins!"
                msgSize = 3
                gameData = [0,0,0]
            else:
                if temp:
                    print(gameData)
                    temp = False
                message = "Round "+str(sum(gameData)+1)+" Press 'r' to begin"
                msgSize = 2
        else:
            if (cDownT - math.floor(time.time() - roundStartTime)) >= 0:
                # print(math.floor(time.time() - roundStartTime >= 0))
                message = "starting in " + str(cDownT - math.floor(time.time() - roundStartTime))
                msgSize = 2
                # print(message)
                cv2.putText(img, message, (50,height-30), cv2.FONT_HERSHEY_PLAIN, 2,(31, 209, 79), 3)
            else:
                print(predictionsList)
                winner = (determineWinner(predictionsList))
                temp = True
                message = winner
                if (winner == "Player 1 Win!"):
                    gameData[0] += 1
                elif (winner == "Player 2 Win!"):
                    gameData[1] += 1
                else:
                    gameData[2] += 1
                roundStart = False
                
                pass
        if keyboard.is_pressed('r'):
            
            roundStart = True
            roundStartTime = time.time()
    cv2.putText(img, message, (50,height-30), cv2.FONT_HERSHEY_PLAIN, msgSize,(31, 209, 79), 3)
    cv2.putText(img, ("Player 1: "+ str(gameData[0])), (50,35), cv2.FONT_HERSHEY_PLAIN, 2,(31, 209, 79), 3)
    cv2.putText(img, ("Player 2: "+ str(gameData[1])), (width-300,35), cv2.FONT_HERSHEY_PLAIN, 2,(31, 209, 79), 3)

        
        # gameDone = False



    # print(time.time() - start)

    # if len(predictionsList) <2:
    #     cv2.putText(img, "Please have both hands in frame", (30,30), cv2.FONT_HERSHEY_PLAIN, 3,(31, 209, 79), 3)

        


    cv2.imshow("Image", img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()

cv2.destroyAllWindows()