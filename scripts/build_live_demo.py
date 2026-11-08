"""Assemble actual timestamped browser recordings with downloaded ElevenLabs speech.

No browser control or generated video. Raw screen frames remain in the local cache.
The edit manifest records every retained interval and any final-frame padding.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import textwrap

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / '.cache/prooflane-recording-v2/raw'
OUT = ROOT / 'submission/agent-rush/video-v2'
BUILD = ROOT / '.cache/prooflane-recording-v2/render'
FF = ROOT / '.cache/video-python/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'

EDITS = [
    ('The disputed invoice', [('01-intro', 0, 18)]),
    ('Resolve the two sources', [('02b-reconcile', 0, None), ('02c-contract', 0, None), ('02d-exclusion', 0, None)]),
    ('A real Vultr agent run', [('03-execute', 0, 26)]),
    ('Trace a decision to the cent', [('04a-ledger', 0, None), ('04c-priority-readable', 0, None)]),
    ('Inspect the execution', [('05c-provenance-readable', 0, 9), ('05b-code', 0, 7), ('05c-provenance-readable', 9, None)]),
    ('Test containment live', [('06-containment', 0, None)]),
    ('Export and independently verify', [('07a-export', 0, None), ('07b-verify', 0, None)]),
    ('A review another person can reproduce', [('08-close', 0, None)]),
]


def run(args):
    p = subprocess.run([str(FF), '-hide_banner', '-y', *map(str, args)], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr[-5000:])
    return p.stderr


def duration(path):
    p = subprocess.run([str(FF), '-hide_banner', '-i', str(path)], capture_output=True, text=True)
    h, m, s = map(float, re.search(r'Duration: (\d+):(\d+):([\d.]+)', p.stderr).groups())
    return 3600 * h + 60 * m + s


def ass_time(t):
    centis = round(t * 100)
    h, centis = divmod(centis, 360000)
    m, centis = divmod(centis, 6000)
    s, c = divmod(centis, 100)
    return f'{h}:{m:02}:{s:02}.{c:02}'


def srt_time(t):
    millis = round(t * 1000)
    h, millis = divmod(millis, 3600000)
    m, millis = divmod(millis, 60000)
    s, ms = divmod(millis, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def chunks(text):
    result, current = [], []
    for word in text.split():
        current.append(word)
        if len(' '.join(current)) > 83 or (len(current) >= 8 and word.endswith(('.', ';', ':'))):
            result.append(' '.join(current))
            current = []
    if current:
        result.append(' '.join(current))
    return result


ASS_HEADER = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Segoe UI,31,&H00FFFFFF,&H00FFFFFF,&H00243838,&H00243838,0,0,0,0,100,100,0,0,1,0,0,2,90,90,20,1
Style: Chapter,Segoe UI,21,&H00DBEBE9,&H00FFFFFF,&H00243838,&H00243838,0,0,0,0,100,100,0,0,1,0,0,7,38,38,969,1
Style: Note,Segoe UI,21,&H00DBEBE9,&H00FFFFFF,&H00243838,&H00243838,0,0,0,0,100,100,0,0,1,0,0,9,38,38,969,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    script = json.loads((OUT / 'script.json').read_text())
    timeline, srt, global_time, serial = [], [], 0.0, 0
    for i, (title, edits) in enumerate(EDITS):
        chapter = script['chapters'][i]
        frames, intervals, local_time = [], [], 0.0
        for name, start, end in edits:
            folder = RAW / name
            meta = json.loads((folder / 'capture.json').read_text())
            source = meta['frames']
            actual_end = source[-1]['at_ms'] / 1000 + 0.09
            stop = min(end if end is not None else actual_end, actual_end)
            interval_frames = []
            for j, f in enumerate(source):
                at = f['at_ms'] / 1000
                nxt = source[j + 1]['at_ms'] / 1000 if j + 1 < len(source) else actual_end
                left, right = max(start, at), min(stop, nxt)
                if right > left:
                    interval_frames.append((folder / f['file'], right - left))
            frames.extend(interval_frames)
            intervals.append({'clip': name, 'from_seconds': start, 'to_seconds': stop,
                              'source_started_at': meta['started_at'], 'kept_frames': len(interval_frames)})
            local_time += sum(t for _, t in interval_frames)
        audio = OUT / 'audio' / f"{chapter['id']}.mp3"
        audio_duration = duration(audio)
        offset = 0.4 if i != 6 else 4.0
        total = max(local_time, audio_duration + offset + 0.65)
        padding = total - local_time
        if padding:
            frames.append((frames[-1][0], padding))
        concat = BUILD / f'{i:02}.ffconcat'
        with concat.open('w', encoding='utf-8', newline='\n') as file:
            file.write('ffconcat version 1.0\n')
            for path, seconds in frames:
                file.write(f"file '{path.as_posix()}'\nduration {seconds:.6f}\n")
            file.write(f"file '{frames[-1][0].as_posix()}'\n")
        events = [f'Dialogue: 0,0:00:00.00,{ass_time(total)},Chapter,,0,0,0,,{i+1:02}   {title}']
        note = 'Live site recording · fictional inputs'
        if i == 7:
            note = '45.76.92.198 · github.com/NuraliKuzhagaliev/Prooflane · elevenlabs.io'
        events.append(f'Dialogue: 0,0:00:00.00,{ass_time(total)},Note,,0,0,0,,{note}')
        parts = chunks(chapter['text'])
        count = sum(len(c.split()) for c in parts)
        t = offset
        for part in parts:
            length = audio_duration * len(part.split()) / count
            wrapped = r'\N'.join(textwrap.wrap(part, width=105))
            events.append(f'Dialogue: 1,{ass_time(t)},{ass_time(t+length)},Caption,,0,0,0,,{wrapped}')
            serial += 1
            srt.append(f'{serial}\n{srt_time(global_time+t)} --> {srt_time(global_time+t+length)}\n{part}\n')
            t += length
        ass = BUILD / f'{i:02}.ass'
        ass.write_text(ASS_HEADER + '\n'.join(events) + '\n', encoding='utf-8', newline='\n')
        ass_filter = ass.as_posix().replace(':', r'\:')
        vf = ("scale=1920:960:force_original_aspect_ratio=decrease,"
              "pad=1920:1080:(ow-iw)/2:0:color=0x243838,setsar=1,"
              f"subtitles=filename='{ass_filter}'")
        output = BUILD / f'{i:02}.mp4'
        log = run(['-f','concat','-safe','0','-i',concat,'-i',audio,
                   '-vf',vf,'-af',f'adelay={round(offset*1000)}:all=1,loudnorm=I=-16:TP=-1.5:LRA=11,apad',
                   '-t',f'{total:.3f}','-r','30','-c:v','libx264','-preset','fast','-crf','22',
                   '-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000',output])
        (BUILD / f'{i:02}.log').write_text(log, encoding='utf-8')
        timeline.append({'chapter':chapter['id'],'title':title,'starts_seconds':global_time,
                         'duration_seconds':total,'audio_seconds':audio_duration,
                         'audio_offset_seconds':offset,'final_frame_padding_seconds':padding,
                         'intervals':intervals})
        global_time += total
        print(f"Rendered {chapter['id']}: {total:.2f}s", flush=True)
    all_clips = BUILD / 'all.ffconcat'
    all_clips.write_text('ffconcat version 1.0\n' + ''.join(f"file '{(BUILD / f'{i:02}.mp4').as_posix()}'\n" for i in range(8)), encoding='utf-8')
    target = OUT / 'prooflane-live-demo.mp4'
    run(['-f','concat','-safe','0','-i',all_clips,'-c','copy','-movflags','+faststart',
         '-metadata','title=Prooflane live product demo | elevenlabs.io narration',
         '-metadata','comment=Actual Vultr website recording. Free-plan ElevenLabs narration; attribution: elevenlabs.io. Fictional data.',target])
    (OUT / 'prooflane-live-demo.en.srt').write_text('\n'.join(srt), encoding='utf-8', newline='\n')
    manifest={'schema':'prooflane.live-demo-edit.v1','video':target.name,'timeline':timeline,
              'nominal_total_seconds':global_time,'video_bytes':target.stat().st_size,
              'video_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
              'capture_method':'Timestamped native browser JPEG stream, approximately 11 fps; output 30 fps repeats captured frames. No interpolated motion or generated scenes.',
              'edit_scope':'Inspection chapters contain editorial view cuts. Execution and containment retain their request, wait and completion. Only idle time after completed execution is trimmed.',
              'omitted_capture':'02a-upload: native file chooser completed slowly outside the captured interval. Chapter 2 starts with both real selected filenames, then reconciliation.',
              'captions':'Text matches generated narration. Cue timings are proportional estimates, visually reviewed; not forced alignment.',
              'voice':'ElevenLabs George, Eleven Multilingual v2, existing Free-plan credits, no purchase. Separate provider terms; attribution elevenlabs.io.'}
    (OUT / 'edit-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'video':str(target),'seconds':global_time,'bytes':target.stat().st_size}),flush=True)


if __name__ == '__main__':
    main()
