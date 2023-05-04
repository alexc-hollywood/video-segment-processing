import os
import subprocess
from tasks import transcode_segment

input_file = "input_video.avi"
output_file = "output_video.mp4"
segment_length = 10
video_length = 2 * 60
num_segments = video_length // segment_length

# Split the video into 10-second segments and transcode them to HEVC using Celery
segment_tasks = []
for i in range(num_segments):
    start_time = i * segment_length
    output_segment = f"segment_{i:03d}.mp4"
    task = transcode_segment.delay(input_file, start_time, segment_length, output_segment)
    segment_tasks.append(task)

# Wait for all tasks to complete
for task in segment_tasks:
    task.get()

# Create a file with a list of segments
with open("segments_list.txt", "w") as f:
    for i in range(num_segments):
        f.write(f"file 'segment_{i:03d}.mp4'\n")

# Concatenate the segments to create the final video
subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "segments_list.txt",
    "-c", "copy", output_file
], check=True)

# Clean up temporary files
for i in range(num_segments):
    os.remove(f"segment_{i:03d}.mp4")
os.remove("segments_list.txt")
