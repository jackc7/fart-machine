from flask import Flask, render_template, request, jsonify
import os
import pygame.mixer
from urllib.parse import quote, unquote
import random
import time

app = Flask(__name__)

SOUND_DIR = './farts'
sounds_playing = {}  # Dictionary to keep track of all sounds currently playing

def get_fart_sounds():
    files = [f for f in os.listdir(SOUND_DIR) if os.path.isfile(os.path.join(SOUND_DIR, f))]
    farts = []
    for file in files:
        file_path = os.path.join(SOUND_DIR, file)
        duration = get_sound_duration(file_path)
        farts.append((os.path.splitext(file)[0], duration))
    return farts

def get_sound_duration(file_path):
    pygame.mixer.init()
    sound = pygame.mixer.Sound(file_path)
    return sound.get_length()

@app.route('/')
def index():
    return render_template('index.html', farts=get_fart_sounds(), quote=quote)

@app.route('/timed')
def timed_fart_page():
    return render_template('timed.html', farts=get_fart_sounds(), quote=quote)

@app.route('/play_after_delay/<fart_name>/<delay>', methods=['POST'])
def play_after_delay(fart_name, delay):
    if fart_name == "random":
        farts = get_fart_sounds()
        chosen_fart = random.choice(farts)
        fart_name = chosen_fart[0]  # Update the fart_name to the randomly chosen fart's name
    time.sleep(int(delay))
    return play_sound(fart_name)

@app.route('/play_on_interval/<fart_name>/<int:interval>/<int:duration>', methods=['POST'])
def play_on_interval(fart_name, interval, duration):
    if fart_name == "random":
        farts = get_fart_sounds()
        chosen_fart = random.choice(farts)
        fart_name = chosen_fart[0]  # Update the fart_name to the randomly chosen fart's name
    file_path = os.path.join(SOUND_DIR, f"{fart_name}.mp3")
    end_time = time.time() + int(duration)
    while time.time() < end_time:
        play_sound(fart_name)
        time.sleep(int(interval))
    return jsonify({"status": "success"})


@app.route('/play/<fart_name>')
def play_sound(fart_name):
    decoded_name = unquote(fart_name)
    file_path = os.path.join(SOUND_DIR, f"{decoded_name}.mp3")
    play_audio(file_path)
    return "Playing", 200

@app.route('/play/random')
def play_random_fart():
    farts = get_fart_sounds()
    chosen_fart = random.choice(farts)
    play_audio(os.path.join(SOUND_DIR, f"{chosen_fart[0]}.mp3"))
    return chosen_fart[0], 200  # Return the name of the randomly chosen fart

@app.route('/stop', methods=['POST'])
def stop_audio():
    global current_sound
    if current_sound:
        current_sound.stop()
    return "Stopped", 200

def play_audio(file_name):
    global current_sound
    pygame.mixer.init()
    current_sound = pygame.mixer.Sound(file_name)
    current_sound.play()

if __name__ == "__main__":
    app.run("0.0.0.0", port=80, debug=True)
