from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
from pydub import AudioSegment
import os
import threading
import time

app = Flask(__name__)

def download_and_convert(url: str, output_path: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}.%(ext)s',
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Convert to MP3 using pydub
        audio = AudioSegment.from_file(filename)
        mp3_filename = output_path + ".mp3"
        audio.export(mp3_filename, format="mp3")

        # Clean up temporary file
        os.remove(filename)
        print(f"Conversion complete: {mp3_filename}")
    
    except Exception as e:
        print(f"Error during download/convert: {str(e)}")

@app.route('/youtube-to-mp3/', methods=['GET'])
def youtube_to_mp3():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is required."}), 400

    output_path = f"downloads/{url.split('=')[-1]}"
    start_time = time.time()

    # Start download and conversion in a new thread
    thread = threading.Thread(target=download_and_convert, args=(url, output_path))
    thread.start()

    end_time = time.time()
    print(f"Request processing time: {end_time - start_time} seconds")

    return jsonify({"message": "Your download will start soon."})

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
