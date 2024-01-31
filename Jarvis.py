from dotenv import load_dotenv
import openai
import speech_recognition as sr
import pyttsx3
import os

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

recognizer = sr.Recognizer()
microphone = sr.Microphone()
engine = pyttsx3.init()  

# Configuração
config = {
    'chat': 'Jarvis',
    'model': 'gpt-3.5-turbo',
    'temperature': 0.5,
    'max_tokens': 10,
    'messages': [
        {"role": "system", "content": "Você é um assistente gente boa. E meu nome é Eneas!"}
    ],
    'assistant_active': False,
    'commands': [
        {
            'name': 'activate_assistant',
            'words': [
                'Jarvis', 'Jarvis ativar', 'Olá Jarvis',  # Adicionado 'Jarvis'
                'Boa noite Jarvis', 'Boa tarde Jarvis', 'Bom dia Jarvis',
            ],
            'action': 'activate_assistant'
        },
        {
            'name': 'exit_assistant',
            'words': [
                'Sair', 'Tchau', 'Jarvis desativar',
                'Até logo',
            ],
            'action': 'exit_assistant'
        }

    ]
}

# Função para ativar o assistente
def activate_assistant():
    if not config['assistant_active']:
        config['assistant_active'] = True
        speak("Olá Mestre, como posso ajudar?")

# Função para desativar o Jarvis
def exit_assistant():
    config['assistant_active'] = False
    speak("Até mais!")

# Função para ouvir e obter entrada de áudio
def listen():
    with microphone as source:
        print("Ouvindo...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)

    try:
        print("Reconhecendo...")
        query = recognizer.recognize_google(audio, language='pt-BR')
        if query:
            print(f"Você disse: {query}\n")
        else:
            query = 'Não entendi. Repita por favor...'

    except Exception as e:
        print(e)
        query = ''
    return query

# Função para falar a resposta
def speak(response):
    voices = engine.getProperty('voices')
    engine.setProperty('rate', 180)

    for indice, vozes in enumerate(voices):
        print(indice, vozes.name)

    engine.setProperty('voice', voices[0].name)

    engine.say(response)
    engine.runAndWait()
    

# Função para obter a resposta do ChatGPT
def get_gpt3_response(message):
    messages = config['messages']
    messages.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=config['temperature'],
        max_tokens=config['max_tokens'],
    )
    return [response.choices[0].message['content'], response.usage]

# Loop principal
while True:
    user_input = listen()

    commands = config['commands']

    for command in commands:
        if user_input.lower() in [word.lower() for word in command['words']]:
            globals().get(command['action'])()
            break

    if config['assistant_active'] and user_input.lower() not in [word.lower() for word in commands[0]['words']]:
        gpt3_response = get_gpt3_response(user_input)
        print("Resposta do ChatGPT:", gpt3_response)
        speak(gpt3_response[0])
