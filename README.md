# GlobalDWS-VA

This README will be a guide for users unfamiliar with Mycroft's Precise (wake word engine) and Mosquitto MQTT protocol. It will introduce the two topics and give info on the requirements, setup, and usage of each. 

------

## Mycroft Precise

Mycroft Precise is a wake word listener. It can be trained to recognize specific phrases and/or words. The software monitors an audio stream from a microphone and when it recognizes a specific phrase, an event (customizable lambda function) is triggered.

The full documentation of Mycroft Precise is available in [Mycroft Precise's GitHub repo](https://github.com/MycroftAI/mycroft-precise).

### Requirements

- <u>Supported Operating Systems</u>:

  Precise is designed to run on Linux. It is known to work on a variety of Linux distributions including Ubuntu, Debian, and Raspbian.

- <u>Supported Languages</u>:

  Precise only supports specific versions of the Python programming language. It supports Python 3.6 – 3.8.

------

### Setup

The solution was tested on a Jetson Nano, a system with the ARM64/ARMv8-A architecture, running **Ubuntu 20.04 LTS** and with **Python 3.7.10**. So, assuming you want to setup a device with the same architecture (Jetson Nano | Raspberry Pi 4), follow the steps below.

#### Python Setup

Before setting up Mycroft Precise, you must first install Python 3.7 with the header files and its static library with the following commands in the terminal:

```shell
sudo pip3 install --upgrade pip
sudo apt install git
sudo apt update

wget https://www.python.org/ftp/python/3.7.10/Python-3.7.10.tar.xz
tar -xf Python-3.7.10.tar.xz
cd Python-3.7.10
./configure
make
sudo make install

sudo apt-get install python3.7-dev
sudo apt-get install python3.7-venv
```

After that, you should clone the GlobalDWS-VA repo to your home directory and create a py3.7 venv to install the required packages with the following commands:

```shell
cd ~
git clone https://github.com/globaldws/GlobalDWS-VA.git
python3.7 -m venv GlobalDWS-VA/venv/
cd GlobalDWS-VA/
source venv/bin/activate
sudo pip install --upgrade pip
sudo pip install -r requirements.txt
```

Now that we have a Python version that is supported by Mycroft Precise, let’s move on to setting up Precise.

#### Precise Setup

<u>There are two Precise setups</u>:

1. **Source Install**
   - Can be used to *train*, *test*, and *run* wake word detection models and gives access to commands for training and testing from terminal
   - Cannot be installed on *ARM32/64 systems* (Raspberry Pi 4 | Jetson Nano) due to TensorFlow 1.13 compatibility issues with the architecture
2. **Binary Install**
   - Can only be used to *run* models in apps. No commands to train and test models from the terminal 
   - Can be installed and used on *ARM32/64* and *x86-64* (most common for desktops) *systems*

So, basically, if you only want to run a model on a Raspberry Pi 4, for example, then you should choose the Binary Install option. If you want other functionality like training, then you should choose the Source Install option.

##### Option 1 – Source Install

Basically, you only have to clone the repository, run the setup script in the directory where you cloned the repo, and then you’re all set!

```shell
git clone https://github.com/mycroftai/mycroft-precise
cd mycroft-precise
./setup.sh
```

##### Option 2 – Binary Install

Basically, you only have to download the Precise engine and extract it to the directory of your project and then install the Python wrapper.

```shell
cd GlobalDWS-VA/
wget https://github.com/MycroftAI/precise-data/raw/dist/aarch64/precise-engine_0.3.0_aarch64.tar.gz
tar xvf precise-engine_0.3.0_aarch64.tar.gz
source venv/bin/activate
sudo pip3 install precise-runner
```

*This is assuming that you want to install it on ARM64 systems*. 

------

### Usage

#### In Training

With regards to training, the instructions on the GitHub are very clear and do not require any further elaboration. Please refer to Mycroft's guide on [How to train your own wake word](https://github.com/MycroftAI/mycroft-precise/wiki/Training-your-own-wake-word).

Regarding the audio samples used in training, the recordings obtained from most of the team members at GlobalDWS are uploaded to the SharePoint. Please note that these were `m4a` files that were converted to `wav` files using the **`ffmpeg`** command line tool as per the instructions in the guide mentioned above.

The audio samples used in the `not-wake-word/` directory are uploaded to the SharePoint as well. They were obtained from Mozilla’s Common Voice Corpus and two YouTube videos, where each of them were converted to an audio file and then split the file into equal fractions of its original length.

The trained model (last trained as of 09-Sep-21) is uploaded to the SharePoint folder and is available on this GitHub repo as well.

#### In Development

As shown in this code snippet, this is how Precise is used in Python. 

You import the necessary packages as shown below. Then, you pass the location of the precise binary and the protbuf model file to the `PreciseEngine` function and assign it to `engine`. You then pass the PreciseEngine object `engine` and a `lambda function` to the `PreciseRunner` function and assign it to the PreciseRunner object `runner`, and then you launch the precise `runner`.

```python
#!/usr/bin/env python3

from precise_runner import PreciseEngine, PreciseRunner

engine = PreciseEngine('precise-engine/precise-engine', 'my_model_file.pb')
runner = PreciseRunner(engine, on_activation=lambda: print('hello'))
runner.start()

# Sleep forever
from time import sleep
while True:
    sleep(10)

```

Instead of `print(‘hello’)`, I put `activate_va()`, which is a function I defined before `main` to send an MQTT message (*refer to MQTT documentation*) whenever the wake word is detected.

------

## MQTT

MQTT is a lightweight, publish-subscribe network protocol that is used for machine-to-machine (M2M) communication. It is used to send and receive messages between several devices. Since we want to use MQTT offline and without the usage of a third-party cloud MQTT provider, we opted to use Mosquitto MQTT for the broker and Eclipse Paho for the client side (*refer to MQTT documentation*).

### Requirements

- <u>Supported Operating Systems</u>:
  - **Linux**
  - **Android**
  - Windows | macOS
- <u>Supported Languages</u>:
  - **Python**
  - **Java for Android**
  - Java | JavaScript | C | C++ | C#  — and more

------

### Setup

Since Android does not support the latest MQTT version (i.e., MQTT 5.0), MQTT 3.1.1 was the version used in the solution. Also, the Linux machine must be configured before setting up the client side.

#### Configuring the Linux Machine

Before installing Mosquitto, we should open port `TCP:1883` on the firewall of the Linux machine with:

```shell
sudo ufw allow 1883/tcp
sudo ufw status verbose # to check firewall status
```

then change its network configuration and assign a static IP address since this IP address will be used in the client code to connect to the broker by following [this tutorial](https://linuxize.com/post/how-to-configure-static-ip-address-on-ubuntu-20-04/). The static IP address currently assigned to the Linux machine is `192.168.99.151`.

After doing so, we should install Mosquitto with:

```shell
sudo apt-get update
sudo apt-get install mosquitto
```

By default, the mosquito service will listen in locally. So, it must be changed to support listening for other devices with:

```shell
sudo nano /etc/mosquitto/mosquitto.conf
```

Now, the file will open in the terminal; add the following

```shell
listener 1883
allow_anonymous true
```

then close and save the file.

Restart the mosquitto service and make sure it is running and listening to port 1883

```shell
sudo systemctl restart mosquitto.service
netstat –at
```

After following the previous steps, the broker will startup automatically once the Linux machine boots up.

The Paho setup instructions for both the [Python](https://www.eclipse.org/paho/index.php?page=clients/python/index.php) and [Android](https://www.eclipse.org/paho/index.php?page=clients/android/index.php) clients are clear and do not need further elaboration from my side. However, there are some notes

#### Notes on Android Client Setup

There are some extra steps required that were not directly on the website but were found on StackOverflow and other websites.

In the `AndroidManifest.xml` file, you should add:

- the below `<service>` tag INSIDE the `<application>` tag

  ```xml
  	<service android:name="org.eclipse.paho.android.service.MqttService"/>
  </application>
  ```

- the below `<uses-permission>` tags INSIDE the `<manifest>` tag

  ```xml
  	<uses-permission android:name="android.permission.WAKE_LOCK"/>
  	<uses-permission android:name="android.permission.INTERNET" />
  	<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
  	<uses-permission android:name="android.permission.READ_PHONE_STATE" />
  </manifest>
  ```



------

### Usage

#### Python Client

As you can see in the code snippet below, we are importing the time and paho.mqtt.client packages and then defining a function to print statements whenever we try to connect to a broker as well as another function to print the received topic and the message that was sent whenever a PUBLISH message is received from the broker.

```python
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

```

We then set the connected_flag to false to assure that we are still not connected. Then, we create a client and assign the IP address of the broker to a variable called broker. Then, we try to connect to the broker and start the loop. As long as the connected_flag is not set true by the on_connect function, a statement will be printed out every one second until the device either connects or fails to do so. If it connects, a message will be published to the topic “AppName/Activate” and its content is “ACTIVATE”, with a Quality of Service level = 2 (*important to stop the issue of message repetition*). Then we stop the loop and disconnect the client from the broker.

```python
mqtt.Client.connected_flag = False  # create flag IN class

client = mqtt.Client("GlobalDWS-Python")
broker = "192.168.99.151"  # Change to IP address of the MQTT broker
topic = "AppName/Activate"  # Change to any topic name you want. The same topic here should be used in the Android app
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

```

The `broker` should be the IP address of the MQTT broker; this is the same broker the Android app should connect to.

The `topic` is whichever topic you want to send it to. Preferably, you should change this according to the name and function of the Android app receiving the message.

The `message` can be whatever string of text you want; it doesn't make a difference what is the content of the message in the CovidScreening app. 

However, you may want to send several messages to the Android app, if so, then you will need to filter the messages received in the Android app, either by topic or by content of the message, to perform different functionalities for different messages received.

An in-depth explanation of using MQTT with Python's client side can be found [here](http://www.steves-internet-guide.com/client-connections-python-mqtt/).

#### Android Client

Firstly, you import all the needed packages or let Android Studio do that once you start writing the code. 

Inside the class definition, we create an empty `mqttAndroidClient` object and create 3 final Strings with the IP address of the broker, a new client ID, and a topic to subscribe to. 

```java
// Create an MQTT client
MqttAndroidClient mqttAndroidClient;

// Setting strings to be used for MQTT connection to broker
final String serverUri = "tcp://192.168.99.151:1883"; // Static IP address of the device running the broker
final String clientId = "CovidScreeningRobot-1"; // Whichever name you want
final String subscriptionTopic = "CovidApp/Activate"; // Which topic is the robot going to subscribe to
```

In the `onCreate` method, we assign an `MqttAndroidClient` object to the empty object we created before and pass 3 params to the constructor. We then set a callback so that the program does something whenever a message has been received. The rest is simple and easy to understand by looking at the code and the comments as well as reading the documentation.

Example code of initializing an MqttAndroidClient object and setting a callback listener:

```java
// Create the MQTT client through the constructor
mqttAndroidClient = new MqttAndroidClient(getApplicationContext(), serverUri, clientId);

// Set a callback listener to use for events that happen asynchronously.
mqttAndroidClient.setCallback(new MqttCallbackExtended() {
    @Override // What to do once a connection has been successfully established
    public void connectComplete(boolean reconnect, String serverURI) {
        if (reconnect) {
            // What to do if bool reconnect=true (it lost connection before and reconnected now)
          	Log.i("ScreenerActivity", "Reconnected to : " + serverURI);
          	// Because the clean_session mqttConnectOption is set to true in the code below, we need to re-subscribe
            subscribeToTopic();
        } else { 
            // What to do if bool=false (it connected normally)
          	Log.i("ScreenerActivity", "Connected to: " + serverURI);
        }
    }

    @Override
    public void connectionLost(Throwable cause) {
        // What to output if the connection was lost
      	Log.e("ScreenerActivity", "The Connection was lost.");
    }

    @Override
    public void messageArrived(String topic, MqttMessage message) throws Exception {
        // What to run when a message containing the subscriptionTopic arrives from the broker
      	Log.i("ScreenerActivity", ("Received MQTT message: " + topic + " -> " + new String(message.getPayload())));
    }

    @Override
    public void deliveryComplete(IMqttDeliveryToken token) {
        // removing deliveryComplete from here will create an error on line 145
    }
});
```

Example code of setting custom connect options before trying to connect the client to the broker:

```java
// Set custom options regarding the connection to the MQTT broker
MqttConnectOptions mqttConnectOptions = new MqttConnectOptions();
mqttConnectOptions.setAutomaticReconnect(true);
mqttConnectOptions.setCleanSession(true);

try {
    mqttAndroidClient.connect(mqttConnectOptions, null, new IMqttActionListener() {
    // try to connect to the MQTT broker using the selected options
        @Override
        public void onSuccess(IMqttToken asyncActionToken) {
            subscribeToTopic(); // if connection is successful, subscribe to the topic in subscriptionTopic
        }

        @Override
        public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
            Log.e("ScreenerActivity", "Failed to connect to: " + serverUri);
            exception.printStackTrace(); // if connection fails, output in the log and print stack trace of the exception
        }
    });
} catch (MqttException ex){
    ex.printStackTrace();
}
```

Example code of subscribing to a topic using a function:

```java
// Subscribe to the topic specified in 'subscriptionTopic'
public void subscribeToTopic(){
    try { // subscribe to the topic specified above with QualityOfService level 2
        // (refer to MQTT documentation online)
        mqttAndroidClient.subscribe(subscriptionTopic, 2, null, new IMqttActionListener() {
            @Override
            public void onSuccess(IMqttToken asyncActionToken) {
                Log.i("ScreenerActivity", "Subscribed to topic: " + subscriptionTopic);
            }

            @Override
            public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                Log.e("ScreenerActivity", "Failed to subscribe!");
            }
        });

    } catch (MqttException mqttException){
        Log.e("ScreenerActivity", "Exception whilst subscribing!");
        mqttException.printStackTrace();
    }
}
```

Example code of unsubscribing to a topic using a function:

```java
// Unsubscribe to the topic specified in 'subscriptionTopic'
public void unsubscribeTopic() {
    try {
        mqttAndroidClient.unsubscribe(subscriptionTopic);
    } catch (MqttException mqttException) {
        Log.e("ScreenerActivity", "Exception whilst unsubscribing!");
        mqttException.printStackTrace();
    }
}
```

Example code of disconnecting from the MQTT Broker using a function:

```java
// Disconnect from the MQTT broker
public void disconnectMqtt() {
    try {
        mqttAndroidClient.disconnect();
    } catch (MqttException mqttException) {
        mqttException.printStackTrace();
    }
}
```

These are the most used MQTT functions and are important for a solution using MQTT to work.

-----

## Integration of Precise and MQTT

Integrating Mycroft Precise and MQTT is fairly simple. Just follow the general template of the following piece of Python code:

```python
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

```

So, we basically use the same pieces of code mentioned in the Usage sections above. 

We run the Mycroft Precise code inside `main` and have it run indefinitely, waiting to hear the wake word. However, as you can see in the `activate_app()` function, we start connecting to the broker there and then send a message to the specified topic "CovidApp/Activate". The broker (which is the same Linux machine) will receive the message and forward it to MQTT clients subscribed to the same topic, which is the robot in our case. Once the message is received by the robot, the app will activate and start asking questions as per the form in the CovidScreening app.

**So, how does it work?**

In the case of the CovidScreening app, the way it should work is like this:

- The Linux machine starts the mosquitto service once booted up and runs the Mycroft Precise and MQTT python script
- The CovidScreening app on the robot connects to the broker once the app is launched and will subscribe to the "CovidApp/Activate" topic
- The Linux machine detects the wake word --> The Linux machine connects to the broker (*it can be both the broker and client at the same time*) --> The Linux machine's client side sends the message to the broker --> The broker forwards the message to devices subscribed to the topic in the message --> The CovidScreening app receives the message from the broker --> The app activates and starts asking questions; it will also disconnect from the broker and clean the session 

![Architecture Diagram](https://images2.imgbox.com/2d/ca/dmnUtdR0_o.png)

