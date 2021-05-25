from PIL import ImageFont, Image, ImageDraw
from typing import List, Dict
from .. import utils
import os
import praw


def render_submission(submission: praw.models.Submission, text_font_size: int,
                      text_font: str, image_max_length: int,
                      image_max_height: int, filepath: str, title_font: str,
                      title_size: int) -> Dict[str, str]:
    """Render a reddit submission into a sequence of images.

    Submission, each image should contain consecutive sentences overlayed on
    it. If text overflows from an image frame, continue to a fresh image frame
    continuing the sentence overlay process.
    Args:
        submission: Reddit submission to be rendered.
        text_font_size: Font size of the submission renderer.
        text_font: Font style.
        image_max_length: Length of the image frame.
        image_max_height: Height of the image frame.
        filepath: String representing path of image.
    Return:
        Dictionary mapping sentence string to filename.
    """
    # Tokenizes paragraph by sentence.
    text = submission.selftext
    text_list = utils.tokenize(text)

    # Open up/down arrow images.
    up_arrow = Image.open(utils.get_asset_filepath()+"/up_arrow.png")
    down_arrow = Image.open(utils.get_asset_filepath()+"/down_arrow.png")
    up_arrow = up_arrow.resize((190, 190))
    down_arrow = down_arrow.resize((190, 190))

    # Declare the image object with the specified dimensions provided
    # to the function. Declare the font with the specified font.
    # Declare the draw object to be used to write text to the image object
    image = Image.new(mode="RGBA", size=(image_max_length, image_max_height),
                      color=(20, 20, 20))
    fnt = ImageFont.truetype(text_font, text_font_size)
    title_fnt = ImageFont.truetype(title_font, title_size)
    score_fnt = ImageFont.truetype(title_font, text_font_size)
    author_fnt = ImageFont.truetype(text_font, text_font_size - 12)
    draw = ImageDraw.Draw(image)

    # Map to store text keyed to filenames of images.
    image_map = {}

    # Declare top margin
    top_margin = title_size*2 + 30

    # Draw score and declare left_margin
    if int(submission.score) > 999:
        score = str(round(int(submission.score)/1000, 2)) + "K"
        draw.text((10, int(top_margin*.55)), score,
                  font=score_fnt, fill=(225, 225, 225), align="left")
        left_margin = fnt.getsize(score + "   ")[0]
    else:
        score = str(submission.score)
        draw.text((10, int(top_margin*.55)), score,
                  font=score_fnt, fill=(225, 225, 225), align="left")
        left_margin = fnt.getsize(score + "   ")[0]

    # Draw the Arrows
    image.paste(
        up_arrow, (int(left_margin/2) - 15, int(top_margin*.2)), mask=up_arrow
    )
    image.paste(
        down_arrow, (int(left_margin/2) - 15, int(top_margin)+5),
        mask=down_arrow
    )

    # Draw author.
    draw.text(
        (left_margin, int(text_font_size * .2)),
        "Posted by u/"+str(submission.author),
        font=author_fnt, fill=(180, 180, 180),
        align="left"
    )
    # Draw title.
    title_x_position = left_margin
    title_y_position = 5 + text_font_size + int(text_font_size / 2)
    title_words = str(submission.title).split(" ")
    for word in title_words:
        if title_x_position + title_fnt.getsize(word + " ")[0] > image_max_length:
            title_y_position = title_y_position + 15 + title_size
            title_x_position = left_margin
            draw.text(
                (title_x_position, title_y_position), word,
                font=title_fnt, fill=(225, 225, 225), align="left"
            )
            title_x_position = (
                    title_x_position + title_fnt.getsize(word + " ")[0]
            )
            top_margin = top_margin + 30 + title_size
        else:
            draw.text(
                (title_x_position, title_y_position), word,
                font=title_fnt, fill=(225, 225, 225), align="left"
            )
            title_x_position = (
                    title_x_position + title_fnt.getsize(word + " ")[0]
            )

    # Write to files.
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    filename = filepath + "/image_%s.png" % str(0)
    image_map[str(submission.title)+str(0)] = filename
    image.save(filename)

    x = left_margin
    y = top_margin

    # Count is for the number related to the png files double_new_line variable
    # is used to handle newline characters in strings sentence_too_long is the
    # variable to account for setences that would not fit on same image.
    count = 1
    sentence_too_long = 0

    # Create directory.
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    for i in range(0, len(text_list)):
        # Splits splits sentence by the lines exposing newlines as '' in the
        # split_on_newline list
        split_on_newline = text_list[i].splitlines()
        if '' in split_on_newline:
            while '' in split_on_newline:
                split_on_newline.remove('')
            x = left_margin
            y = y + 15 + text_font_size * 2

        for splits in split_on_newline:
            words = splits.split(" ")
            while '' in words:
                words.remove('')
            for word in words:
                # If the added word exceeds the dimensions of the image
                if ((x + fnt.getsize(word + " ")[0]) > image_max_length
                        or (image_max_height - (y+15)) < text_font_size):
                    # check if it exceeded the y dimension first
                    if ((image_max_height - y) < text_font_size or
                            abs((y + 15 + text_font_size) - image_max_height)
                            < text_font_size):
                        sentence_too_long = 1
                        break
                    # handles exceeding x dimensions
                    else:
                        x = left_margin
                        y = y + 15 + text_font_size
                        draw.text((x, y), word, font=fnt, fill=(225, 225, 225),
                                  align="left")
                        x = x + fnt.getsize(word + " ")[0]
                else:
                    # If adding new word doesnt exceed size of image draw it,
                    # then increment x the length of the word.
                    draw.text((x, y), word, font=fnt, fill=(225, 225, 225),
                              align="left")
                    x = x + fnt.getsize(word + " ")[0]

            # If the sentence was too long come back to beginning of outer for-
            # loop(word loop) and put the sentence on a new image only equal to
            # 1 if the entire sentence does not fit on image
            if sentence_too_long == 1:
                sentence_too_long = 0
                image = Image.new(
                    mode="RGBA", size=(image_max_length, image_max_height),
                    color=(20, 20, 20)
                )
                draw = ImageDraw.Draw(image)
                x = left_margin
                y = 5
                words = splits.split(" ")
                while '' in words:
                    words.remove('')
                for word in words:
                    if (x + fnt.getsize(word + " ")[0]) > image_max_length:
                        x = left_margin
                        y = y + 15 + text_font_size
                        draw.text((x, y), word, font=fnt, fill=(225, 225, 225),
                                  align="left")
                        x = x + fnt.getsize(word + " ")[0]
                    else:
                        draw.text((x, y), word, font=fnt, fill=(225, 225, 225),
                                  align="left")
                        x = x + fnt.getsize(word + " ")[0]
        filename = filepath + "/image_%s.png" % str(count)
        image_map[text_list[i] + str(count)] = filename
        image.save(filename)
        count += 1

    return image_map


def render_comment_chains(comment_chains: List[List[praw.models.Comment]],
                          filename: str, font_size: int, font: str,
                          image_max_length: int, image_max_height: int):
    """Render a reddit comment chains into a sequence of images.

    Each image should contain consecutive sentences overlayed on
    it. If text overflows from an image frame, continue to a fresh image frame
    continuing the sentence overlay process. This should format the image
    in a similar way to how Reddit renders comment chains, with consecutive
    comments in a chain indented. The first comment of every chain starts
    fresh without indentations.
    Args:
        submission: Reddit submission to be rendered.
        filename: Filename to store the images.
        font_size: Font size of the submission renderer.
        font: Font style.
        image_max_length: Length of the image frame.
        image_max_height: Height of the image frame.
    Return:
        Dictionary mapping sentence string to filename.
    """
    return
