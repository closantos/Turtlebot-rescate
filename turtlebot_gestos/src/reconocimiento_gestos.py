#!/usr/bin/env python

import rospy
from std_msgs.msg import String

# Libreria mediapipe para reconocimiento de gestos
import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture(1)

# Carga la imagen en un objeto "imagen"
img_est1 = cv2.imread("estado1.jpg")
img_est2 = cv2.imread("estado2.jpg")
img_est3 = cv2.imread("estado3.jpg")
img_dch = cv2.imread("izq.jpeg")
img_izq = cv2.imread("dcha.jpeg")

# Cambio de tamaño
alto = 144
ancho = 250
img_est1 = cv2.resize(img_est1, (ancho, alto))
img_est2 = cv2.resize(img_est2, (ancho, alto))
img_est3 = cv2.resize(img_est3, (ancho, alto))
img_izq = cv2.resize(img_izq, (ancho, alto))
img_dch = cv2.resize(img_dch, (ancho, alto))
img_gestos = np.concatenate((img_est1, img_est2, img_est3, img_dch, img_izq), axis=0) 

def gestos():
    estado = 1
    estado_ant = 1
    count = 0
    N_frames = 5
    res = 0
    odometria = False

    # Declaro que mi nodo va a publicar al topic /gestos
    pub = rospy.Publisher('gestos', String, queue_size=10)
    # Nombre de mi nodo 'reconocimiento_gestos'
    rospy.init_node('reconocimiento_gestos', anonymous=True)
    rate = rospy.Rate(10)   #10hz
    # Codigo de reconocimiento de gestos
    while not rospy.is_shutdown():
        with mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5) as hands:
                while True:
                    ret, frame = cap.read()
                    if ret == False:
                        break

                    height, width, _ = frame.shape
                    frame = cv2.flip(frame, 1)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    results = hands.process(frame_rgb)

                    # Concatena el frame y img_gestos
                    frame = np.concatenate((frame, img_gestos), axis=1)

                    '''if results.multi_hand_landmarks is not None:
                        for hand_landmarks in results.multi_hand_landmarks:
                            mp_drawing.draw_landmarks(
                                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(0,255,255), thickness=3, circle_radius=5),
                                mp_drawing.DrawingSpec(color=(255,0,255), thickness=4, circle_radius=5))'''

                    if results.multi_hand_landmarks is not None:    
                    # Accediendo a los puntos de referencia, de acuerdo a su nombre
                        for hand_landmarks in results.multi_hand_landmarks:
                            # Para detectar dedo indice y pulgar
                            x1 = int(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x * width)
                            y1 = int(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y * height)

                            x2 = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * width)
                            y2 = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * height)
                            
                            # Para detectar los 3 dedos restantes de la mano
                            x3 = int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x * width)
                            y3 = int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y * height)

                            x4 = int(hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].x * width)
                            y4 = int(hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y * height)

                            x5 = int(hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].x * width)
                            y5 = int(hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y * height)

                            cv2.circle(frame, (x1, y1), 3,(255,0,0),3)
                            cv2.circle(frame, (x2, y2), 3,(255,0,0),3)
                            cv2.circle(frame, (x3, y3), 3,(255,0,0),3)
                            cv2.circle(frame, (x4, y4), 3,(255,0,0),3)
                            cv2.circle(frame, (x5, y5), 3,(255,0,0),3)

                        #print(x2, y2)
                        print("ESTADO = ", estado)
                        if estado == 1:
                            cv2.putText(frame, "Estado 1",(1300, 140), 1, 2, (0, 0, 255), 3)
                            cv2.putText(frame, "Estado 2",(1300, 270), 1, 2, (255, 0, 0), 3)
                            cv2.putText(frame, "Estado 3",(1300, 410), 1, 2, (255, 0, 0), 3)
                            cv2.putText(frame, "AVANZAR",(1300, 710), 1, 2, (255, 0, 0), 3)
                            cv2.putText(frame, "RETROCEDER",(1300, 570), 1, 2, (255, 0, 0), 3)
                            # COMPROBAMOS LAS X PARA MOVERNOS AVANZAR O RETROCEDER
                            if x1 > x2 and y2 > y1 and y3 > y1 and y4 > y1 and y5 > y1:
                                # DEVOLVEMOS UN 1 PARA SABER QUE ES AVANZAR
                                res = 1
                                cv2.putText(frame, "AVANZAR",(1300, 710), 1, 2, (0, 0, 255), 3)

                                print("AVANZA")
                            elif x1 < x2 and y2 > y1 and y3 > y1 and y4 > y1 and y5 > y1:
                                # DEVOLVEMOS UN 2 PARA SABER QUE ES RETROCEDER
                                res = 2
                                cv2.putText(frame, "RETROCEDER",(1300, 570), 1, 2, (0, 0, 255), 3)

                                print("RETROCEDE")
                                
                            else: # COMPROBAMOS EL CAMBIO DE ESTADO
                                if y2 < y1 and y2 < y3 and y2 < y4 and y2 < y5 and y5 < y1 and y5 < y3 and y5 < y4:
                                    # CAMBIAMOS AL ESTADO 2
                                    estado = 2
                                elif y1 < y2 and y1 < y3 and y1 < y4 and y5 < y2 and y5 < y3 and y5 < y4:
                                    # CAMBIAMOS AL ESTADO 3
                                    estado = 3
                                elif x2 > width-150  and y2 < 100:
                                    # VOLVER A ORIGEN
                                    estado = 4
                                    res = 7
                                    print("Odometria")
                                else:
                                    # NOS QUEDAMOS EN EL MISMO ESTADO
                                    estado = 1
                                    res = 0
                                    print("Ningun gesto")


                        elif estado == 2:
                            cv2.putText(frame, "Estado 1",(1300, 140), 1, 2, (255, 0, 0), 3)
                            cv2.putText(frame, "Estado 2",(1300, 270), 1, 2, (0, 0, 255), 3)
                            cv2.putText(frame, "Estado 3",(1300, 410), 1, 2, (255, 0, 0), 3)
                            cv2.putText(frame, "AVANZA Y DERECHA",(1300, 710), 1, 1, (255, 0, 0), 2)
                            cv2.putText(frame, "AVANZA E IZQUIERDA",(1300, 570), 1, 1, (255, 0, 0), 2)
                            # MOVEMOS DERECHA E IZQUIERDA MIENTRAS EL ROBOT AVANZA
                            if x1 > x2 and y2 > y1 and y3 > y1 and y4 > y1 and y5 > y1:
                                # DEVOLVEMOS UN 3 PARA SABER QUE ES DERECHA
                                res = 3
                                cv2.putText(frame, "AVANZA Y DERECHA",(1300, 710), 1, 1, (0, 0, 255), 2)

                                print("DERECHA")
                            elif x1 < x2 and y2 > y1 and y3 > y1 and y4 > y1 and y5 > y1:
                                # DEVOLVEMOS UN 4 PARA SABER QUE ES IZQUIERDA
                                res = 4
                                cv2.putText(frame, "AVANZA E IZQUIERDA",(1300, 570), 1, 1, (0, 0, 255), 2)

                                print("IZQUIERDA")
                            else: # COMPROBAMOS EL CAMBIO DE ESTADO
                                if y2 < y1 and y2 < y4 and y2 < y5 and y3 < y1 and y3 < y2 and y3 < y4 and y3 < y5:
                                    # CAMBIAMOS AL ESTADO 1
                                    estado = 1
                                elif y1 < y2 and y1 < y3 and y1 < y4 and y5 < y2 and y5 < y3 and y5 < y4:
                                    # CAMBIAMOS AL ESTADO 3
                                    estado = 3
                                elif x2 > width-150 and y2 < 100:
                                    # VOLVER A ORIGEN
                                    estado = 4
                                    res = 7
                                    print("Odometria")
                                else:
                                    # NOS QUEDAMOS EN EL MISMO ESTADO
                                    estado = 2
                                    res = 0
                                    print("Ningun gesto")
                        
                        elif estado == 3:
                            cv2.putText(frame, "Estado 1",(1300, 140), 1, 2, (255, 0, 0), 3)
                            cv2.putText(frame, "Estado 2",(1300, 270), 1, 2, (255, 0, 0), 3)
                            cv2.putText(frame, "Estado 3",(1300, 410), 1, 2, (0, 0, 255), 3)
                            cv2.putText(frame, "DERECHA",(1300, 710), 1, 2, (255, 0, 0), 3)
                            cv2.putText(frame, "IZQUIERDA",(1300, 570), 1, 2, (255, 0, 0), 3)
                            # DERECHA O IZQUIERDA MIENTRAS EL ROBOT ESTA QUIETO
                            if x1 > x2 and y2 > y1 and y3 > y1 and y4 > y1 and y5 > y1:
                                # DEVOLVEMOS UN 5 PARA SABER QUE ES DENTRO
                                res = 5
                                cv2.putText(frame, "DERECHA",(1300, 710), 1, 2, (0, 0, 255), 3)

                                print("DERECHA")
                            elif x1 < x2 and y2 > y1 and y3 > y1 and y4 > y1 and y5 > y1:
                                # DEVOLVEMOS UN 6 PARA SABER QUE ES FUERA
                                res = 6
                                cv2.putText(frame, "IZQUIERDA",(1300, 570), 1, 2, (0, 0, 255), 3)

                                print("IZQUIERDA")
                            else: # COMPROBAMOS EL CAMBIO DE ESTADO
                                if y2 < y1 and y2 < y4 and y2 < y5 and y3 < y1 and y3 < y2 and y3 < y4 and y3 < y5:
                                    # CAMBIAMOS AL ESTADO 1
                                    estado = 1
                                elif y2 < y1 and y2 < y3 and y2 < y4 and y2 < y5 and y5 < y1 and y5 < y3 and y5 < y4:
                                    # CAMBIAMOS AL ESTADO 2
                                    estado = 2
                                elif x2 > width-150  and y2 < 100:
                                    # VOLVER A ORIGEN
                                    estado = 4
                                    res = 7
                                    print("Odometria")
                                else:
                                    # NOS QUEDAMOS EN EL MISMO ESTADO
                                    estado = 3
                                    res = 0
                                    print("Ningun gesto")
                        
                        if x2 > width-150 and y2 < 100:
                            odometria = True
                            print("Dentro")	
                        else:
                            odometria = False

                        #print(estado)
                        # Visualizacion 		coordenadas, tamano letra, color
                        if estado != 0:
                            cv2.putText(frame, "Estado: ",(15, 30), 1, 2, (255, 255, 255), 2)
                            if odometria == False:
                                cv2.circle(frame, (width-100, 60), 30, (255, 0, 0), 50)
                                #cv2.putText(frame, "Ventosa Off",(width-220, 150), 1, 2, (255, 255, 255), 2)
                                cv2.putText(frame, "Volver",(width-170, 150), 1, 2, (255, 255, 255), 2)
                            else:
                                cv2.circle(frame, (width-100, 60), 30, (0, 0, 255), 50)
                                #cv2.putText(frame, "Ventosa On",(width-220, 150), 1, 2, (255, 255, 255), 2)
                                cv2.putText(frame, "Volver",(width-170, 150), 1, 2, (255, 255, 255), 2)
                            if estado == 1:
                                cv2.putText(frame, "1",(150, 30), 1, 2, (255, 255, 255), 2)
                            elif estado == 2:
                                cv2.putText(frame, "2",(150, 30), 1, 2, (255, 255, 255), 2)
                            elif estado == 3:
                                cv2.putText(frame, "3",(150, 30), 1, 2, (255, 255, 255), 2)
                            elif estado == 4:
                                cv2.putText(frame, "Odometria",(150, 30), 1, 2, (255, 255, 255), 2)
                            cv2.putText(frame, "Movimiento: ",(15, 60), 1, 2, (255, 255, 255), 2)
                            if res == 0:
                                cv2.putText(frame, "Ningun gesto",(220, 60), 1, 2, (255, 255, 255), 2)
                            elif res == 1:
                                cv2.putText(frame, "Avanza",(220, 60), 1, 2, (255, 255, 255), 2)
                            elif res == 2:
                                cv2.putText(frame, "Retrocede",(220, 60), 1, 2, (255, 255, 255), 2)
                            elif res == 3:
                                cv2.putText(frame, "Derecha",(220, 60), 1, 2, (255, 255, 255), 2)
                            elif res == 4:
                                cv2.putText(frame, "Izquierda",(220, 60), 1, 2, (255, 255, 255), 2)
                            elif res == 5:
                                cv2.putText(frame, "Derecha",(220, 60), 1, 2, (255, 255, 255), 2)
                            elif res == 6:
                                cv2.putText(frame, "Izquierda",(220, 60), 1, 2, (255, 255, 255), 2)
                            elif res == 7:
                                cv2.putText(frame, "Volviendo",(220, 60), 1, 2, (255, 255, 255), 2)
                    
                    if( estado == estado_ant ):
                        count += 1
                    else:
                        count = 0          
                    estado_ant = estado
                    
                    if( count >= N_frames ):
                        print("     Res: ", res)
                        pub.publish(str(res))
                        rate.sleep()

                    cv2.imshow('Frame',frame)
                    #if odometria == True & cv2.waitKey(1):
                    if ord('q') == 0xFF & cv2.waitKey(1):
                    #if cv2.waitKey(0):
                        break
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        gestos()
    except rospy.ROSInterruptException:
        pass