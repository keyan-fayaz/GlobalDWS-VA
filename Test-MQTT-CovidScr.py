import time
from time import sleep

import paho.mqtt.client as mqtt


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True  # set flag
        print("Connected successfully")
    else:
        print("Bad connection! Return code: " + str(rc))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("Received message: " + msg.topic + " -> " + msg.payload.decode("utf-8"))


mqtt.Client.connected_flag = False  # create flag IN class

client = mqtt.Client("GlobalDWS-Python")
broker = "192.168.99.151"  # Change to IP address of the MQTT broker
topic = "CovidApp/Activate"  # Change to any topic name you want. The same topic here should be used in the Android app
message = "ACTIVATE"  # Change to whichever message you want

client.on_connect = on_connect

print("Connecting to broker", broker)
client.connect(broker)

client.loop_start()

while not client.connected_flag:  # wait in loop
    print("In wait loop")
    time.sleep(1)

client.publish(topic, message, qos=2)
print("MQTT message sent")

client.loop_stop()
client.disconnect()  # disconnect
print("Disconnected successfully")
