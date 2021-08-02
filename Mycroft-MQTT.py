from __future__ import division
import os
from precise_runner import PreciseEngine, PreciseRunner
import paho.mqtt.client as mqtt
from time import sleep

precise_path = os.path.join(os.path.dirname(__file__), "precise-engine/precise-engine")
ww_path = os.path.join(os.path.dirname(__file__), "hey-dsr/hey-dsr.pb")


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
    else:
        print("Connect returned result code: " + str(rc))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("Received message: " + msg.topic + " -> " + msg.payload.decode("utf-8"))


# create the client
client = mqtt.Client()

# enable TLS
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)

# set username and password
client.username_pw_set("JetsonNano", "G1obalDWS")

# connect to HiveMQ Cloud on port 8883
client.connect("df50a90e1ca64a16a186f38cb2d14114.s2.eu.hivemq.cloud", 8883)

# subscribe to the topic "CovidApp/Activate"
client.subscribe("CovidApp/Activate")


def activate_app():
    print("##### WAKE WORD DETECTED #####\n")

    client.loop_start()

    client.on_connect = on_connect
    client.on_message = on_message

    client.publish("CovidApp/Activate", "ACTIVATE")

    client.loop_stop()

    return


def main():
    engine = PreciseEngine(precise_path, ww_path)
    runner = PreciseRunner(engine, on_activation=lambda: activate_app())
    runner.start()

    # Sleep forever
    while True:
        sleep(100)


for i in range(0, 1):
    main()
