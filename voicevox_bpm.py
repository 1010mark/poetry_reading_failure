import requests
from pydub import AudioSegment
from pydub.playback import play
import io
import math
from datetime import datetime

# VOICEVOXエンジンのURL
BASE_URL = "http://127.0.0.1:50021"

# テキスト
sample_text = "これはポエトリーリーディングのテストです。テンポに合わせて音声を生成します。"
# アクセント句を取得
def get_accent_phrases(text, speaker_id):
    response = requests.post(
        f"{BASE_URL}/audio_query",
        params={"text": text, "speaker": speaker_id},
    )
    response.raise_for_status()
    audio_query = response.json()
    return [phrase["moras"] for phrase in audio_query["accent_phrases"]]

# 音声合成
def synthesize_voice(text, speaker_id, BPM):
    audio_query = requests.post(
        f"{BASE_URL}/audio_query",
        params={"text": text, "speaker": speaker_id},
    ).json();
    audio_query["postPhonemeLength"] = 0
    audio_query["prePhonemeLength"] = 0
    # print(f"BPM:{BPM} speedScale:")
    audio_query["speedScale"] = BPM/120
    # print(audio_query)
    response = requests.post(
        f"{BASE_URL}/synthesis",
        json=audio_query,
        params={"speaker": speaker_id},
    )
    response.raise_for_status()
    return response.content

# メイン処理
def generate_audio_on_bpm(text, SPEAKER_ID = 3, BPM = 120):
    BEAT_DURATION = 60 / BPM  # 1拍の長さ（秒）
    silence_adjust = 0.02 * 120 / BPM # マジックナンバーすぎますわ～ (秒)
    # アクセント句を取得
    accent_phrases = get_accent_phrases(text, SPEAKER_ID)
    one_beat_duration = BEAT_DURATION
    combined_audio = AudioSegment.silent(duration=0)  # 空のオーディオ
    for i, phrase in enumerate(accent_phrases):
        # アクセント句を文字列に変換
        phrase_text = "".join(mora["text"] for mora in phrase if mora["text"])
        print(f"Processing accent phrase: {phrase_text}")

        # 音声生成
        audio_data = synthesize_voice(phrase_text, SPEAKER_ID, BPM)
        
        # 一時ファイルとして保存せず、直接操作
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")
        
        # BPMに基づいて間隔を挿入
        combined_audio += audio_segment
        now_length = combined_audio.duration_seconds
        target_duration = math.ceil(now_length / one_beat_duration) * one_beat_duration - silence_adjust
        print("now:" + str(now_length))
        combined_audio += AudioSegment.silent(duration=(target_duration - now_length)*1000)
        print("after:" + str(combined_audio.duration_seconds))
        

    # 最終音声を保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    combined_audio.export(f"poetry_reading_bpm_{timestamp}.wav", format="wav")
    print(f"音声ファイルを保存しました: poetry_reading_bpm_{timestamp}.wav")
    return combined_audio

generate_audio_on_bpm(sample_text)