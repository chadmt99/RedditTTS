import argparse
import json
import redtts.reddit.reddit as r
import redtts.utils as utils
import redtts.speech.speech as speech
import redtts.image.image as im
import redtts.video.stitcher as stitch


parser = argparse.ArgumentParser(description='Make videos.')
parser.add_argument('--config', default='',
                    help='Location of config.')
args = parser.parse_args()


WIDTH = 1920
HEIGHT = 1080


def main():
    # Load in config file.
    with open(args.config) as f:
        config = json.load(f)["config"]

    # Instantiate a video stitcher.
    stitcher = stitch.Stitcher(
        filepath="_tmp/video",
        fps=2,
        width=WIDTH,
        height=HEIGHT
    )

    # Iterate through the config.
    for i, segment in enumerate(config):
        # Extract content from url.
        URL = segment["url"]
        content_generator = r.ContentGenerator(url=URL)

        # Tokenize submission
        submission = content_generator.submission
        text_list = [submission.title]
        text_list.extend(utils.tokenize(submission.selftext))

        # Generate images and audio.
        text_to_image = im.render_submission(
            submission=submission,
            text_font_size=42,
            text_font=segment["text_font"],
            image_max_length=WIDTH,
            image_max_height=HEIGHT,
            filepath="_tmp/images_%s" % str(i),
            title_font=segment["title_font"],
            title_size=60
        )
        vb = speech.VoiceBot(rate_delta=segment["rate_delta"])
        text_to_speech = vb.generate_speech_files(
            text_list=text_list,
            filepath="_tmp/audio_%s" % str(i),
            submission=submission,
            include_intro=segment["include_intro"]
        )

        # Make video.
        stitcher.stitch(text_list, text_to_image, text_to_speech)

    # Compile all videos and add background music.
    stitcher.compile_all_videos(
        include_outro=True,
        voice_bot=vb
    )
    stitcher.add_background_music(
        volume_delta=-30
    )


if __name__ == "__main__":
    main()