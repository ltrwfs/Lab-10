import webbrowser, json
import requests, pyttsx3, pyaudio, vosk


class Speech:
    def __init__(self):
        self.tts = pyttsx3.init()
        voices = self.tts.getProperty('voices')
        self.tts.setProperty('voice', voices[1].id)
        self.tts.setProperty('rate', 150)

    def say(self, text):
        print(f"Assistant: {text}")
        self.tts.say(text)
        self.tts.runAndWait()


class Recognize:
    def __init__(self):
        model = vosk.Model("vosk-model-en-us")
        self.record = vosk.KaldiRecognizer(model, 16000)
        self.stream()
    
    def stream(self):
        pa = pyaudio.PyAudio()
        self.stream = pa.open(format=pyaudio.paInt16,
                         channels=1,
                         rate=16000,
                         input=True,
                         frames_per_buffer=8000)

    def listen(self):
        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.record.AcceptWaveform(data):
                answer = json.loads(self.record.Result())
                if answer['text']:
                    return answer['text']


class Assistant:
    def __init__(self):
        self.speech = Speech()
        self.recognizer = Recognize()
        self.word_data = None
        self.word = ""

    def find_word(self, word):
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            result = requests.get(url)
            result.raise_for_status()
            self.word_data = result.json()[0]
            self.word = word
            self.speech.say(f"Word {word} is found.")
        except Exception:
            self.speech.say(f"Could not find {word}.")

    def save(self):
        if self.word_data:
            try:
                with open("dictionary.txt", "a", encoding="utf-8") as file:
                    meanings = self.word_data['meanings']
                    definition = meanings[0]['definitions'][0]['definition']
                    file.write(f"{self.word}: {definition}\n\n")
                self.speech.say("Saved")
            except:
                self.speech.say("Error while saving")
        else:
            self.speech.say("You have not loaded any words")

    def meaning(self):
        if self.word_data:
            try:
                meanings = self.word_data['meanings']
                definition = meanings[0]['definitions'][0]['definition']
                self.speech.say(f"{self.word} means {definition}")
            except:
                self.speech.say(f"Could not find meaning for {self.word}")
        else:
            self.speech.say("You have not loaded any words")

    def link(self):
        if self.word:
            webbrowser.open(f"https://www.dictionary.com/"
                            +f"browse/{self.word}")
            self.speech.say("Link is opened")
        else:
            self.speech.say("You have not loaded any words")

    def example(self):
        if self.word_data:
            try:
                meanings = self.word_data['meanings']
                example = meanings[0]['definitions'][0]['example']
                self.speech.say(f"Example: {example}")
            except:
                self.speech.say("Could not find examples for {self.word}")
        else:
            self.speech.say("You have not loaded any words")


    def run(self):
        self.speech.say("Hello! Assistant is ready and waiting for commands")
        while True:
            command = self.recognizer.listen()
            print(f"User: {command}")

            if command.startswith("find "):
                word = command.replace("find ", "").strip()
                self.find_word(word)
            elif command == "save":
                self.save()
            elif command == "meaning":
                self.meaning()
            elif command == "link":
                self.link()
            elif command == "example":
                self.example()
            elif command == "stop":
                break
            else:
                self.speech.say("Command was not recognized or wrong command")


if __name__ == "__main__":
    assistant = Assistant()
    assistant.run()