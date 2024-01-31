from pytube import YouTube
import os
import subprocess
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import threading







def download_video(link):
    return YouTube(link).streams.first().download()


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
    return has_doc.count(link) > 0




# Create a callback on_snapshot function to capture changes
def on_snapshot(doc_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == "ADDED":
            link = change.document.to_dict()["link"]
            print(link)
            if not check_has_link(link):
                print("download")
                video_path = download_video(link)
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


while True:
    pass



