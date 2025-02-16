import sys
import speech_recognition as sr
import pyttsx3
from ollama import chat
from ollama import ChatResponse
from RealtimeSTT import AudioToTextRecorder
from BERT import BERT

def STT():
    print("Wait until it says 'speak now'")
    recorder = AudioToTextRecorder()
    transcribed_text = None

    def process_text(text):
        nonlocal transcribed_text
        transcribed_text = text

    while True:
        try:
            recorder.text(process_text)

            if transcribed_text.lower() == 'turn off.':
                recorder.shutdown()
                sys.exit()
            else:
                response: ChatResponse = chat(model='llama3.2:3b', messages=[
                    {
                        'role': 'user',
                        'content': transcribed_text,
                    },
                ])

                # or access fields directly from the response object
                print(transcribed_text)
                print(response.message.content)
                TTS(response.message.content)
                # recorder.shutdown()
                # return transcribed_text

        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
            return None


def TTS(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def main():
    # Convert speech to text and recognize intent
    result = STT()

    # If we got some text, convert it back to speech
    if result is None:
        print("No valid speech input to process.")

if __name__ == "__main__":
    main()
