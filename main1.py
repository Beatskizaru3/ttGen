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

# Конфигурация папок
folder_main = "./main"
folder_bg = "./bgr"
output_folder = "./output"
os.makedirs(output_folder, exist_ok=True)

# Загрузка основного видео
try:
    main_video = VideoFileClip(os.path.join(folder_main, "main.mp4"))
except Exception as e:
    print(f"Ошибка загрузки видео: {e}")
    exit(1)

# Проверка фоновых видео
bg_videos = [os.path.join(folder_bg, f) for f in os.listdir(folder_bg) 
            if f.endswith(".mp4")]
if not bg_videos:
    print("Ошибка: отсутствуют фоновые видео")
    exit(1)

# Параметры обработки
VIDEO_COUNT = 5
FADE_DURATION = 0.01

for i in range(VIDEO_COUNT):
    try:
        # Генерация случайных параметров
        speed = random.uniform(1.15, 1.25)
        rotation = random.uniform(-3, 3)
        brightness = random.uniform(0.95, 1.05)
        contrast = random.uniform(0.95, 1.05)
        saturation = random.uniform(0.95, 1.05)

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
            volume_factor = random.uniform(0.98, 1.02)
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

        # Собираем финальный клип с аудио
        final = CompositeVideoClip([
            bg_clip, 
            processed.with_position("center")
        ])

        # Экспорт
        output_path = os.path.join(output_folder, f"video_{i+1}.mp4")
        final.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=30,
            preset="slow",
            ffmpeg_params=["-profile:v", "main", "-level", "3.1"]
        )
        print(f"Успешно: {output_path}")

    except Exception as e:
        print(f"Ошибка при обработке видео {i+1}: {str(e)}")

main_video.close()
print("Обработка завершена!")