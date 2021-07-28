from __future__ import division

import os
import re
import sys
import pyaudio
from six.moves import queue
from google.cloud import speech
from google.cloud import texttospeech
from precise_runner import PreciseEngine, PreciseRunner
from time import sleep
from playsound import playsound

RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), "google-credentials.json")


class MicrophoneStream(object):

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


def listen_print_loop(responses):
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript

        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            voice_transcription = transcript + overwrite_chars

            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                print("Exiting..")
                break

            num_chars_printed = 0
            return voice_transcription


# Speech to Text
client = speech.SpeechClient()
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=RATE,
    language_code="en-US",
    enable_automatic_punctuation=True,
)

streaming_config = speech.StreamingRecognitionConfig(
    config=config,
    interim_results=True,
)

# Text to Speech
tts = texttospeech.TextToSpeechClient()
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Wavenet-C"
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)


def activate_va():
    print("##### WAKE WORD DETECTED #####\n")

    ask_name = tts.synthesize_speech(
        input=texttospeech.SynthesisInput(text="Hello. Could you please tell me your name?"),
        voice=voice, audio_config=audio_config
    )
    with open("ask_name.mp3", "wb") as out:
        out.write(ask_name.audio_content)

    playsound("ask_name.mp3")

    increment = 1

    while increment < 5:

        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )
            transcription = client.streaming_recognize(streaming_config, requests)
            voice_transcription = listen_print_loop(transcription)
            print(voice_transcription)

            response = ""

            if increment == 1:
                response = "Hello, Rami. Could you please tell me your age?"

            if increment == 2:
                response = "Did you travel recently in the past 14 days?"

            if increment == 3:
                if "Yes" in voice_transcription:
                    response = "Please leave the hospital premises and contact your doctor for a check up."
                if "No" in voice_transcription:
                    response = "Did you socialize with anyone infected with COVID-19 in the past 14 days?"

            if increment == 4:
                if "Yes" in voice_transcription:
                    response = "Please leave the hospital premises and contact your doctor for a check up."
                if "No" in voice_transcription:
                    response = "Okay. Thank you for following social distancing protocols!"

            # Output the response from the Natural Language Understanding module
            voice_response = tts.synthesize_speech(
                input=texttospeech.SynthesisInput(text=response),
                voice=voice, audio_config=audio_config
            )
            with open("voice_response.mp3", "wb") as out:
                out.write(voice_response.audio_content)

            increment = increment + 1
            playsound("voice_response.mp3")

            if increment == 3 or increment == 4 and "Yes" in voice_transcription:
                return

    return


precise_path = os.path.join(os.path.dirname(__file__), "precise-engine/precise-engine")
ww_path = os.path.join(os.path.dirname(__file__), "hey-dsr/hey-dsr.pb")


def main():
    engine = PreciseEngine(precise_path, ww_path)
    runner = PreciseRunner(engine, on_activation=lambda: activate_va())
    runner.start()

    # Sleep forever
    while True:
        sleep(100)


for i in range(0, 1):
    main()
