import yt_dlp
from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip, concatenate_audioclips
import os
# import ffmpeg
# from pytube import YouTube # Not working as video contain guns, it mark it as 18+ content restricting me to download it. so i used yt_dlp


def download_youtube_video(url, output_path="media/video"):
    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]', 
        'merge_output_format': 'mp4',
        'outtmpl': output_path,
        'noplaylist': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    print("Video downloaded in HD quality:", output_path+"mp4")
    return output_path + ".mp4"


def extract_music(url, output_path="media/music"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if os.path.exists(output_path + ".mp3"):
        print(f"Audio already exists at: {output_path}. Skipping download.")
        return output_path + ".mp3"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
        ],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Audio downloaded and saved to: {output_path + '.mp3'}")
    except Exception as e:
        print(f"Error downloading audio: {e}")
        raise e

    # Verify audio file
    if not os.path.exists(output_path + ".mp3") or os.path.getsize(output_path + ".mp3") == 0:
        raise ValueError("Downloaded audio file is invalid or empty.")
    return output_path + ".mp3"

def clip_and_remove_audio(video_path, intervals, temp_folder="media/temp_clips"):
    os.makedirs(temp_folder, exist_ok=True)
    clips = []

    print("\n\n Video path = " + video_path.split('.')[0])
    # video_path = video_path.split('.')[0]
    
    for i, (start_time, end_time) in enumerate(intervals):
        clip = VideoFileClip(video_path).subclipped(start_time, end_time).without_audio()
        temp_clip_path = f"{temp_folder}/clip_{i}.mp4"
        clip.write_videofile(temp_clip_path, codec="libx264")
        clips.append(VideoFileClip(temp_clip_path))
        print(f"Clipped video segment {i} saved:", temp_clip_path)
    
    final_video = concatenate_videoclips(clips)
    final_video_path = os.path.join(temp_folder, "clipped_video.mp4")
    final_video.write_videofile(final_video_path, codec="libx264")
    return final_video_path

# add_music_to_video is not working we need to correct it. set_audio is depricated
def add_music_to_video(video_path, audio_path, output_path="media/final_video"):
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    if audio_clip.duration < video_clip.duration:
        loops = int(video_clip.duration // audio_clip.duration) + 1
        audio_clip = concatenate_audioclips([audio_clip] * loops).subclipped(0, video_clip.duration)
    
    video_clip = video_clip.with_audio(audio_clip)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_video_path = output_path + ".mp4"
    video_clip.write_videofile(final_video_path, codec="libx264", audio_codec="aac")
    
    print(f"Final video with music saved to: {final_video_path}")
    return final_video_path


if __name__ == "__main__":
    MEDIA_URL = 'https://www.youtube.com/watch?v=y3RIHnK0_NE&ab_channel=CorridorDigital'
    MUSIC_URL = 'https://www.youtube.com/shorts/dkt8KEDe2_Q'
    VIDEO_FILE = "media/video"
    MUSIC_FILE = "media/music"
    
    CUTTING_TIME_INTERVALS = [
        (0, 3), (11, 15), (17, 46), (49, 54), (62, 68), 
        (71, 78), (80, 89), (96, 116), (150, 159), 
        (169, 173), (180, 214), (221, 226)
    ]
    
    downloaded_video = download_youtube_video(MEDIA_URL, VIDEO_FILE)
    clipped_video = clip_and_remove_audio(downloaded_video, CUTTING_TIME_INTERVALS)
    downloaded_music = extract_music(MUSIC_URL, MUSIC_FILE)
    
    add_music_to_video(clipped_video, downloaded_music)

# def add_music_to_video(video, music_path, output_path="final_video.mp4"):
#     music = AudioFileClip(music_path)
    
#     # Repeat audio if it is shorter than the video duration
#     if music.duration < video.duration:
#         loops = int(video.duration // music.duration) + 1
#         music = concatenate_audioclips([music] * loops).subclipped(0, video.duration)
    
#     # Add the repeated or original music to the video
#     final_video = video.with_audio(music)
#     final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
#     print("Final video with music saved:", output_path)

# def add_music_to_video(video_path, music_path, output_path="final_video.mp4"):
#     # Get durations
#     video_duration = ffmpeg.probe(video_path, v='error', select_streams='v:0', show_entries='stream=duration')['streams'][0]['duration']
#     audio_duration = ffmpeg.probe(music_path, v='error', select_streams='a:0', show_entries='stream=duration')['streams'][0]['duration']

#     # Repeat audio if it's shorter than the video
#     loops = int(float(video_duration) // float(audio_duration)) + 1
#     repeated_audio_path = "media/temp_clips/repeated_audio.mp3"

#     # Use ffmpeg to repeat the audio to match the video length
#     ffmpeg.input(music_path, stream_loop=loops).output(repeated_audio_path).run()

#     # Combine video and repeated audio
#     ffmpeg.input(video_path).output(repeated_audio_path, output_path, vcodec='libx264', acodec='aac', strict='experimental').run()
#     print(f"Final video with music saved to: {output_path}")
