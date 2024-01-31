from pytube import YouTube
import os
import subprocess
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import threading

from flask import Flask
from flask import render_template
app = Flask(__name__)

audios=[]
audios_keys = []

def list_buttons(): 
    # return ["a", "b", "c"]
    return os.listdir("./static/audios")


@app.route("/")
def hello_world():
    return render_template('front.html', list_buttons = audios)

def download_video(link, key):
    return YouTube(link).streams.first().download(output_path='static/audios', filename=key)


def convert_video_to_audio_ffmpeg(video_file, output_ext="mp3"):
    """Converts video to audio directly using `ffmpeg` command
    with the help of subprocess module"""
    filename, ext = os.path.splitext(video_file)
    subprocess.call(["ffmpeg", "-y", "-i", video_file, f"{filename}.{output_ext}"], 
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT)


def delet_video_file(path):
    os.remove(path)



cred = credentials.Certificate("sound-table-8076c-firebase-adminsdk-5c36f-e635bdfcf1.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
callback_done = threading.Event()

# doc_ref = db.collection("users").document("alovelace")
# doc_ref.set({"first": "Ada", "last": "Lovelace", "born": 1815})


def write_on_has_link(link):
    open("has.txt", "a").write(link + "\n")

def check_has_link(link):
    has_doc = open("has.txt", "r").readlines()
    print(has_doc)
    return has_doc.count(link + '\n') > 0




# Create a callback on_snapshot function to capture changes
def on_snapshot(doc_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == "ADDED":
            data = change.document.to_dict()
            link = data["link"]
            key = data['key']
            title = data['title']
            if audios_keys.count(key) == 0:
                audios_keys.append(key)
                audios.append({
                    'key': key,
                    'link': link,
                    'title': title,
                })

            if not check_has_link(link):
                print("download")
                video_path = download_video(link, key)
                print("convert")
                convert_video_to_audio_ffmpeg(video_path)
                print("delet")
                delet_video_file(video_path)
                write_on_has_link(link)
            else:
                print("Ja contem video")
    callback_done.set()

doc_ref = db.collection("videos")
# Watch the document
doc_watch = doc_ref.on_snapshot(on_snapshot)

os.system('chromium --kiosk http://localhost:5000')
app.run(debug=True, host='0.0.0.0')
while True:
    pass



