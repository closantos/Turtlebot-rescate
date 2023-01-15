#!/usr/bin/env python
import rospy
import math, sys
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import *
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from actionlib_msgs.msg import GoalStatus
#import subprocess
import os
#----------------
import smach
import threading

velocidad = 0
giro = 0
res = 0


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
        #subprocess.run(["rosrun", "map_server", "map_saver", "-f", "map"])
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


# ------------------------------------ FUNCIÓN DE MOVER CON GESTOS ---------------------------------------
def moverse(data):
	global velocidad, giro, res
	res = int(data.data)
	#print(res)
	#dar vuelta valores del láser
	#data.ranges = list(data.ranges)
	#data.ranges.reverse()

	speed = Twist()
	
	'''
	# RES = 0 -> PARAMOS ROBOT
	if res == 0:
		velocidad = 0
		giro = 0
	
	# ESTADO 1
	if res == 1:                    # AVANZA RECTO
		velocidad = 0.30            # velocidad lineal constante
		giro = 0                    # y angular a cero
	elif res == 2:                  # RETROCEDE
		velocidad = -0.30
		giro = 0

	# ESTADO 2
	if res == 3:                    # AVANZA Y DERECHA
		velocidad = 0.30            # velocidad lineal
		giro = -0.4                 # y angular levemente
	elif res == 4:                  # AVANZA E IZQUIERDA
		velocidad = 0.30
		giro = 0.4

	# ESTADO 3
	if res == 5:                    # QUIETO GIRO DERECHA
		velocidad = 0               # velocidad lineal a cero
		giro = -0.4                 # giro angular rápido
	elif res == 6:                  # QUIETO GIRO IZQUIERDA
		velocidad = 0
		giro = 0.4

	#ESTADO 4
	if res == 7:
		#rospy.Subscriber("/scan", LaserScan, odometria)
		#odometria()
		print("---------------------------- ODOMETRIA ")
		#os.system("python3 test_movebase.py")
	'''

	if res != 7:
		speed.linear.x = float(velocidad)
		speed.angular.z = float(giro)
        #pub = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size=10)  #REAL
		pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)  #simulacion

		pub.publish(speed)

# Definimos estado: Detenemos Robot
class Stop(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=['Cambiamos a Estado 1','Cambiamos a Estado 2','Cambiamos a Estado 3','Cambiamos a Estado 4','Finalizado'])
		self.estado = 0

	def execute(self, userdata):
		global velocidad, giro, res

		rospy.loginfo('ESTADO ACTUAL DEL ROBOT: Robot detenido')

		# La variable res es una variable global que determina en que estado nos encontramos
		# Esperamos mientras la variable res siga indicando el valor 0
		self.estado = 0
		while res == 0:		
			velocidad = 0
			giro = 0

		# Cuando res cambia, cambiamos de estado:
		self.estado = res

		# En función de su valor, vamos a un estado u otro
		if self.estado == 1 or self.estado == 2:
			return 'Cambiamos a Estado 1'
		elif self.estado == 3 or self.estado == 4:
			return 'Cambiamos a Estado 2'
		elif self.estado == 5 or self.estado == 6:
			return 'Cambiamos a Estado 3'
		elif self.estado == 7:
			return 'Cambiamos a Estado 4'
		else:
			return 'Finalizado'

# Definimos estado: Movimiento Lineal
class MovLineal(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=['Cambiamos a Estado 0','Cambiamos a Estado 2','Cambiamos a Estado 3','Cambiamos a Estado 4','Finalizado'])
		self.estado = 1

	def execute(self, userdata):
		global velocidad, giro, res

		rospy.loginfo('ESTADO ACTUAL DEL ROBOT: Robot en movimiento lineal')

		# La variable res es una variable global que determina en que estado nos encontramos
		# Esperamos mientras la variable res siga indicando el valor 0
		self.estado = res
		while res == 1 or res == 2:
			if res == 1:                    # AVANZA RECTO
				rospy.loginfo('      Avanzace')
				velocidad = 0.30            # velocidad lineal constante
				giro = 0                    # y angular a cero
			elif res == 2:                  # RETROCEDE
				rospy.loginfo('      Retroceso')
				velocidad = -0.30
				giro = 0	

		# Cuando res cambia, cambiamos de estado:
		self.estado = res

		# En función de su valor, vamos a un estado u otro
		if self.estado == 0:
			return 'Cambiamos a Estado 0'
		elif self.estado == 3 or self.estado == 4:
			return 'Cambiamos a Estado 2'
		elif self.estado == 5 or self.estado == 6:
			return 'Cambiamos a Estado 3'
		elif self.estado == 7:
			return 'Cambiamos a Estado 4'
		else:
			return 'Finalizado'

