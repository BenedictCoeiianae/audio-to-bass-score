"""Validate a bass practice pack and optionally render score page samples.

Usage: python validate_pack.py PACK_DIR [--preview-dir DIR]
The pack needs a manifest.json containing one object per song. Paths may be
absolute or relative to PACK_DIR. This checks structure, not transcription
accuracy or playback inside Guitar Pro.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import fitz
import mido
from mutagen import File as AudioFile


def resolve(pack: Path, raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else pack / path


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def measure_lengths(xml_path: Path) -> tuple[int, int]:
    root = ET.parse(xml_path).getroot()
    parts = root.findall("part")
    if not parts:
        raise ValueError(f"No parts: {xml_path}")
    total_measures = None
    sounding_notes = 0
    for part in parts:
        measures = part.findall("measure")
        if total_measures is None:
            total_measures = len(measures)
        elif len(measures) != total_measures:
            raise ValueError(f"Part measure count differs: {xml_path}")
        divisions = None
        beats = None
        beat_type = None
        for number, measure in enumerate(measures, 1):
            attributes = measure.find("attributes")
            if attributes is not None:
                divisions_text = attributes.findtext("divisions")
                if divisions_text is not None:
                    divisions = int(divisions_text)
                time = attributes.find("time")
                if time is not None:
                    beats = int(time.findtext("beats"))
                    beat_type = int(time.findtext("beat-type"))
            if not all((divisions, beats, beat_type)):
                raise ValueError(f"Missing meter or divisions in {xml_path}, bar {number}")
            expected = divisions * beats * 4 / beat_type
            cursor = 0
            furthest = 0
            for child in measure:
                if child.tag == "note":
                    if child.find("grace") is not None:
                        continue
                    duration = int(child.findtext("duration", "0"))
                    if child.find("pitch") is not None:
                        sounding_notes += 1
                    if child.find("chord") is None:
                        cursor += duration
                        furthest = max(furthest, cursor)
                elif child.tag == "backup":
                    cursor -= int(child.findtext("duration", "0"))
                elif child.tag == "forward":
                    cursor += int(child.findtext("duration", "0"))
                    furthest = max(furthest, cursor)
            pickup = measure.get("implicit") == "yes" or measure.get("number") in ("0", "X1")
            if furthest != expected and not (pickup and 0 < furthest < expected):
                raise ValueError(f"Bar duration {furthest} != {expected}: {xml_path}, bar {number}")
    if not sounding_notes:
        raise ValueError(f"No pitched notes: {xml_path}")
    return total_measures or 0, sounding_notes


def validate_song(pack: Path, item: dict, preview_dir: Path | None) -> str:
    title = item.get("title", "untitled")
    required = ("pdf", "musicxml", "midi", "events", "bass_audio", "backing_audio")
    files = {}
    for key in required:
        if not item.get(key):
            raise ValueError(f"{title}: missing manifest field {key}")
        path = resolve(pack, item[key])
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"{title}: missing or empty {key}: {path}")
        files[key] = path

    source = item.get("source")
    if source and item.get("source_sha256"):
        source_path = resolve(pack, source)
        if source_path.is_file() and hash_file(source_path) != item["source_sha256"]:
            raise ValueError(f"{title}: source hash changed")

    bars, pitched = measure_lengths(files["musicxml"])
    if item.get("bars") is not None and bars != item["bars"]:
        raise ValueError(f"{title}: bar count changed")
    gp_dir = pack / "guitar_pro_import"
    if gp_dir.is_dir():
        candidates = list(gp_dir.glob(files["musicxml"].stem + "_GP_import.musicxml"))
        if len(candidates) != 1:
            raise ValueError(f"{title}: missing single-track Guitar Pro import file")
        gp_bars, _ = measure_lengths(candidates[0])
        gp_root = ET.parse(candidates[0]).getroot()
        if gp_bars != bars or len(gp_root.findall("part")) != 1:
            raise ValueError(f"{title}: invalid Guitar Pro import part/bar count")
        score_part = gp_root.find("./part-list/score-part")
        if (score_part is None or score_part.find("score-instrument") is None
                or score_part.findtext("./midi-instrument/midi-program") is None):
            raise ValueError(f"{title}: Guitar Pro import lacks instrument metadata")
        if gp_root.find("./part/measure/direction/sound") is None:
            raise ValueError(f"{title}: Guitar Pro import lacks tempo metadata")

    midi = mido.MidiFile(files["midi"])
    note_ons = sum(msg.type == "note_on" and msg.velocity > 0 for track in midi.tracks for msg in track)
    if note_ons == 0:
        raise ValueError(f"{title}: MIDI has no notes")
    with files["events"].open(encoding="utf-8-sig", newline="") as stream:
        event_count = sum(1 for _ in csv.DictReader(stream))
    if event_count == 0:
        raise ValueError(f"{title}: CSV has no events")

    expected_duration = item.get("duration")
    for key in ("bass_audio", "backing_audio"):
        audio = AudioFile(files[key])
        if audio is None or audio.info.length <= 0:
            raise ValueError(f"{title}: unreadable audio: {files[key]}")
        if expected_duration and abs(audio.info.length - expected_duration) > 2:
            raise ValueError(f"{title}: {key} duration differs by over two seconds")

    pdf = fitz.open(files["pdf"])
    if len(pdf) == 0:
        raise ValueError(f"{title}: empty PDF")
    if item.get("pages") is not None and len(pdf) != item["pages"]:
        raise ValueError(f"{title}: PDF page count changed")
    pages = sorted({0, len(pdf) // 2, len(pdf) - 1})
    for index in pages:
        page = pdf[index]
        if abs(page.rect.width - 595) > 2 or abs(page.rect.height - 842) > 2:
            raise ValueError(f"{title}: page {index + 1} is not A4 portrait")
        if preview_dir is not None:
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            pix.save(preview_dir / f"{item.get('number', 'song')}_{index + 1:03d}.png")
    return f"{title}: {bars} bars, {len(pdf)} PDF pages, {pitched} XML pitched notes, {note_ons} MIDI note-ons"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", type=Path)
    parser.add_argument("--preview-dir", type=Path)
    args = parser.parse_args()
    pack = args.pack.resolve()
    items = json.loads((pack / "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(items, list) or not items:
        raise ValueError("Manifest must contain a nonempty song list")
    preview_dir = args.preview_dir.resolve() if args.preview_dir else None
    if preview_dir:
        preview_dir.mkdir(parents=True, exist_ok=True)
    for item in items:
        print(validate_song(pack, item, preview_dir))
    print(f"Validated {len(items)} song(s). Visual and listening review still required.")


if __name__ == "__main__":
    main()
