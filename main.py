import os
import json
import subprocess
import random

from pytubefix import YouTube
from pytubefix.cli import on_progress
from youtube_transcript_api import YouTubeTranscriptApi

ids=['c4NVYZXjnnY', 'DwLIHjucj4E', 'gyVdHAKvKQ8', '3ASjk5tZdVk', 'logsBBYBJYo', 'Xj6fQH8Jm24', 'zS7dctq0SjI', 'Xq49U6Iwv5M', 'n1AGLQDZMXA', 'UpSlDgX9hMU', 'sXWFr5Nk-g8', 'aszQti5MOVg', 'iJ3yvRQVOvc', 'XVIcSRMGew0', 'bWnI3p86_Vg', 'dWnFRG-hRxg', 'zqsrGr3uf38', 'lkhoYbeFmh4', 'sqSTkElZBcs', 'f7o50aGUimI', 'WdrSNvcNthI', 'ovulHVpLYNI', 'IhWr1FX9eUk', 'odZo2zOzCYE', 'TdP0yNipdJQ', 'JWEHzroH48E', 'CPFj7tqdHC4', 'IhGlpiaZaiE', 'p2S-jLjUOv8', 'nlzNNqrbFxY', 'XwPWBDTr3XM', 'SZ2m6USjri8', 'n00bwsjwXEg', '6jOYS-7-d9M', 'i6IKTwA8Jdg', 'F_zDW6acDU8', '4jz0UuxtGiE', '5GGsvuvA_Oo', 'ELQQPeBty0M', 'pppA7RIAWOY', 'uhVg0I_S5aE', 'zD-_OdUffD0', 'VPcJsAnViUw', '0l3b9z6QtJA', 'ySBfE8-6NEE', 'WWV0gAa-7fY', 'afMur5q8nIg', '9MUE27wBmpY', '8nARHZsq8H0', 'yPccTfD05_4', 'u1NSnUCeN-s', '026mgs9lkts', 'F4jlzHjO_mk', 'HrW45utwIRg', 'ROeee4gCI1c', 'u6rXcLbXq5c', 'QhZN6h7KOyM', 'S3bHtYevSZQ', 'RROIhdOIRwI', 'c2dzMMe9KSA', '7jErfSG1zoc', 'mf8zlfUbEu8', 'zQbVkPPeVJ0', 'H-4XnhCwc9A', 'wRq3VWmV3JE', 'yVZ60SYNBK0', 'FFkxc-EgKms', 'caYiZwesO8s', '5grrEU4GSpo', 'ZUQf3fy1V4k', 'zAu8ZLVIGxE', 'NTrIZh2rkYw', 'VbpVL4ma2Fg', 'VYzo595EUMw', 'rFN5_R601Sg', 'N4GxEYkofK0', 'W73sjMm0hl8', 'LOglsZE-5wk', 'Hiv5aJQGlZc', 'sR4Qm-zk7Gw', 'ObCwd2bL8DU', 'MFw0hG7-LDQ', 'kTs-Lu2-p-M', 'iY7jYl3Lq00', 'SB9ovJyqVrI', 'ObdEAvV63uo', 'PxVRM29fiFM', 'HNPk1MzT3rA', 'RE_oje_dqQI', 'c8V2k5T5Cck', '73N3aYPDWLQ', 'W0qI7ImxscM', '1FmOzcI-H6c', '61dHKtMJv3o', '1m6gQK3_ck4', 'vOeG8vrgBHE', 'yiGJkQjZv7Y', 'XFQ50sIe5mI']

print("videos todo:", len(ids))

def chunk_subtitles(transcript, chunk_size):
    chunks = []
    for i in range(0, len(transcript), chunk_size):
        chunks.append(transcript[i:i+chunk_size])
    return chunks

for video_id in ids:
    print("Processing video ID:", video_id)
    
    url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        print(f"Downloading: {yt.title}")

        video = yt.streams.get_highest_resolution()

        destination = video_id  # place all the clips in this folder
        if not os.path.exists(destination):
            os.makedirs(destination)

        out_file = video.download(output_path=destination)

        base, ext = os.path.splitext(out_file)
        new_file = f'{destination}/vid.mp4'
        os.rename(out_file, new_file)

        # Get transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'ja'])

        # Chunk the subtitles
        chunk_size = 15
        chunked_transcript = chunk_subtitles(transcript, chunk_size)

        # Process each chunk
        for chunk_num, chunk in enumerate(chunked_transcript):
            # Skip to next video if chunk_num is greater than 100
            if chunk_num > 100:
                print(f"Chunk number exceeded 100 for video {video_id}. Skipping to next video.")
                break

            chunk_start_time = chunk[0]['start']
            
            # Calculate the end time for ffmpeg based on chunk_size
            ffmpeg_end_index = min(chunk_size - 2, len(chunk) - 1)
            chunk_ffmpeg_end_time = chunk[ffmpeg_end_index]['start'] + chunk[ffmpeg_end_index]['duration']
            
            chunk_duration = chunk_ffmpeg_end_time - chunk_start_time

            # Write metadata
            with open(f"{destination}/metadata.jsonl", 'a') as f:
                json.dump({
                    'chunk_num': chunk_num,
                    'subtitles': [entry['text'] for entry in chunk]
                }, f)
                f.write('\n')

            # Create clip
            output_file = f"{destination}/vid-chunk-{chunk_num}.mp4"
            subprocess.call(["ffmpeg", "-i", new_file, "-ss", f"{chunk_start_time:.2f}", "-to", f"{chunk_ffmpeg_end_time:.2f}", "-c:v", "libx264", "-c:a", "aac", "-strict", "experimental", output_file])

        print(f"{yt.title} has been successfully downloaded and processed.")

    except Exception as e:
        print(f"An error occurred while processing video {video_id}: {str(e)}")

print("All videos have been processed.")