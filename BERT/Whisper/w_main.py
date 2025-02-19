import torch
from TTS.api import TTS
import gradio
import pyaudio
import wave

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
# if use multi-lingual then add speaker and language

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

def generate_audio(text):
    tts = TTS("tts_models/en/ljspeech/fast_pitch").to(device)
    tts.tts_to_file(text, file_path='outputs/output.wav')
    return 'outputs/output.wav'


audio = generate_audio('What are you doing here?')

demo = gradio.Interface(
    fn=generate_audio,
    inputs=[gradio.Text(label="Text"),],
    outputs=[gradio.Audio(label="Audio"),],
)
demo.launch()

# Usage example for pyaudio

# a = AudioFile(audio)
# a.play()
# a.close()
