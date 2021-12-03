# GlobalDWS-VA

This README will be a guide for users unfamiliar with Mycroft's Precise (wake word engine) and Mosquitto MQTT protocol. It will introduce the two topics and give info on the requirements, setup, and usage of each. 

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
