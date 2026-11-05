#!/usr/bin/env python3
"""Build one myradio episode: spec JSON -> VOICEVOX synthesis -> episode JSON + mp3.

Usage: build_episode.py <spec.json>
Spec: {"date": "YYYY-MM-DD", "title": "...", "opening": [{say,show}...],
       "news": [{"label","points","url","link","lines":[{say,show}...]}...],
       "closing": [{say,show}...], "highlight": 0}
Engine must be running at 127.0.0.1:50021 (VOICEVOX, speaker 14 = 冥鳴ひまり ノーマル).
"""
import json, subprocess, sys, wave, io, os, urllib.request, urllib.parse, datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = "http://127.0.0.1:50021"
SPEAKER = 14
HEAD_SILENCE = 0.6
LINE_GAP = 0.25
SEG_GAP = 0.55

VOICE = {}  # optional style: {"speed": 1.05, "pitch": 0.0, "intonation": 1.4}

def synth(text):
    q = urllib.parse.urlencode({"text": text, "speaker": SPEAKER})
    req = urllib.request.Request(f"{ENGINE}/audio_query?{q}", method="POST")
    query = urllib.request.urlopen(req).read()
    if VOICE:
        qj = json.loads(query)
        if "speed" in VOICE: qj["speedScale"] = VOICE["speed"]
        if "pitch" in VOICE: qj["pitchScale"] = VOICE["pitch"]
        if "intonation" in VOICE: qj["intonationScale"] = VOICE["intonation"]
        query = json.dumps(qj).encode()
    req2 = urllib.request.Request(
        f"{ENGINE}/synthesis?speaker={SPEAKER}",
        data=query, headers={"Content-Type": "application/json"}, method="POST")
    return urllib.request.urlopen(req2).read()

def wav_seconds(b):
    with wave.open(io.BytesIO(b)) as w:
        return w.getnframes() / w.getframerate()

def silence_wav(seconds, ref):
    with wave.open(io.BytesIO(ref)) as w:
        params = w.getparams()
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setparams(params)
        w.writeframes(b"\x00" * int(params.framerate * seconds) * params.sampwidth * params.nchannels)
    return buf.getvalue()

def main():
    spec = json.load(open(sys.argv[1]))
    if "voice" in spec:
        VOICE.update(spec["voice"])
    date = spec["date"]
    # Flatten lines in playback order, tracking segment membership.
    sequence = []  # (part_index, kind, news_index, line)
    part = 0
    for ln in spec["opening"]:
        sequence.append((part, "opening", None, ln))
    part += 1
    for i, item in enumerate(spec["news"]):
        for ln in item["lines"]:
            sequence.append((part, "news", i, ln))
        part += 1
    for ln in spec["closing"]:
        sequence.append((part, "closing", None, ln))

    wavs, durations = [], []
    for _, _, _, ln in sequence:
        b = synth(ln["say"])
        wavs.append(b)
        durations.append(wav_seconds(b))

    # Timing walk.
    lines_timed, segments = [], []
    t = HEAD_SILENCE
    cur_part, seg_start = None, None
    prev_part = None
    for (p, kind, nidx, ln), dur in zip(sequence, durations):
        if prev_part is not None and p != prev_part:
            t += SEG_GAP
        if p != cur_part:
            if cur_part is not None:
                pk, pi = seg_kind[cur_part]
                segments.append({"kind": pk, "index": pi, "start": round(seg_start, 3), "end": round(t, 3)})
            cur_part, seg_start = p, t
        start = t
        t += dur
        lines_timed.append({"start": round(start, 3), "end": round(t, 3), "show": ln["show"], "part": p})
        t += LINE_GAP
    total = t - LINE_GAP
    pk, pi = seg_kind[cur_part]
    segments.append({"kind": pk, "index": pi, "start": round(seg_start, 3), "end": round(total, 3)})

    # Concatenate audio: head silence + wavs with gaps mirroring the timing walk.
    pieces = [silence_wav(HEAD_SILENCE, wavs[0])]
    prev_part = None
    for (p, _, _, _), b in zip(sequence, wavs):
        if prev_part is not None:
            pieces.append(silence_wav(SEG_GAP if p != prev_part else 0, b) if p != prev_part else silence_wav(LINE_GAP, b))
        pieces.append(b)
        prev_part = p
    tmp = os.path.join(BASE, "audio", f".tmp-{date}")
    os.makedirs(tmp, exist_ok=True)
    names = []
    for i, b in enumerate(pieces):
        fn = os.path.join(tmp, f"{i:03d}.wav")
        open(fn, "wb").write(b)
        names.append(fn)
    listf = os.path.join(tmp, "list.txt")
    open(listf, "w").write("".join(f"file '{n}'\n" for n in names))
    mp3 = os.path.join(BASE, "audio", f"{date}-ja.mp3")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", listf, "-codec:a", "libmp3lame", "-q:a", "4", mp3], check=True)
    subprocess.run(["rm", "-rf", tmp])

    ep = {
        "format": "monoradio/news-1",
        "date": date,
        "lang": "ja",
        "title": spec["title"],
        "opening": spec["opening"],
        "news": [{k: item[k] for k in ("label", "points", "lines", "url", "link") if k in item}
                 for item in spec["news"]],
        "closing": spec["closing"],
        "seconds": round(total, 2),
        "lines_timed": lines_timed,
        "segments": segments,
        "made_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    if "highlight" in spec:
        ep["highlight"] = spec["highlight"]
    ep_path = os.path.join(BASE, "episodes", f"{date}-ja.json")
    json.dump(ep, open(ep_path, "w"), ensure_ascii=False, indent=1)

    idx_path = os.path.join(BASE, "episodes.json")
    idx = json.load(open(idx_path))
    idx = [e for e in idx if e["date"] != date]
    idx.insert(0, {"date": date, "ja": {"title": spec["title"], "seconds": round(total, 2)}})
    idx.sort(key=lambda e: e["date"], reverse=True)
    json.dump(idx, open(idx_path, "w"), ensure_ascii=False, indent=1)
    print(f"OK {date}: {total:.1f}s, {len(lines_timed)} lines -> {ep_path}, {mp3}")

# segment kind/index lookup, built in main via closure order
seg_kind = {}
_orig_main = main
def main_wrapped():
    spec = json.load(open(sys.argv[1]))
    p = 0
    seg_kind[p] = ("opening", None); p += 1
    for i in range(len(spec["news"])):
        seg_kind[p] = ("news", i); p += 1
    seg_kind[p] = ("closing", None)
    _orig_main()
main = main_wrapped

if __name__ == "__main__":
    main()
