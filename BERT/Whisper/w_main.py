import torch
from TTS.api import TTS
import pyaudio
import wave

class AudioFile:
    chunk = 1024

    def __init__(self, file):
        """ Init audio stream """
        self.wf = wave.open(file, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.p.get_format_from_width(self.wf.getsampwidth()),
            channels=self.wf.getnchannels(),
            rate=self.wf.getframerate(),
            output=True
        )

    def play(self):
        """ Play entire file """
        data = self.wf.readframes(self.chunk)
        while data != b'':
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)

    def close(self):
        """ Graceful shutdown """
        self.stream.close()
        self.p.terminate()

device = 'cuda' if torch.cuda.is_available() else 'cpu'

''' 
model 1: tts_models/multilingual/multi-dataset/xtts_v2
   - Is multi-lingual
   - Synthesis speech more percisely but slower
'''

'''
model 2: tts_models/en/ljspeech/fast_pitch
    - Has en only
    - Faster speech conversion
'''
# path for config : C:\Users\ADMIN\AppData\Local\tts

def generate_audio(text):
    tts = TTS("tts_models/en/ljspeech/fast_pitch").to(device)
    tts.tts_to_file(text, speaker="Ana Florence", language='en', file_path='output.wav')
    return 'output.wav'

audio = generate_audio('Justin Beaver is a popular singer!')

# Usage example for pyaudio
a = AudioFile(audio)
a.play()
a.close()
