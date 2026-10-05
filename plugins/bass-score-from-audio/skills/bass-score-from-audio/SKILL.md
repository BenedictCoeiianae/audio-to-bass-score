---
name: bass-score-from-audio
description: Turn user-provided songs into a practice pack with isolated bass and no-bass audio, rhythm-bearing bass-clef notation, four-string TAB, MIDI, MusicXML, and a visually checked PDF. Use for bass transcription from recordings or for revising such a pack; do not use for unrelated audio editing.
---

# Bass score from audio

Create a usable bass practice pack from the user's recordings. Preserve the original audio. Match a supplied score sample when there is one; otherwise use readable bass-clef staff above four-line TAB, with visible staff and ledger lines, note values, beams, rests, ties, bar numbers, title, tuning, and tempo.

Read [references/workflow.md](references/workflow.md) before processing audio or changing score files. It contains the specific analysis, engraving, Guitar Pro, and verification choices learned from the O-Hum work. Treat its parameters as starting points, not claims that every song is 4/4 or that an automatic transcription is exact.

## Decisions that matter

- Inventory the **current** input files and confirm which ones the user wants included. Reuse a previous bass separation only after verifying that the decoded source audio is identical. Preserve source files and unrelated outputs. Delete or replace earlier deliverables only when the user asks.
- Separate bass and no-bass audio, then estimate pitches and onsets from the bass stem. Determine tempo, meter, beat phase, note values, rests, and ties from evidence in the recording. Mark uncertainty; do not turn a tentative beat grid or fingering into a claim of exact transcription.
- Produce standard notation and TAB with **the same note and duration sequence**. For standard four-string bass, E1/A1/D2/G2 are MIDI 28/33/38/43; the bass-clef staff is conventionally written one octave above sounding pitch. Confirm tuning from the recording or user before applying that default. Keep string/fret indications on TAB only; do not show circled string numbers or their continuation lines above standard notation.
- Keep an editable master score, a PDF for reading, a MIDI for listening, isolated-bass and no-bass audio, and a machine-readable note-event record. For Guitar Pro, the import file **must show both bass-clef five-line notation and four-line TAB** in one track. Make a single-part, two-staff MusicXML with numbered clefs and `<staff-type>alternate</staff-type>` for TAB, plus tuning, electric-bass instrument metadata, tempo, and matching note durations. Put `<technical><string>` and `<fret>` on TAB notes only, not on five-line staff notes, so Guitar Pro does not add circled string numbers and extension lines above the staff. A two-part staff-plus-TAB file can import as two tracks; a TAB-clef-only single part shows no five-line staff. Do not claim the result is a native `.gp` file.
- Render every final PDF and inspect at least the first, middle, and last page of **each** song. Verify staff and TAB lines remain visible, there is no clipping, note values are readable, and pages are consistent. For the Guitar Pro import file, verify one part, two numbered clefs, TAB as alternate staff, both note and fret content on an engraved preview, equal bar durations, and no circled string numbers above the five-line staff. Check actual Guitar Pro import and playback when the application is available; imported tempo or sound presets may differ from MusicXML metadata. Use `scripts/validate_pack.py` for structural checks when producing a manifest in the documented shape.
- Describe automatic transcription as a draft until its pitches and rhythms have been checked by ear against the isolated bass. State clearly what was and was not manually corrected.

## Output and handoff

Name files by track number and song title. Keep per-song PDF, editable MusicXML, Guitar Pro import MusicXML, MIDI, event CSV, bass-only audio, and no-bass backing together in one practice-pack directory; add a concise manifest and usage note. Give direct links to the pack and representative files. Report any failed validation or application-specific playback issue rather than hiding it.

If Guitar Pro shows notes but plays silently, inspect track mute/volume, its selected RSE or MIDI sound, audio-output preferences, and the application's log. A missing soundbank or output device cannot be repaired just by changing note data. Refer to the official Guitar Pro support instructions linked in [references/workflow.md](references/workflow.md) for the user's version.