# Definimos estado: Movimiento Con Giro
class MovGiro(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=['Cambiamos a Estado 0','Cambiamos a Estado 1','Cambiamos a Estado 3','Cambiamos a Estado 4','Finalizado'])
		self.estado = 3

	def execute(self, userdata):
		global velocidad, giro, res

		rospy.loginfo('ESTADO ACTUAL DEL ROBOT: Robot en movimiento + giros')

		# La variable res es una variable global que determina en que estado nos encontramos
		# Esperamos mientras la variable res siga indicando el valor 0
		self.estado = res
		while res == 3 or res == 4:
			if res == 3:                    # AVANZA Y DERECHA
				rospy.loginfo('      Avanzace girando hacia la derecha')
				velocidad = 0.30            # velocidad lineal
				giro = -0.4                 # y angular levemente
			elif res == 4:                  # AVANZA E IZQUIERDA
				rospy.loginfo('      Avanzace girando hacia la izquierda')
				velocidad = 0.30
				giro = 0.4


		# Cuando res cambia, cambiamos de estado:
		self.estado = res

		# En función de su valor, vamos a un estado u otro
		if self.estado == 0:
			return 'Cambiamos a Estado 0'
		elif self.estado == 1 or self.estado == 2:
			return 'Cambiamos a Estado 1'
		elif self.estado == 5 or self.estado == 6:
			return 'Cambiamos a Estado 3'
		elif self.estado == 7:
			return 'Cambiamos a Estado 4'
		else:
			return 'Finalizado'

# Definimos estado: Giro En Parado
class Giro(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=['Cambiamos a Estado 0','Cambiamos a Estado 1','Cambiamos a Estado 2','Cambiamos a Estado 4','Finalizado'])
		self.estado = 5

	def execute(self, userdata):
		global velocidad, giro, res

		rospy.loginfo('ESTADO ACTUAL DEL ROBOT: Robot girando en parado')

		# La variable res es una variable global que determina en que estado nos encontramos
		# Esperamos mientras la variable res siga indicando el valor 0
		self.estado = res
		while res == 5 or res == 6:
			if res == 5:                    # QUIETO GIRO DERECHA
				rospy.loginfo('      Giro en parado hacia la derecha')
				velocidad = 0               # velocidad lineal a cero
				giro = -0.4                 # giro angular rápido
			elif res == 6:                  # QUIETO GIRO IZQUIERDA
				rospy.loginfo('      Giro en parado hacia la izquierda')
				velocidad = 0
				giro = 0.4

		# Cuando res cambia, cambiamos de estado:
		self.estado = res

		# En función de su valor, vamos a un estado u otro
		if self.estado == 0:
			return 'Cambiamos a Estado 0'
		elif self.estado == 1 or self.estado == 2:
			return 'Cambiamos a Estado 1'
		elif self.estado == 3 or self.estado == 4:
			return 'Cambiamos a Estado 2'
		elif self.estado == 7:
			return 'Cambiamos a Estado 4'
		else:
			return 'Cambiamos a Finalizado'

