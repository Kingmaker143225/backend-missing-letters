

# backend/main.py

# import os
# import uuid
# import math
# import numpy as np

# from fastapi import FastAPI, UploadFile, File, Form
# from fastapi.responses import FileResponse
# from fastapi.middleware.cors import CORSMiddleware

# from PIL import Image, ImageDraw, ImageFont
# from moviepy import VideoClip, AudioFileClip
# from gtts import gTTS

# # =========================================================
# # FASTAPI APP
# # =========================================================

# app = FastAPI(title="Missing Letters Video API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",
#         "https://missing-letters-app-fullstack.vercel.app",
#         "*",
#     ],
#     allow_credentials=False,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # =========================================================
# # VIDEO SETTINGS
# # =========================================================

# WIDTH = 720
# HEIGHT = 1280
# FPS = 24

# UPLOAD_DIR = "uploads"
# OUTPUT_DIR = "output"

# os.makedirs(UPLOAD_DIR, exist_ok=True)
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# # Colors
# BG_COLOR = "#FFD43B"
# CARD_COLOR = "#FFFFFF"
# DOT_COLOR = "#FFE066"
# ORANGE = "#FF9500"
# BOX_FILL = "#FFF2CC"
# TEXT_COLOR = "#222222"
# GREEN = "#008000"
# SHADOW_COLOR = "#DDDDDD"

# # =========================================================
# # FONT LOADER
# # =========================================================

# def load_font(size, bold=False):
#     font_candidates = []

#     if bold:
#         font_candidates = [
#             "arialbd.ttf",
#             "Arial Bold.ttf",
#             "DejaVuSans-Bold.ttf",
#         ]
#     else:
#         font_candidates = [
#             "arial.ttf",
#             "Arial.ttf",
#             "DejaVuSans.ttf",
#         ]

#     for font_name in font_candidates:
#         try:
#             return ImageFont.truetype(font_name, size)
#         except:
#             pass

#     return ImageFont.load_default()


# # TITLE_FONT = load_font(68, True)
# # LETTER_FONT = load_font(120, True)
# # COUNT_FONT = load_font(180, True)
# # ANSWER_FONT = load_font(56, True)
# # SMALL_FONT = load_font(36, True)
# # =========================
# # FONT SETTINGS
# # =========================
# TITLE_FONT = load_font(68, True)

# # Increase this to make letters inside boxes larger
# LETTER_FONT = load_font(160, True)

# # Countdown number (5,4,3,2,1)
# COUNT_FONT = load_font(220, True)

# # Final answer text (optional)
# ANSWER_FONT = load_font(72, True)

# # Small text like "Find the missing letter"
# SMALL_FONT = load_font(42, True)

# # =========================================================
# # TEXT HELPERS
# # =========================================================

# def draw_center_text(draw, text, y, font, fill):
#     bbox = draw.textbbox((0, 0), text, font=font)
#     width = bbox[2] - bbox[0]
#     x = (WIDTH - width) / 2
#     draw.text((x, y), text, font=font, fill=fill)


# # =========================================================
# # IMAGE HELPERS
# # =========================================================

# def remove_white_background(image):
#     """
#     Makes near-white pixels transparent.
#     Works for PNG and JPG.
#     """
#     image = image.convert("RGBA")
#     pixels = image.getdata()
#     new_pixels = []

#     for r, g, b, a in pixels:
#         if (
#             r > 235 and g > 235 and b > 235
#         ) or (
#             abs(r - g) < 12 and
#             abs(g - b) < 12 and
#             r > 210
#         ):
#             new_pixels.append((255, 255, 255, 0))
#         else:
#             new_pixels.append((r, g, b, a))

#     image.putdata(new_pixels)
#     return image


# def get_bounce_offset(t):
#     """
#     Creates continuous jumping effect.
#     Range: 0 to -50 pixels.
#     """
#     return int(-50 * abs(math.sin(t * math.pi * 2)))


# # =========================================================
# # DRAW WORD BOXES
# # =========================================================

# def draw_word_boxes(draw, letters):
#     box_size = 90
#     gap = 16

#     total_width = len(letters) * box_size + (len(letters) - 1) * gap
#     start_x = (WIDTH - total_width) // 2
#     y = 760

#     for i, ch in enumerate(letters):
#         x = start_x + i * (box_size + gap)

#         fill_color = "#FFFFFF" if ch == "_" else BOX_FILL

#         # Shadow
#         draw.rounded_rectangle(
#             (x + 4, y + 6, x + box_size + 4, y + box_size + 6),
#             radius=18,
#             fill=SHADOW_COLOR,
#         )

