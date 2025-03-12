from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp
import os
import tempfile

app = Flask(__name__)

def get_video_info(link):
    """Fetch video details without downloading."""
    try:
        ydl_opts = {'quiet': True, 'noplaylist': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            return {
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'filesize': info.get('filesize_approx', 'Unknown'),
                'duration': info.get('duration_string', 'Unknown'),
                'format': info.get('format', 'Unknown'),
            }
    except Exception as e:
        return {'error': str(e)}

def download_video(link):
    """Download video and return the temporary file path."""
    try:
        temp_dir = tempfile.gettempdir()
        ydl_opts = {
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("\n📥 Downloading...")
            info = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info)
            print("✅ Download completed!\n")
            return filename
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/get_video_info', methods=['POST'])
def fetch_video_info():
    video_link = request.json.get('video_link')
    if not video_link:
        return jsonify({'error': 'No link provided'}), 400
    video_info = get_video_info(video_link)
    return jsonify(video_info)

@app.route('/download', methods=['POST'])
def download():
    video_link = request.form['video_link'].strip()
    file_path = download_video(video_link)
    if file_path:
        return send_file(file_path, as_attachment=True)
    return "Error downloading file", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
