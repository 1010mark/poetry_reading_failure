import argparse
from pythonosc import dispatcher, osc_server
from pydub import AudioSegment
from pydub.playback import play
import sounddevice as sd
import threading
import time
import voicevox_bpm

# 現在のサイクル状態を共有するための変数
current_cycle = None
current_cps = 0.5625
lock = threading.Lock()
error_seconds = 0.14
audio_queue = []
is_playing = False

def parse_osc_message(message):
    parsed = {}
    for i in range(0, len(message), 2):  # 2個ずつ取り出す
        key = message[i]
        value = message[i + 1]
        parsed[key] = value
    return parsed

def handle_cycles(address, *args):
    """
    OSCで送られてきたメッセージを処理して現在のサイクルを更新します。
    """
    global current_cycle
    if(address != "/dirt/play") : return 0
    message = parse_osc_message(args)
    with lock:
        current_cycle = message["cycle"]  # 現在のcycle値を更新
        current_cps = message["cps"]
        print(current_cycle)
        if int(current_cycle) == current_cycle :
            playQueueAudio()

def stdin_listener():
    """
    標準入力を監視して入力を受け取ります。
    """
    try:
        # 標準入力からテキストを受け取る
        text = input("Enter text: ").strip()
        if text:
            print(f"Generating audio for input: {text}")
            audio = voicevox_bpm.generate_audio_on_bpm(text,3,current_cps*240)
            audio_queue.append([audio.get_array_of_samples(), audio.frame_rate])
            stdin_listener()

    except EOFError:
        pass

def playQueueAudio() :
    global is_playing
    if(len(audio_queue) == 0 | is_playing): return 0
    audio = audio_queue.pop()
    time.sleep(error_seconds)
    is_playing = True
    sd.play(audio[0], audio[1])
    is_playing = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=2020, help="The port to listen on")
    args = parser.parse_args()

    # OSCサーバのセットアップ
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/dirt/play", handle_cycles)

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))

    # 標準入力を別スレッドで監視
    stdin_thread = threading.Thread(target=stdin_listener, daemon=True)
    stdin_thread.start()

    # サーバを開始
    server.serve_forever()