#         # Main box
#         draw.rounded_rectangle(
#             (x, y, x + box_size, y + box_size),
#             radius=18,
#             fill=fill_color,
#             outline=ORANGE,
#             width=5,
#         )

#         if ch != "_":
#             bbox = draw.textbbox((0, 0), ch, font=LETTER_FONT)
#             tw = bbox[2] - bbox[0]
#             th = bbox[3] - bbox[1]
            
#             draw.text(
#                 (
#                     x + (box_size - tw) / 2,
#                     y + (box_size - th) / 2 - 8,
#                 ),
#                 ch,
#                 font=LETTER_FONT,
#                 fill=TEXT_COLOR,
#             )


# # =========================================================
# # CREATE FRAME
# # =========================================================

# def create_frame(
#     title,
#     image_path,
#     display_word,
#     answer_word,
#     show_answer=False,
#     count=None,
#     bounce_t=0,
# ):
#     # Base canvas
#     canvas = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
#     draw = ImageDraw.Draw(canvas)

#     # Decorative dots
#     for x in range(30, WIDTH, 60):
#         for y in range(30, HEIGHT, 60):
#             draw.ellipse((x, y, x + 8, y + 8), fill=DOT_COLOR)

#     # Card shadow
#     draw.rounded_rectangle(
#         (28, 36, WIDTH - 12, HEIGHT - 4),
#         radius=40,
#         fill="#E5E5E5",
#     )

#     # White card
#     draw.rounded_rectangle(
#         (20, 20, WIDTH - 20, HEIGHT - 20),
#         radius=40,
#         fill=CARD_COLOR,
#     )

#     # Title
#     draw_center_text(draw, title, 90, TITLE_FONT, ORANGE)

#     # Load object image
#     obj = Image.open(image_path).convert("RGBA")
#     obj = remove_white_background(obj)

#     # High-quality resize
#     obj.thumbnail((360, 360), Image.LANCZOS)

#     # Jump animation
#     bounce = get_bounce_offset(bounce_t)

#     obj_x = (WIDTH - obj.width) // 2
#     obj_y = 250 + bounce

#     canvas.paste(obj, (obj_x, obj_y), obj)

#     # Word boxes
#     letters = list(answer_word if show_answer else display_word)
#     draw_word_boxes(draw, letters)

#     # Countdown
#     if not show_answer and count is not None:
#         draw_center_text(draw, str(count), 930, COUNT_FONT, ORANGE)
#         draw_center_text(
#             draw,
#             "Find the missing letter",
#             1140,
#             SMALL_FONT,
#             "#666666",
#         )

#     # Final answer
#     if show_answer:
#         draw_center_text(
#             draw,
#             f"Answer: {answer_word}",
#             980,
#             ANSWER_FONT,
#             GREEN,
#         )

#     return canvas


# # =========================================================
# # ROUTES
# # =========================================================

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

#     title = title.strip()
#     word = word.upper().strip()
#     display_word = display_word.upper().strip()

#     # Save uploaded image
#     image_path = os.path.join(
#         UPLOAD_DIR,
#         f"{unique_id}_{image.filename}"
#     )

#     with open(image_path, "wb") as f:
#         f.write(await image.read())

#     # =====================================================
#     # GENERATE AUDIO
#     # =====================================================

#     audio_text = (
#         "Find the missing letter. "
#         "5... 4... 3... 2... 1... "
#         f"The answer is {word}."
#     )

#     audio_path = os.path.join(OUTPUT_DIR, f"{unique_id}.mp3")
#     gTTS(text=audio_text, lang="en").save(audio_path)

#     # Load audio to get exact duration
#     audio = AudioFileClip(audio_path)
#     total_duration = audio.duration

#     # =====================================================
#     # FRAME FUNCTION
#     # =====================================================

#     def make_frame(t):
#         if t < 5:
#             count = max(1, 5 - int(t))

#             frame = create_frame(
#                 title=title,
#                 image_path=image_path,
#                 display_word=display_word,
#                 answer_word=word,
#                 show_answer=False,
#                 count=count,
#                 bounce_t=t,
#             )
#         else:
#             frame = create_frame(
#                 title=title,
#                 image_path=image_path,
#                 display_word=display_word,
#                 answer_word=word,
#                 show_answer=True,
#                 bounce_t=t,
#             )

#         return np.array(frame)

#     # =====================================================
#     # CREATE VIDEO
#     # =====================================================

#     video = VideoClip(make_frame, duration=total_duration)
#     video = video.with_audio(audio)

#     output_path = os.path.join(
#         OUTPUT_DIR,
#         f"{unique_id}.mp4"
#     )

