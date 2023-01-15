Este documento es una guía sobre un trabajo práctico, realizado en la Universidad de Alicante, para la asignatura de "Robots Móviles". Los integrantes del grupo son: Carmen Losantos Pulido, Luis Pérez-Brotons Ballester y Carlos Dorado Pérez.

El objetivo de la práctica es realizar una aplicación que pueda ser útil para un robot de rescate y se harán las diversas pruebas con el Turtlebot3 SIMULADO.

En la carpeta scripts se encontrarán tres códigos (python): turtlebot.py, reconocimineto_gestos.py y test_movebase.py
El código de reconocimiento_gestos.py utiliza la librería mediapipe (es necesario tenerla instalada) y las imágenes que se encuentran en la carpeta. Estas imágenes son los gestos que se han utilizado y al ejecutar el archivo saldrán en la parte derecha de la ventana de la cámara para saber en todo momento en el estado en el que nos encontramos. Empezando por arriba, los 3 primeros gestos es para cambiar de estado, en el código y en pantalla se muestra que hace cada uno, y los 2 gestos de abajo son para cambiar de opción dentro del estado en el que nos encontramos. Esto serviría para ir mapeando las zonas que han sido visitadas en busca de la persona perdida.
Se recomienda ver el último vídeo para entender mejor su funcionamiento.


El código de reconocimiento_gestos.py publica en el topic /gestos un resultado y por otro lado, el código turtlebot.py se suscribe al topic /gestos para recibir el resultado y poder publicar al turtlebot velocidades lineales y angulares según lo que haya recibido.


Por último, el código test_movebase.py se ejecuta cuando el dedo índice se sitúa encima del botón azul que dice "Volver", para volver al origen o punto deseado y de esta manera guiar a la persona perdida hasta la salida.

Estos códigos, han sido creados con el fin de teleoperar el turtlebot con gestos, para poder hacer una simulación en casa hay que seguir los siguientes pasos:
1º.- Extraer el paquete turtlebot_gestos en la carpeta src del espacio de trabajo catkin_ws
2º.- Abrir una terminal en catkin_ws y escribir:
catkin_make
source devel/setup.bash
roscore
3º.- Abrir en la carpeta que se encuentran reconocimiento_gestos.py y turtlebot.py una terminal y escribir (para abrir un para en Gazebo):
export TURTLEBOT3_MODEL=burger
roslaunch turtlebot3_gazebo turtlebot3_world.launch
4º.- Abrir otra terminal en la misma ubicación para abrir rviz:
export TURTLEBOT3_MODEL=burger
roslaunch turtlebot3_slam turtlebot3_slam.launch slam_methods:=gmapping
5º.- Abrir dos terminales y en una ejecutar:
python3 turtlebot.py
Y en la otra:
python3 reconocimiento_gestos.py

Por último, un ejemplo de vídeo demostrativo de los pasos explicados anteriormente: https://youtu.be/VLlYDgmMJiU
Y el vídeo demostrativo de mandarle de vuelta al origen: https://youtu.be/SwTCrvA_DTg

Para el último vídeo hace falta guardar el mapa que se ha mapeado con el siguiente comando:
rosrun map_server map_saver -f ~/mapa
Y ejecutar en vez del comando de gmapping:
roslaunch turtlebot3_navigation turtlebot3_navigation.launch map_file:=$HOME/mapa.yaml
Situar bien el mapa con la herramienta "2D Pose Estimate".


En caso de que se quisiera más información sobre esta práctica se adjunta un enlace a la memoria realizada: https://es.overleaf.com/read/pgchzhzhgcgd

