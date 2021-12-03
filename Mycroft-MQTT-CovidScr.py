from __future__ import division
import os
import time
from time import sleep

from precise_runner import PreciseEngine, PreciseRunner
import paho.mqtt.client as mqtt

precise_path = os.path.join(os.path.dirname(__file__), "precise-engine/precise-engine")
ww_path = os.path.join(os.path.dirname(__file__), "hey-dsr/hey-dsr.pb")


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

client = mqtt.Client("LinuxMachine-1")
broker = "192.168.99.151"  # Change to IP address of the MQTT broker
topic = "CovidApp/Activate"  # Change to any topic name you want. The same topic here should be used in the Android app
message = "ACTIVATE"  # Change to whichever message you want

client.on_connect = on_connect


def activate_app():
    print("##### WAKE WORD DETECTED #####")

    print("Connecting to broker", broker)
    client.connect(broker)

    client.loop_start()

    while not client.connected_flag:  # wait in loop
        print("In wait loop")
        time.sleep(1)

    client.publish(topic, message, qos=2)
    print("MQTT message sent")

    client.loop_stop()
    client.disconnect()
    print("Disconnected successfully\n")


def main():
    engine = PreciseEngine(precise_path, ww_path)
    runner = PreciseRunner(engine, on_activation=lambda: activate_app())
    runner.start()

    # Sleep forever
    while True:
        sleep(100)


for i in range(0, 1):
    main()
