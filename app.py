from flask import Flask, request, jsonify
import yt_dlp
import json

app = Flask(__name__)

def extract_youtube_urls(video_url):
    """Extract video and audio URLs from YouTube using yt-dlp"""
    ydl_opts = {
        'format': 'best[ext=webm]/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            video_url = info.get('url')
            title = info.get('title', 'Unknown')

            formats = info.get('formats', [])
            video_stream = None
            audio_stream = None

            for fmt in formats:
                if fmt.get('vcodec') != 'none' and fmt.get('acodec') == 'none':
                    if not video_stream or fmt.get('quality', 0) > video_stream.get('quality', 0):
                        video_stream = fmt
                elif fmt.get('vcodec') == 'none' and fmt.get('acodec') != 'none':
                    if not audio_stream or fmt.get('quality', 0) > audio_stream.get('quality', 0):
                        audio_stream = fmt

            return {
                'success': True,
                'title': title,
                'video_url': video_url,
                'video_stream': video_stream.get('url') if video_stream else None,
                'audio_stream': audio_stream.get('url') if audio_stream else None
            }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/extract', methods=['GET'])
def extract():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({'success': False, 'error': 'No URL provided'})

    result = extract_youtube_urls(video_url)
    return jsonify(result)

@app.route('/')
def home():
    return "YouTube Extractor API - Use /extract?url=YOUTUBE_URL"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
