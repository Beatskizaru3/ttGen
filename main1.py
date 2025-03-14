import random
import os
import numpy as np

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.AudioClip import AudioClip
from moviepy import CompositeAudioClip
from moviepy.video.fx.MultiplySpeed import MultiplySpeed
from moviepy.video.fx.Rotate import Rotate
from moviepy.video.fx.MultiplyColor import MultiplyColor
from moviepy.video.fx.LumContrast import LumContrast
from moviepy.audio.fx.AudioFadeIn import AudioFadeIn
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume
from moviepy.video.fx.Resize import Resize

# Функция для чтения конфигурации из файла
def read_config(config_file):
    config = {}
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    return config

# Загрузка конфигурации
config = read_config("config.txt")

def get_config_value(key, default, cast_func):
    return cast_func(config.get(key, default))

# Параметры из конфигурационного файла с преобразованием типов
VIDEO_COUNT = get_config_value("VIDEO_COUNT", "5", int)
FADE_DURATION = get_config_value("FADE_DURATION", "0.01", float)

# Разбор разрешения iPhone 13 из строки формата "1170,2532"
resolution_str = config.get("IPHONE_RESOLUTION", "1170,2532")
width_str, height_str = resolution_str.split(",")
IPHONE_RESOLUTION = (int(width_str), int(height_str))

TARGET_WIDTH_PERCENTAGE = get_config_value("TARGET_WIDTH_PERCENTAGE", "0.95", float)

# Дополнительные параметры для генерации случайных эффектов
SPEED_MIN = get_config_value("SPEED_MIN", "1.15", float)
SPEED_MAX = get_config_value("SPEED_MAX", "1.25", float)
ROTATION_MIN = get_config_value("ROTATION_MIN", "-1", float)
ROTATION_MAX = get_config_value("ROTATION_MAX", "1", float)
BRIGHTNESS_MIN = get_config_value("BRIGHTNESS_MIN", "0.95", float)
BRIGHTNESS_MAX = get_config_value("BRIGHTNESS_MAX", "1.05", float)
CONTRAST_MIN = get_config_value("CONTRAST_MIN", "0.95", float)
CONTRAST_MAX = get_config_value("CONTRAST_MAX", "1.05", float)
SATURATION_MIN = get_config_value("SATURATION_MIN", "0.95", float)
SATURATION_MAX = get_config_value("SATURATION_MAX", "1.05", float)
VOLUME_MIN = get_config_value("VOLUME_MIN", "0.98", float)
VOLUME_MAX = get_config_value("VOLUME_MAX", "1.02", float)
FPS = get_config_value("FPS", "30", int)

# Конфигурация папок
folder_main = "./main"
folder_bg = "./bgr"
output_folder = "./output"
os.makedirs(output_folder, exist_ok=True)

# Поиск единственного видеофайла в папке main
main_files = [f for f in os.listdir(folder_main) if f.lower().endswith((".mp4", ".avi", ".mov", ".mkv"))]
if not main_files:
    print("Ошибка: в папке main не найдено видео")
    exit(1)
elif len(main_files) > 1:
    print("Предупреждение: найдено более одного файла в папке main. Будет использован первый.")
main_video_path = os.path.join(folder_main, main_files[0])

# Загрузка основного видео
try:
    main_video = VideoFileClip(main_video_path)
except Exception as e:
    print(f"Ошибка загрузки видео: {e}")
    exit(1)

# Проверка фоновых видео
bg_videos = [os.path.join(folder_bg, f) for f in os.listdir(folder_bg) if f.lower().endswith(".mp4")]
if not bg_videos:
    print("Ошибка: отсутствуют фоновые видео")
    exit(1)

for i in range(VIDEO_COUNT):
    try:
        # Генерация случайных параметров
        speed = random.uniform(SPEED_MIN, SPEED_MAX)
        rotation = random.uniform(ROTATION_MIN, ROTATION_MAX)
        brightness = random.uniform(BRIGHTNESS_MIN, BRIGHTNESS_MAX)
        contrast = random.uniform(CONTRAST_MIN, CONTRAST_MAX)
        saturation = random.uniform(SATURATION_MIN, SATURATION_MAX)

        # Последовательное применение эффектов
        processed = main_video

        # 1. Ускорение видео
        processed = MultiplySpeed(factor=speed).apply(processed)

        # 2. Поворот
        processed = Rotate(angle=rotation, unit="deg").apply(processed)

        # 3. Яркость
        processed = MultiplyColor(factor=brightness).apply(processed)

        # 4. Контраст
        processed = LumContrast(contrast=contrast).apply(processed)

        # 5. Насыщенность
        processed = MultiplyColor(factor=saturation).apply(processed)

        # Обработка аудио
        audio = processed.audio
        if audio:
            fade_in = AudioFadeIn(duration=FADE_DURATION).apply(audio)
            volume_factor = random.uniform(VOLUME_MIN, VOLUME_MAX)
            audio = MultiplyVolume(factor=volume_factor).apply(fade_in)

            # Добавление шума
            noise = AudioClip(
                lambda t: random.uniform(0.001, 0.005) * (2 * np.random.random() - 1),
                duration=processed.duration,
                fps=audio.fps
            )
            processed = processed.with_audio(CompositeAudioClip([audio, noise]))

        # Композиция с фоновым видео
        bg_clip = VideoFileClip(random.choice(bg_videos))
        bg_clip = bg_clip.with_duration(processed.duration).without_audio()

        if bg_clip.duration < processed.duration:
            bg_clip = bg_clip.loop(duration=processed.duration)

        # Масштабирование основного видео с сохранением пропорций и строгой шириной 95%
        main_width, main_height = processed.size
        target_width, target_height = IPHONE_RESOLUTION
        new_width = int(target_width * TARGET_WIDTH_PERCENTAGE)
        aspect_ratio_main = main_width / main_height

        # Вычисляем высоту с сохранением пропорций
        new_height = int(new_width / aspect_ratio_main)

        # Применяем Resize с сохранением пропорций
        processed = Resize(width=new_width, height=new_height).apply(processed)

        # Масштабируем фоновое видео под разрешение iPhone 13
        bg_clip = Resize(width=target_width, height=target_height).apply(bg_clip)

        # Центрируем главное видео
        x_center = (target_width - new_width) // 2
        y_center = (target_height - new_height) // 2

        # Собираем финальный клип
        final = CompositeVideoClip([
            bg_clip,
            processed.with_position((x_center, y_center))
        ], size=IPHONE_RESOLUTION)

        # Экспорт
        output_path = os.path.join(output_folder, f"{i+1}.mp4")
        final.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=FPS,
            preset="slow",
            ffmpeg_params=["-profile:v", "main", "-level", "3.1"]
        )
        print(f"Успешно: {output_path}")

    except Exception as e:
        print(f"Ошибка при обработке видео {i+1}: {str(e)}")

main_video.close()
print("Обработка завершена!")
