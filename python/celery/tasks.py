from celery import Celery
import subprocess

app = Celery()
app.config_from_object('celeryconfig')

@app.task
def transcode_segment(input_file, start_time, segment_length, output_segment):
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start_time), "-t", str(segment_length),
        "-i", input_file, "-c:v", "libx265", "-c:a", "aac", output_segment
    ], check=True)
    return output_segment
