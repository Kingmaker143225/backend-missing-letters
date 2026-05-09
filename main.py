# import os
# import math
# import uuid
# import numpy as np

# from fastapi import FastAPI, UploadFile, File, Form
# from fastapi.responses import FileResponse
# from fastapi.middleware.cors import CORSMiddleware

# from PIL import Image, ImageDraw, ImageFont
# from moviepy import VideoClip, AudioFileClip
# from gtts import gTTS

# app = FastAPI()

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=[
# #         "https://missing-letters-app-fullstack.vercel.app",
# #         "http://localhost:5173",
# #     ],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=False,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # WIDTH = 1080
# # HEIGHT = 1920
# # FPS = 24
# # WIDTH = 720
# # HEIGHT = 1280
# # FPS = 20

# # WIDTH = 540
# # HEIGHT = 960
# # FPS = 10
# # VIDEO_DURATION = 7

# WIDTH = 360
# HEIGHT = 640
# FPS = 8
# VIDEO_DURATION = 5

# UPLOAD_DIR = "uploads"
# OUTPUT_DIR = "output"

# os.makedirs(UPLOAD_DIR, exist_ok=True)
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# BG_COLOR = "#FFD000"
# CARD_COLOR = "#FFFFFF"
# ORANGE = "#FF9500"
# BOX_FILL = "#FFE7B8"
# TEXT_COLOR = "#222222"
# GREEN = "#008000"


# def load_font(size, bold=False):
#     try:
#         if bold:
#             return ImageFont.truetype("arialbd.ttf", size)
#         return ImageFont.truetype("arial.ttf", size)
#     except:
#         return ImageFont.load_default()


# TITLE_FONT = load_font(90, True)
# LETTER_FONT = load_font(100, True)
# ANSWER_FONT = load_font(70, True)
# SMALL_FONT = load_font(45, True)
# # COUNT_FONT = load_font(120, True)
# COUNT_FONT = load_font(70, True)


# def draw_rounded_rectangle(draw, xy, radius, fill, outline=None, width=1):
#     draw.rounded_rectangle(
#         xy,
#         radius=radius,
#         fill=fill,
#         outline=outline,
#         width=width,
#     )


# def remove_white_background(image):
#     image = image.convert("RGBA")
#     data = image.getdata()
#     new_data = []

#     for item in data:
#         r, g, b, a = item

#         if (
#             (r > 220 and g > 220 and b > 220)
#             or (abs(r - g) < 12 and abs(g - b) < 12 and r > 180)
#         ):
#             new_data.append((255, 255, 255, 0))
#         else:
#             new_data.append((r, g, b, a))

#     image.putdata(new_data)
#     return image


# def draw_center_text(draw, text, y, font, fill):
#     bbox = draw.textbbox((0, 0), text, font=font)
#     text_w = bbox[2] - bbox[0]

#     draw.text(
#         ((WIDTH - text_w) / 2, y),
#         text,
#         fill=fill,
#         font=font,
#     )


# def create_frame(title, image_path, display_word, answer_word, t):
#     img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
#     draw = ImageDraw.Draw(img)

#     # dotted background
#     for x in range(70, WIDTH, 100):
#         for y in range(80, HEIGHT, 100):
#             draw.ellipse((x, y, x + 20, y + 20), fill="#FFE066")

#     # white card
#     draw_rounded_rectangle(
#         draw,
#         (90, 70, WIDTH - 90, HEIGHT - 120),
#         70,
#         CARD_COLOR,
#     )

#     # title
#     draw_center_text(draw, title, 210, TITLE_FONT, ORANGE)

#     # image
#     object_img = Image.open(image_path).convert("RGBA")
#     object_img = remove_white_background(object_img)
#     # object_img.thumbnail((430, 430))
#     object_img.thumbnail((180, 180))

#     # jump_offset = int(math.sin(t * math.pi * 2) * 35)
#     jump_offset = 0

#     obj_x = (WIDTH - object_img.width) // 2
#     obj_y = 500 - jump_offset

#     img.paste(object_img, (obj_x, obj_y), object_img)

#     show_answer = t >= 5
#     letters = list(answer_word if show_answer else display_word)

#     box_size = 155
#     gap = 25

#     total_w = len(letters) * box_size + (len(letters) - 1) * gap
#     start_x = (WIDTH - total_w) // 2
#     y = 1050

#     for i, ch in enumerate(letters):
#         x = start_x + i * (box_size + gap)

#         fill_color = BOX_FILL if ch != "_" else "#FFFFFF"

#         draw_rounded_rectangle(
#             draw,
#             (x, y, x + box_size, y + box_size),
#             35,
#             fill_color,
#             outline=ORANGE,
#             width=8,
#         )

#         if ch != "_":
#             bbox = draw.textbbox((0, 0), ch, font=LETTER_FONT)
#             text_w = bbox[2] - bbox[0]
#             text_h = bbox[3] - bbox[1]

#             draw.text(
#                 (
#                     x + (box_size - text_w) / 2,
#                     y + (box_size - text_h) / 2 - 15,
#                 ),
#                 ch,
#                 fill=TEXT_COLOR,
#                 font=LETTER_FONT,
#             )

#     if t < 5:
#         count = 5 - int(t)

#         draw_center_text(draw, str(count), 1265, COUNT_FONT, ORANGE)
#         draw_center_text(
#             draw,
#             "Find the missing letter",
#             1430,
#             SMALL_FONT,
#             "#444444",
#         )
#     else:
#         draw_center_text(
#             draw,
#             f"Answer: {answer_word}",
#             1300,
#             ANSWER_FONT,
#             GREEN,
#         )

#     return img


# @app.get("/")
# def home():
#     return {"message": "Missing Letters Video API running"}


# @app.post("/generate-video")
# async def generate_video(
#     title: str = Form(...),
#     word: str = Form(...),
#     display_word: str = Form(...),
#     image: UploadFile = File(...),
# ):
#     unique_id = str(uuid.uuid4())

#     image_path = os.path.join(UPLOAD_DIR, f"{unique_id}_{image.filename}")

#     with open(image_path, "wb") as f:
#         f.write(await image.read())

#     word = word.upper().strip()
#     display_word = display_word.upper().strip()

#     audio_text = (
#         f"Find the missing letter. "
#         f"Five. Four. Three. Two. One. "
#         f"The answer is {word}."
#     )

#     audio_path = os.path.join(OUTPUT_DIR, f"audio_{unique_id}.mp3")

#     tts = gTTS(text=audio_text, lang="en")
#     tts.save(audio_path)

#     def make_frame(t):
#         frame = create_frame(
#             title=title,
#             image_path=image_path,
#             display_word=display_word,
#             answer_word=word,
#             t=t,
#         )
#         return np.array(frame)

#     video = VideoClip(make_frame, duration=VIDEO_DURATION)
#     audio = AudioFileClip(audio_path)

#     video = video.with_audio(audio)

#     output_path = os.path.join(OUTPUT_DIR, f"{unique_id}.mp4")

#     video.write_videofile(
#         output_path,
#         fps=FPS,
#         codec="libx264",
#         audio_codec="aac",
#     )

#     audio.close()
#     video.close()

#     return FileResponse(
#         output_path,
#         media_type="video/mp4",
#         filename="missing_letters.mp4",
#     )









import os
import uuid

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
from gtts import gTTS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WIDTH = 360
# HEIGHT = 640
# FPS = 8
WIDTH = 270
HEIGHT = 480
FPS = 6

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

BG_COLOR = "#FFD000"
CARD_COLOR = "#FFFFFF"
ORANGE = "#FF9500"
BOX_FILL = "#FFE7B8"
TEXT_COLOR = "#222222"
GREEN = "#008000"


def load_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype("arialbd.ttf", size)
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()


TITLE_FONT = load_font(34, True)
LETTER_FONT = load_font(44, True)
ANSWER_FONT = load_font(28, True)
SMALL_FONT = load_font(18, True)
COUNT_FONT = load_font(54, True)


def draw_center_text(draw, text, y, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    draw.text(((WIDTH - text_w) / 2, y), text, fill=fill, font=font)


def remove_white_background(image):
    image = image.convert("RGBA")
    data = image.getdata()
    new_data = []

    for r, g, b, a in data:
        if (
            (r > 220 and g > 220 and b > 220)
            or (abs(r - g) < 12 and abs(g - b) < 12 and r > 180)
        ):
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append((r, g, b, a))

    image.putdata(new_data)
    return image


def create_frame(title, image_path, display_word, answer_word, show_answer=False, count=None):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # dotted background
    for x in range(25, WIDTH, 45):
        for y in range(35, HEIGHT, 45):
            draw.ellipse((x, y, x + 7, y + 7), fill="#FFE066")

    # white card
    draw.rounded_rectangle(
        (25, 25, WIDTH - 25, HEIGHT - 35),
        radius=28,
        fill=CARD_COLOR,
    )

    draw_center_text(draw, title, 75, TITLE_FONT, ORANGE)

    # object image
    object_img = Image.open(image_path).convert("RGBA")
    object_img = remove_white_background(object_img)
    object_img.thumbnail((140, 140))

    obj_x = (WIDTH - object_img.width) // 2
    obj_y = 165

    img.paste(object_img, (obj_x, obj_y), object_img)

    letters = list(answer_word if show_answer else display_word)

    box_size = 48
    gap = 10
    total_w = len(letters) * box_size + (len(letters) - 1) * gap
    start_x = (WIDTH - total_w) // 2
    y = 360

    for i, ch in enumerate(letters):
        x = start_x + i * (box_size + gap)

        fill_color = BOX_FILL if ch != "_" else "#FFFFFF"

        draw.rounded_rectangle(
            (x, y, x + box_size, y + box_size),
            radius=12,
            fill=fill_color,
            outline=ORANGE,
            width=3,
        )

        if ch != "_":
            bbox = draw.textbbox((0, 0), ch, font=LETTER_FONT)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]

            draw.text(
                (x + (box_size - tw) / 2, y + (box_size - th) / 2 - 5),
                ch,
                fill=TEXT_COLOR,
                font=LETTER_FONT,
            )

    if show_answer:
        draw_center_text(draw, f"Answer: {answer_word}", 455, ANSWER_FONT, GREEN)
    else:
        if count is not None:
            draw_center_text(draw, str(count), 450, COUNT_FONT, ORANGE)

        draw_center_text(draw, "Find the missing letter", 525, SMALL_FONT, "#444444")

    return img


@app.get("/")
def home():
    return {"message": "Missing Letters Video API running"}


@app.post("/generate-video")
async def generate_video(
    title: str = Form(...),
    word: str = Form(...),
    display_word: str = Form(...),
    image: UploadFile = File(...),
):
    unique_id = str(uuid.uuid4())

    word = word.upper().strip()
    display_word = display_word.upper().strip()
    title = title.strip()

    image_path = os.path.join(UPLOAD_DIR, f"{unique_id}_{image.filename}")

    with open(image_path, "wb") as f:
        f.write(await image.read())

    audio_text = f"Find the missing letter. Five. Four. Three. Two. One. The answer is {word}."
    audio_path = os.path.join(OUTPUT_DIR, f"audio_{unique_id}.mp3")

    tts = gTTS(text=audio_text, lang="en")
    tts.save(audio_path)

    # static countdown frames: much faster than frame-by-frame animation
    image_paths = []

    for count in [5, 4, 3, 2, 1]:
        frame = create_frame(
            title=title,
            image_path=image_path,
            display_word=display_word,
            answer_word=word,
            show_answer=False,
            count=count,
        )

        frame_path = os.path.join(OUTPUT_DIR, f"{unique_id}_count_{count}.png")
        frame.save(frame_path)
        image_paths.append((frame_path, 0.5))

    answer_frame = create_frame(
        title=title,
        image_path=image_path,
        display_word=display_word,
        answer_word=word,
        show_answer=True,
    )

    answer_path = os.path.join(OUTPUT_DIR, f"{unique_id}_answer.png")
    answer_frame.save(answer_path)
    image_paths.append((answer_path, 2))

    clips = [
        ImageClip(path).with_duration(duration)
        for path, duration in image_paths
    ]

    video = concatenate_videoclips(clips)

    audio = AudioFileClip(audio_path)
    video = video.with_audio(audio)

    output_path = os.path.join(OUTPUT_DIR, f"{unique_id}.mp4")

    # video.write_videofile(
    #     output_path,
    #     fps=FPS,
    #     codec="libx264",
    #     audio_codec="aac",
    #     logger=None,
    # )
    video.write_videofile(
      output_path,
      fps=FPS,
      codec="libx264",
      audio_codec="aac",
      preset="ultrafast",
      threads=2,
      logger=None,
    )

    audio.close()
    video.close()

    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename="missing_letters.mp4",
    )