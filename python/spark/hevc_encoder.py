import os
import subprocess
from pyspark import SparkContext, SparkConf

def transcode_segment(args):
    input_file, start_time, segment_length, output_segment = args
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start_time), "-t", str(segment_length),
        "-i", input_file, "-c:v", "libx265", "-c:a", "aac", output_segment
    ], check=True)
    return output_segment

input_file = "input_video.avi"
output_file = "output_video.mp4"
segment_length = 10
video_length = 2 * 60
num_segments = video_length // segment_length

# Initialize Spark
conf = SparkConf().setAppName("VideoProcessing")
sc = SparkContext(conf=conf)

# Prepare the input data
input_data = [
    (input_file, i * segment_length, segment_length, f"segment_{i:03d}.mp4")
    for i in range(num_segments)
]

# Distribute the data and process it using Spark
rdd = sc.parallelize(input_data)
rdd.map(transcode_segment).collect()

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
