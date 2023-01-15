#!/usr/bin/python
# -*- coding: utf-8 -*-
import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from actionlib_msgs.msg import GoalStatus
import sys

#Uso de la acción move_base en ROS para moverse a un punto determinado
#En ROS una acción es como una petición de un "cliente" a un "servidor"
#En este caso este código es el cliente y el servidor es ROS
#(en concreto el nodo de ROS 'move_base')
class ClienteMoveBase:
    def __init__(self):
        #creamos un cliente ROS para la acción, necesitamos el nombre del nodo 
        #y la clase Python que implementan la acción
        #Para mover al robot, estos valores son "move_base" y MoveBaseAction
        self.client =  actionlib.SimpleActionClient('move_base',MoveBaseAction)
        #esperamos hasta que el nodo 'move_base' esté activo`
        self.client.wait_for_server()

    def moveTo(self, x, y):
        #un MoveBaseGoal es un punto objetivo al que nos queremos mover
        goal = MoveBaseGoal()
        #sistema de referencia que estamos usando
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.pose.position.x = x   
        goal.target_pose.pose.position.y = y
        #La orientación es un quaternion. Tenemos que fijar alguno de sus componentes
        goal.target_pose.pose.orientation.w = 1.0

        #enviamos el goal 
        self.client.send_goal(goal)
        #vamos a comprobar cada cierto tiempo si se ha cumplido el goal
        #get_state obtiene el resultado de la acción 
        state = self.client.get_state()
        #ACTIVE es que está en ejecución, PENDING que todavía no ha empezado
        while state==GoalStatus.ACTIVE or state==GoalStatus.PENDING:
            rospy.Rate(10)   #esto nos da la oportunidad de escuchar mensajes de ROS
            state = self.client.get_state()
        return self.client.get_result()

if __name__ == "__main__":
    '''
    if len(sys.argv) <= 2:
        print("Uso: " + sys.argv[0] + " x_objetivo y_objetivo")
        exit()   
    '''   
    rospy.init_node('prueba_clientemovebase')
    cliente = ClienteMoveBase()
    #result = cliente.moveTo(float(sys.argv[1]), float(sys.argv[2]))
    result = cliente.moveTo(float(-2.04), float(-0.53))
    print(result)
    if result:
        rospy.loginfo("Goal conseguido!")
