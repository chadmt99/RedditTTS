from pydub import AudioSegment
from .. import utils
from . import constants
import cv2
import math
import moviepy.editor as mpe
import os


class Stitcher(object):
    """Stitch audio and image together to make video."""

    def __init__(self, filepath, fps, width, height):
        """ Initialize video stitcher.

        VoiceBot to speak lines and generate text to speech data.
        Args:
            filepath: Directory to store videos.
            fps: FPS of video.
            width: Width of each video frame in pixels.
            height: Height of each video frame in pixels.
        """
        self.filepath = filepath
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        self.fps, self.width, self.height = fps, width, height
        self.videos = []
        self.composite_video_filename = None

    def stitch(self, text_list, image_map, audio_map):
        """Stitch together image and audio files into a video."""
        current_filepath = self.filepath + "/video_%s" % str(len(self.videos))
        if not os.path.exists(current_filepath):
            os.makedirs(current_filepath)
        video_filename = current_filepath + "/video.mp4"
        video = cv2.VideoWriter(
            filename=video_filename, fourcc=cv2.VideoWriter_fourcc(*'mp4v'),
            fps=self.fps, frameSize=(self.width, self.height)
        )
        # Render video frames.
        for i, text_key in enumerate(text_list):
            image_filename = image_map[text_key + str(i)]
            audio_filename = audio_map[text_key + str(i)]
            audio = AudioSegment.from_file(audio_filename)

            # Calculate the number of frames to add for this section of audio.
            num_frames = int(math.ceil(
                (len(audio) / 1000.0) / (1.0 / self.fps)))
            for _ in range(num_frames):
                video.write(cv2.imread(image_filename))

            # Pad the audio file to account for the fps.
            desired_duration = int((num_frames/float(self.fps)) * 1000)
            padded_duration = desired_duration - len(audio)
            padded_audio = AudioSegment.silent(duration=padded_duration)
            audio = audio + padded_audio
            audio.export(audio_filename)

        video.release()
        cv2.destroyAllWindows()

        # Compile audio.
        combined_audio = AudioSegment.empty()
        for i, text_key in enumerate(text_list):
            combined_audio += AudioSegment.from_file(
                audio_map[text_key + str(i)]
            )
        combined_audio_filename = current_filepath + "/audio.mp3"
        combined_audio.export(combined_audio_filename)

        # Overlay audio onto video.
        video_clip = mpe.VideoFileClip(video_filename)
        audio_clip = mpe.AudioFileClip(combined_audio_filename)
        new_audioclip = mpe.CompositeAudioClip([audio_clip])
        video_clip.audio = new_audioclip
        final_video_file_name = current_filepath + "/video_audio.mp4"
        video_clip.write_videofile(final_video_file_name)
        self.videos.append(final_video_file_name)

    def stitch_outro(self, voice_bot):
        """Create outro."""
        outro_background_filename = (
                utils.get_asset_filepath() +
                "/outro_background.png"
        )
        audio_map = voice_bot.generate_speech_files(
            text_list=[constants.OUTRO],
            filepath=self.filepath + "/outro_audio",
            submission=None,
            include_intro=False
        )
        text_key = constants.OUTRO + "0"
        image_map = {text_key: outro_background_filename}
        self.stitch(
            [constants.OUTRO], image_map, audio_map
        )

    def compile_all_videos(self, include_outro=False, voice_bot=None):
        """Compile all videos into one video."""
        if include_outro:
            self.stitch_outro(voice_bot)
        clips = [
            mpe.VideoFileClip(video_filename) for video_filename
            in self.videos
        ]

        concat_clip = mpe.concatenate_videoclips(clips)
        self.composite_video_filename = self.filepath + "/composite_video.mp4"
        concat_clip.write_videofile(self.composite_video_filename)

    def add_background_music(self, volume_delta=0):
        """Overlay background music onto the video."""
        if self.composite_video_filename is None:
            print("Please compile all videos.")

        # Get the video duration in milliseconds.
        video_clip = mpe.VideoFileClip(self.composite_video_filename)
        video_duration = int(video_clip.duration * 1000)

        # Load background music, extend it to be the duration of video.
        background_audio_filename = (
            utils.get_asset_filepath() +
            "/background_music/bensound-allthat.mp3"
        )
        background_audio = AudioSegment.from_file(background_audio_filename)
        background_audio = background_audio + volume_delta
        while len(background_audio) < video_duration:
            background_audio += background_audio
        background_audio = background_audio[:video_duration]
        video_background_audio_filename = (
                self.filepath + "/background_audio.mp3"
        )
        background_audio.export(video_background_audio_filename)

        # Add to video.
        audio_clip = mpe.AudioFileClip(
            video_background_audio_filename
        ).set_duration(video_clip.duration)
        new_audio = mpe.CompositeAudioClip([video_clip.audio, audio_clip])
        video_clip.audio = new_audio

        # Write out video with background audio.
        final_video_file_name = self.filepath + "/composite_video_bg.mp4"
        video_clip.write_videofile(final_video_file_name)