#     video.write_videofile(
#         output_path,
#         fps=FPS,
#         codec="libx264",
#         audio_codec="aac",
#         preset="ultrafast",
#         threads=2,
#         logger=None,
#     )

#     # Close resources
#     audio.close()
#     video.close()

#     # Return generated video
#     return FileResponse(
#         output_path,
#         media_type="video/mp4",
#         filename="missing_letters.mp4",
#     )












import os
import uuid
import math
import numpy as np

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip, AudioFileClip
from gtts import gTTS

# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(title="Missing Letters Video API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://missing-letters-app-fullstack.vercel.app",
        "*",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# VIDEO SETTINGS
# =========================================================

WIDTH = 720
HEIGHT = 1280
FPS = 24

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Colors
BG_COLOR = "#FFD43B"
CARD_COLOR = "#FFFFFF"
DOT_COLOR = "#FFE066"
ORANGE = "#FF9500"
BOX_FILL = "#FFF2CC"
TEXT_COLOR = "#222222"
GREEN = "#00AA00"
SHADOW_COLOR = "#DDDDDD"

# =========================================================
# FONT LOADER
# =========================================================

def load_font(size, bold=False):
    font_candidates = []

    if bold:
        font_candidates = [
            "arialbd.ttf",
            "Arial Bold.ttf",
            "DejaVuSans-Bold.ttf",
        ]
    else:
        font_candidates = [
            "arial.ttf",
            "Arial.ttf",
            "DejaVuSans.ttf",
        ]

    for font_name in font_candidates:
        try:
            return ImageFont.truetype(font_name, size)
        except:
            pass

    return ImageFont.load_default()


# =========================================================
# FONT SETTINGS
# =========================================================

TITLE_FONT = load_font(68, True)

# Bigger letters
LETTER_FONT = load_font(120, True)

# Bigger countdown
COUNT_FONT = load_font(220, True)

# Bigger answer
ANSWER_FONT = load_font(78, True)

SMALL_FONT = load_font(42, True)

# =========================================================
# TEXT HELPERS
# =========================================================

def draw_center_text(draw, text, y, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    x = (WIDTH - width) / 2
    draw.text((x, y), text, font=font, fill=fill)


# =========================================================
# IMAGE HELPERS
# =========================================================

def remove_white_background(image):
    """
    Makes near-white pixels transparent.
    """
    image = image.convert("RGBA")
    pixels = image.getdata()
    new_pixels = []

    for r, g, b, a in pixels:
        if (
            r > 235 and g > 235 and b > 235
        ) or (
            abs(r - g) < 12 and
            abs(g - b) < 12 and
            r > 210
        ):
            new_pixels.append((255, 255, 255, 0))
        else:
            new_pixels.append((r, g, b, a))

    image.putdata(new_pixels)
    return image


def get_bounce_offset(t):
    """
    Creates continuous jumping effect.
    """
    return int(-50 * abs(math.sin(t * math.pi * 2)))


# =========================================================
# DRAW WORD BOXES
# =========================================================

def draw_word_boxes(draw, letters, show_answer=False):

    # Bigger boxes
    box_size = 180
    gap = 24

    total_width = len(letters) * box_size + (len(letters) - 1) * gap
    start_x = (WIDTH - total_width) // 2

    y = 760

    for i, ch in enumerate(letters):

        x = start_x + i * (box_size + gap)

        fill_color = "#FFFFFF" if ch == "_" else BOX_FILL

        # Shadow
        draw.rounded_rectangle(
            (x + 4, y + 6, x + box_size + 4, y + box_size + 6),
            radius=18,
            fill=SHADOW_COLOR,
        )

        # Main box
        draw.rounded_rectangle(
            (x, y, x + box_size, y + box_size),
            radius=18,
            fill=fill_color,
            outline=ORANGE,
            width=5,
        )

        if ch != "_":

            bbox = draw.textbbox((0, 0), ch, font=LETTER_FONT)

            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]

            draw.text(
                (
                    x + (box_size - tw) / 2,
                    y + (box_size - th) / 2 - 12,
                ),
                ch,
                font=LETTER_FONT,

                # GREEN AFTER REVEAL
                fill=GREEN if show_answer else TEXT_COLOR,
            )


# =========================================================
# CREATE FRAME
# =========================================================

