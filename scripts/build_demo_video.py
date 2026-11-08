"""Build a captioned, narrated MP4 from genuine browser captures.

This is an edited still-frame walkthrough, not a continuous screen recording.
Run narrate_demo.ps1 first. Uses bundled Pillow and project-local FFmpeg.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import wave

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.cache/video-python'))
import imageio_ffmpeg

VIDEO = ROOT / 'submission/agent-rush/video'
BUILD = VIDEO / '.build'
W, H = 1920, 1080
C = {'paper': '#EDF2F3', 'ink': '#162633', 'teal': '#215B58', 'muted': '#465B65', 'line': '#BDCDD1', 'dark': '#173238'}
FONT_DIR = Path('C:/Windows/Fonts')


def font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


def lines(text, face, width):
    result, current = [], ''
    for word in text.split():
        trial = (current + ' ' + word).strip()
        if current and face.getlength(trial) > width:
            result.append(current)
            current = word
        else:
            current = trial
    if current:
        result.append(current)
    return result


def put(draw, text, xy, face, width, fill, leading):
    x, y = xy
    rows = lines(text, face, width)
    for row in rows:
        draw.text((x, y), row, font=face, fill=fill)
        y += leading
    return y


def chunks(text, limit=122):
    result, current = [], ''
    for word in text.split():
        trial = (current + ' ' + word).strip()
        if current and len(trial) > limit:
            result.append(current)
            current = word
        else:
            current = trial
    if current:
        result.append(current)
    return result


def timecode(seconds):
    ms = round(seconds * 1000)
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    secs, ms = divmod(ms, 1000)
    return f'{hours:02}:{minutes:02}:{secs:02},{ms:03}'


def scene_canvas(scene, index, count):
    img = Image.new('RGB', (W, H), C['paper'])
    draw = ImageDraw.Draw(img)
    draw.text((88, 35), 'Prooflane', font=font('georgia.ttf', 43), fill=C['ink'])
    draw.text((1360, 51), 'VULTR AGENT RUSH  2026', font=font('segoeui.ttf', 23), fill=C['muted'])
    draw.line((88, 109, 1832, 109), fill=C['line'], width=2)
    draw.text((92, 158), f'{index:02}   {scene["label"]}', font=font('segoeuib.ttf', 22), fill=C['teal'])
    y = put(draw, scene['title'], (88, 219), font('georgia.ttf', 58), 770, C['ink'], 72)
    y = max(y + 49, 440)
    for item in scene['facts']:
        draw.line((92, y + 17, 121, y + 17), fill=C['teal'], width=3)
        y = put(draw, item, (145, y), font('segoeui.ttf', 31), 685, C['ink'], 43) + 25
    if scene.get('source'):
        source = (VIDEO / scene['source']).resolve()
        shot = Image.open(source).convert('RGB')
        if scene.get('crop'):
            x0, y0, x1, y1 = scene['crop']
            if not (0 <= x0 < x1 <= shot.width and 0 <= y0 < y1 <= shot.height):
                raise ValueError(f'Invalid capture crop: {source.name}')
            shot = shot.crop((x0, y0, x1, y1))
        shot = ImageOps.contain(shot, (880, 750), Image.Resampling.LANCZOS)
        px, py = 955 + (880 - shot.width) // 2, 157 + (750 - shot.height) // 2
        draw.rectangle((px - 2, py - 2, px + shot.width + 2, py + shot.height + 2), fill=C['line'])
        img.paste(shot, (px, py))
    else:
        y = 235
        for name in ['Nurali Kuzhagaliev', 'Nuraiym Kilybayeva', 'Mariyam Murzagaliyeva', 'Abylay Tabayev']:
            draw.text((1020, y), name, font=font('georgia.ttf', 38), fill=C['ink'])
            y += 89
        draw.line((1020, y + 15, 1785, y + 15), fill=C['teal'], width=3)
        put(draw, 'Source decisions → contained execution → portable evidence', (1020, y + 60), font('segoeui.ttf', 33), 750, C['teal'], 47)
    draw.text((92, 868), 'Fictional data  ·  Edited browser captures  ·  Local synthetic narration', font=font('segoeui.ttf', 22), fill=C['muted'])
    draw.text((1740, 50), f'{index:02} · {count:02}', font=font('segoeui.ttf', 24), fill=C['muted'])
    return img


def build():
    BUILD.mkdir(parents=True, exist_ok=True)
    story = json.loads((VIDEO / 'storyboard.json').read_text(encoding='utf-8'))
    audio_parts, audio_format, timeline, subtitle_items, concat = [], None, [], [], []
    elapsed = 0.0
    for i, scene in enumerate(story['scenes'], 1):
        wav_path = BUILD / 'audio' / f'scene-{i:02}.wav'
        with wave.open(str(wav_path), 'rb') as audio:
            fmt = (audio.getnchannels(), audio.getsampwidth(), audio.getframerate())
            if audio_format is not None and fmt != audio_format:
                raise ValueError('Inconsistent narration format')
            audio_format = fmt
            data = audio.readframes(audio.getnframes())
            spoken = audio.getnframes() / audio.getframerate()
        channels, sample_bytes, rate = fmt
        lead_frames, tail_frames = round(rate * .35), round(rate * .85)
        duration = (lead_frames + len(data) // (channels * sample_bytes) + tail_frames) / rate
        audio_parts.extend([bytes(lead_frames * channels * sample_bytes), data, bytes(tail_frames * channels * sample_bytes)])
        captions = chunks(scene['narration'])
        weights = [len(c.split()) for c in captions]
        base = scene_canvas(scene, i, len(story['scenes']))
        scene_time = 0.0
        for j, (caption, weight) in enumerate(zip(captions, weights), 1):
            span = duration * weight / sum(weights)
            frame = base.copy()
            draw = ImageDraw.Draw(frame)
            draw.rectangle((0, 925, W, H), fill=C['dark'])
            face = font('segoeui.ttf', 33)
            rows = lines(caption, face, 1710)
            if len(rows) > 2:
                raise ValueError('Caption exceeds two lines')
            y = 968 if len(rows) == 1 else 949
            for row in rows:
                draw.text(((W - face.getlength(row)) / 2, y), row, font=face, fill='#FAFCFC')
                y += 46
            draw.rectangle((0, 921, round(W * ((i - 1) + j / len(captions)) / len(story['scenes'])), 925), fill=C['teal'])
            frame_path = BUILD / f'frame-{i:02}-{j:02}.png'
            frame.save(frame_path)
            concat.extend([f"file '{frame_path.as_posix()}'", f'duration {span:.6f}'])
            subtitle_items.append(f'{len(subtitle_items)+1}\n{timecode(elapsed + scene_time)} --> {timecode(elapsed + scene_time + span)}\n{caption}\n')
            scene_time += span
        timeline.append({'scene': i, 'title': scene['title'], 'start_seconds': round(elapsed, 3), 'duration_seconds': round(duration, 3), 'source': scene.get('source'), 'narration': scene['narration']})
        elapsed += duration
    concat.append(concat[-2])
    (BUILD / 'frames.ffconcat').write_text('\n'.join(concat) + '\n', encoding='utf-8')
    (VIDEO / 'prooflane-demo.en.srt').write_text('\n'.join(subtitle_items), encoding='utf-8')
    (VIDEO / 'transcript.en.txt').write_text('\n\n'.join(s['narration'] for s in story['scenes']) + '\n', encoding='utf-8')
    with wave.open(str(BUILD / 'narration.wav'), 'wb') as audio:
        audio.setnchannels(audio_format[0])
        audio.setsampwidth(audio_format[1])
        audio.setframerate(audio_format[2])
        audio.writeframes(b''.join(audio_parts))
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    output = VIDEO / 'prooflane-demo.mp4'
    command = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(BUILD / 'frames.ffconcat'), '-i', str(BUILD / 'narration.wav'), '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p', '-r', '12', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', '-t', f'{elapsed:.6f}', str(output)]
    subprocess.run(command, check=True)
    subprocess.run([ffmpeg, '-hide_banner', '-v', 'error', '-i', str(output), '-f', 'null', '-'], check=True)
    assert output.stat().st_size < 300_000_000 and elapsed < 300
    manifest = {'title': story['title'], 'format': story['format'], 'width': W, 'height': H, 'fps': 12, 'duration_seconds': round(elapsed, 3), 'bytes': output.stat().st_size, 'sha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'voice': story['voice'], 'audio': 'AAC, local Windows synthetic English voice', 'captions': 'Burned-in English captions plus SRT', 'fully_decoded_without_error': True, 'new_model_calls_for_video': 0, 'timeline': timeline, 'ffmpeg': subprocess.check_output([ffmpeg, '-version'], text=True).splitlines()[0]}
    (VIDEO / 'video-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: manifest[k] for k in ['duration_seconds', 'bytes', 'sha256', 'fully_decoded_without_error']}))


if __name__ == '__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    build()
