import os
import json
import uuid
import gdown
import shutil
from moviepy.editor import VideoFileClip
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
TASK_FILE = "task.json"
LAST_TASK_FILE = "last_task.json"
DOWNLOAD_PATH = "movie.mkv"
TRIMMED_PATH = "trimmed.mp4"
CLIPS_DIR = "clips"
os.makedirs(CLIPS_DIR, exist_ok=True)

# FFmpeg effects
EFFECTS = (
    "eq=brightness=0.1:contrast=1.4:saturation=1.4,"
    "unsharp=5:5:1.0:5:5:0.0,"
    "curves=preset=medium_contrast"
)

def download_video(url, out_path):
    print("🎥 Downloading video...")
    gdown.download(url, out_path, quiet=False)
    print("✅ Download complete")

def trim_video(in_path, out_path, start, end):
    print("✂️ Trimming video...")
    clip = VideoFileClip(in_path).subclip(start, end)
    clip.write_videofile(out_path, codec="libx264", audio_codec="aac")
    print("✅ Trimming complete")

def apply_effects(in_path, out_path):
    print("🎨 Applying effects...")
    cmd = [
        "ffmpeg", "-y", "-i", in_path,
        "-vf", EFFECTS,
        "-c:a", "copy",
        out_path
    ]
    subprocess.run(cmd)
    print("✅ Effects applied")

def process_task():
    if not os.path.exists(TASK_FILE):
        print("❌ No task.json found.")
        return

    with open(TASK_FILE, "r") as f:
        task = json.load(f)

    video_url = task.get("video_url")
    start_time = task.get("start_time")
    end_time = task.get("end_time")

    if not video_url or not start_time or not end_time:
        print("❌ Missing required fields in task.json.")
        return

    # Check if video was already downloaded
    already_downloaded = False
    if os.path.exists(LAST_TASK_FILE):
        with open(LAST_TASK_FILE, "r") as f:
            last_task = json.load(f)
            if last_task.get("video_url") == video_url:
                already_downloaded = True

    if already_downloaded and os.path.exists(DOWNLOAD_PATH):
        print("⏩ Skipping download (same URL as last task)")
    else:
        download_video(video_url, DOWNLOAD_PATH)
        with open(LAST_TASK_FILE, "w") as f:
            json.dump({"video_url": video_url}, f)

    # Trim and process
    trim_video(DOWNLOAD_PATH, TRIMMED_PATH, start_time, end_time)

    # Save with unique name
    final_output = f"clip_{uuid.uuid4().hex}.mp4"
    final_path = os.path.join(CLIPS_DIR, final_output)
    apply_effects(TRIMMED_PATH, final_path)

    print(f"✅ Final clip ready: {final_path}")

if __name__ == "__main__":
    process_task()