def create_frame(
    title,
    image_path,
    display_word,
    answer_word,
    show_answer=False,
    count=None,
    bounce_t=0,
):

    # Base canvas
    canvas = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    # Decorative dots
    for x in range(30, WIDTH, 60):
        for y in range(30, HEIGHT, 60):
            draw.ellipse((x, y, x + 8, y + 8), fill=DOT_COLOR)

    # Card shadow
    draw.rounded_rectangle(
        (28, 36, WIDTH - 12, HEIGHT - 4),
        radius=40,
        fill="#E5E5E5",
    )

    # White card
    draw.rounded_rectangle(
        (20, 20, WIDTH - 20, HEIGHT - 20),
        radius=40,
        fill=CARD_COLOR,
    )

    # Title
    draw_center_text(draw, title, 90, TITLE_FONT, ORANGE)

    # =====================================================
    # LOAD IMAGE
    # =====================================================

    obj = Image.open(image_path).convert("RGBA")
    obj = remove_white_background(obj)

    obj.thumbnail((360, 360), Image.LANCZOS)

    bounce = get_bounce_offset(bounce_t)

    obj_x = (WIDTH - obj.width) // 2
    obj_y = 250 + bounce

    canvas.paste(obj, (obj_x, obj_y), obj)

    # =====================================================
    # WORD BOXES
    # =====================================================

    letters = list(answer_word if show_answer else display_word)

    draw_word_boxes(draw, letters, show_answer)

    # =====================================================
    # COUNTDOWN
    # =====================================================

    if not show_answer and count is not None:

        draw_center_text(
            draw,
            str(count),
            940,
            COUNT_FONT,
            ORANGE,
        )

        draw_center_text(
            draw,
            "Find the missing letter",
            1140,
            SMALL_FONT,
            "#666666",
        )

    # =====================================================
    # ANSWER REVEAL
    # =====================================================

    if show_answer:

        draw_center_text(
            draw,
            f"Answer: {answer_word}",
            980,
            ANSWER_FONT,
            GREEN,
        )

    return canvas


# =========================================================
# HOME ROUTE
# =========================================================

@app.get("/")
def home():
    return {"message": "Missing Letters Video API running"}


# =========================================================
# GENERATE VIDEO ROUTE
# =========================================================

@app.post("/generate-video")
async def generate_video(
    title: str = Form(...),
    word: str = Form(...),
    display_word: str = Form(...),
    image: UploadFile = File(...),
):

    unique_id = str(uuid.uuid4())

    title = title.strip()
    word = word.upper().strip()
    display_word = display_word.upper().strip()

    # =====================================================
    # SAVE IMAGE
    # =====================================================

    image_path = os.path.join(
        UPLOAD_DIR,
        f"{unique_id}_{image.filename}"
    )

    with open(image_path, "wb") as f:
        f.write(await image.read())

    # =====================================================
    # GENERATE AUDIO
    # =====================================================

    audio_text = (
        "Find the missing letter. "
        "5... 4... 3... 2... 1... "
        f"The answer is {word}."
    )

    audio_path = os.path.join(
        OUTPUT_DIR,
        f"{unique_id}.mp3"
    )

    gTTS(
        text=audio_text,
        lang="en",
        slow=False,
    ).save(audio_path)

    # =====================================================
    # LOAD AUDIO
    # =====================================================

    audio = AudioFileClip(audio_path)

    total_duration = audio.duration

    # =====================================================
    # FRAME FUNCTION
    # =====================================================

    def make_frame(t):

        # -------------------------------------------------
        # 1 SECOND INTRO DELAY
        # -------------------------------------------------

        if t < 1:

            frame = create_frame(
                title=title,
                image_path=image_path,
                display_word=display_word,
                answer_word=word,
                show_answer=False,
                count=5,
                bounce_t=t,
            )

        # -------------------------------------------------
        # COUNTDOWN
        # -------------------------------------------------

        elif t < 6:

            count = max(1, 6 - int(t))

            frame = create_frame(
                title=title,
                image_path=image_path,
                display_word=display_word,
                answer_word=word,
                show_answer=False,
                count=count,
                bounce_t=t,
            )

        # -------------------------------------------------
        # ANSWER
        # -------------------------------------------------

        else:

            frame = create_frame(
                title=title,
                image_path=image_path,
                display_word=display_word,
                answer_word=word,
                show_answer=True,
                bounce_t=t,
            )

        return np.array(frame)

    # =====================================================
    # CREATE VIDEO
    # =====================================================

    video = VideoClip(
        make_frame,
        duration=total_duration
    )

    video = video.with_audio(audio)

    output_path = os.path.join(
        OUTPUT_DIR,
        f"{unique_id}.mp4"
    )

    video.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=2,
        logger=None,
    )

    # =====================================================
    # CLEANUP
    # =====================================================

    audio.close()
    video.close()

    # =====================================================
    # RETURN VIDEO
    # =====================================================

    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename="missing_letters.mp4",
    )