# Definimos estado: HOME
class HOME(smach.State):
	def __init__(self):
		smach.State.__init__(self, outcomes=['Cambiamos a Estado 0','Cambiamos a Estado 1','Cambiamos a Estado 2','Cambiamos a Estado 3','Finalizado'])
		self.estado = 7

	def execute(self, userdata):
		global velocidad, giro, res

		rospy.loginfo('ESTADO ACTUAL DEL ROBOT: Vuelta a HOME')

		# La variable res es una variable global que determina en que estado nos encontramos
		# Esperamos mientras la variable res siga indicando el valor 0
		self.estado = res
		while res == 7:
			#rospy.Subscriber("/scan", LaserScan, odometria)
			#odometria()
			print("---------------------------- ODOMETRIA ")
			os.system("python3 test_movebase.py")

		# Cuando res cambia, cambiamos de estado:
		self.estado = res

		# En función de su valor, vamos a un estado u otro
		if self.estado == 0:
			return 'Cambiamos a Estado 0'
		elif self.estado == 1 or self.estado == 2:
			return 'Cambiamos a Estado 1'
		elif self.estado == 3 or self.estado == 4:
			return 'Cambiamos a Estado 2'
		elif self.estado == 5 or self.estado == 6:
			return 'Cambiamos a Estado 3'
		else:
			return 'Finalizado'

if __name__ == '__main__':
	rospy.init_node('reconocimiento_gestos')
	#rospy.Subscriber("/gestos", String, moverse)
	#rospy.Subscriber("/base_scan", LaserScan, odometria) # REAL
	#rospy.Subscriber("/scan", LaserScan, odometria) # simulacion

	# MAQUINA DE ESTADOS SMACH
	
	#Con esto funciona
	hilo_gestos = threading.Thread(target = rospy.Subscriber("/gestos", String, moverse))
	hilo_gestos.start()

	#Si quieres descomentar y comentar lo otro a ver si así funciona
    #rospy.Subscriber("/gestos", String, moverse)

	# Create a SMACH state machine
	sm = smach.StateMachine(outcomes=['FIN'])

    # Open the container
	with sm:
        # Add states to the container

		# Detenemos los motores del turtlebot
		smach.StateMachine.add('Detenemos Robot', Stop(), 
                            transitions={'Cambiamos a Estado 1':'Movimiento Lineal','Cambiamos a Estado 2':'Movimiento Con Giro','Cambiamos a Estado 3':'Giro En Parado','Cambiamos a Estado 4':'Vuelta A Home','Finalizado':'FIN'})
		# Movimiento lineal: AVANCE - RETROCESO
		smach.StateMachine.add('Movimiento Lineal', MovLineal(), 
                            transitions={'Cambiamos a Estado 0':'Detenemos Robot','Cambiamos a Estado 2':'Movimiento Con Giro','Cambiamos a Estado 3':'Giro En Parado','Cambiamos a Estado 4':'Vuelta A Home','Finalizado':'FIN'})
		# Movimiento con giro: GIRO DERECHA - GIRO IZQUIERDA
		smach.StateMachine.add('Movimiento Con Giro', MovGiro(), 
                            transitions={'Cambiamos a Estado 0':'Detenemos Robot','Cambiamos a Estado 1':'Movimiento Lineal','Cambiamos a Estado 3':'Giro En Parado','Cambiamos a Estado 4':'Vuelta A Home','Finalizado':'FIN'})
		# Giro en parado: GIRO IZQUIERDA - GIRO DERECHA
		smach.StateMachine.add('Giro En Parado', Giro(), 
                            transitions={'Cambiamos a Estado 0':'Detenemos Robot','Cambiamos a Estado 1':'Movimiento Lineal','Cambiamos a Estado 2':'Movimiento Con Giro','Cambiamos a Estado 4':'Vuelta A Home','Finalizado':'FIN'})
		# Odometría: VUELTA A LA POS INICIAL
		smach.StateMachine.add('Vuelta A Home', HOME(), 
                            transitions={'Cambiamos a Estado 0':'Detenemos Robot','Cambiamos a Estado 1':'Movimiento Lineal','Cambiamos a Estado 2':'Movimiento Con Giro','Cambiamos a Estado 3':'Giro En Parado','Finalizado':'FIN'})
		

    # Execute SMACH plan
	outcome = sm.execute()
	
	rospy.spin()
