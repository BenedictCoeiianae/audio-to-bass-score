# Audio-to-bass-score workflow

This reference documents an audio-to-bass-score workflow as a reusable starting point. Inspect the current recordings and any score samples supplied by the user; do not assume a fixed artist, input directory, output directory, or reference collection.

## Tools and portability

The original implementation used FFmpeg, Demucs, Python with librosa/NumPy/SciPy/SoundFile for analysis, MusicXML and MIDI writers, Verovio for engraving, and PyMuPDF for PDF rendering. The bundled validator needs `PyMuPDF`, `mido`, and `mutagen`. Check availability and install compatible versions only when the current task needs them. Guitar Pro is optional for file creation but required to test its import and playback behavior. This skill contains instructions and a validator, not copyrighted source recordings, soundbanks, Guitar Pro, or a guaranteed one-command transcription engine.

## 1. Input and separation

1. Inventory requested source audio; record name, byte size, duration, and a source hash. Decode to a consistent WAV (`ffmpeg -ar 44100 -ac 2 -sample_fmt s16`). Keep the original unchanged.
2. Run Demucs with an available bass-capable model. The O-Hum run used `python -m demucs -n htdemucs --two-stems bass --out OUTPUT/STEMS INPUT.wav`, yielding `bass.wav` and `no_bass.wav`. Model output is imperfect: listen for kick, guitar, or vocal bleed and for bass notes lost in the backing.
3. Reuse a previous stem only when the decoded source WAV matches byte-for-byte or by SHA-256, not merely by filename. Encode both stems to user-friendly practice audio; the O-Hum run used 192-kbps MP3.

## 2. Note and beat analysis

The O-Hum draft combined a harmonic-spectrum pitch estimate with `librosa.yin` on the bass stem. Energy thresholding removed quiet regions; onset detection split repeated plucks; short unstable events were filtered; a duration-weighted heuristic corrected some octave-high readings caused by strong second harmonics. Save the unquantized onsets, offsets, MIDI pitches, and confidence to a CSV before engraving.

Estimate BPM, beat positions, beat phase, and meter from the source and bass stem. The O-Hum run used `librosa.beat.beat_track` and placed events on a sixteenth-note grid. It assumed 4/4 throughout; this was an approximation, **not** a verified property of every song. If beat tracking drifts or meter changes, correct the grid before generating durations. Audit phrase boundaries and bars against audio. Preserve separate events for repeated notes even when they have the same pitch.

Represent a long event with a duration and, when it crosses a beat or bar, appropriate ties. Insert rests where there is no active bass note. Check that each bar sums to its meter. Assign a feasible string and fret for the chosen tuning; the O-Hum E-A-D-G draft tried frets 0–16 and favored lower positions. Fingering is a suggestion, not proof of the performer's technique.

## 3. Score and files

- Write a MusicXML master with explicit divisions, time, clef, pitch, duration, type, ties, grouped beams, TAB `staff-tuning`, technical string/fret, and score-instrument plus midi-instrument metadata. The O-Hum MIDI voice used General MIDI Electric Bass (finger), program 34 in MusicXML's 1-based numbering.
- Staff notation for electric bass normally displays notes an octave above their sounding pitch; the TAB uses the sounding octave. Check the entire score for octave mismatches.
- The accepted visual layout places bass-clef notation above four-line TAB, without duplicate TAB rhythm stems, and shows title, artist, tuning, tempo, bar numbers, rests, beams, and ties. Do not force every song into the same number of bars per system if readability suffers.
- The O-Hum PDF path was MusicXML → Verovio SVG → PyMuPDF PDF. Verovio staff and ledger lines were initially invisible after SVG conversion; explicitly stroking line paths before conversion fixed that. Render a page preview and inspect the actual five staff lines rather than trusting XML validity.
- Produce MIDI from the note events for listening, not as the only editable score. Produce a single-track Guitar Pro import MusicXML in addition to any two-staff master; Guitar Pro can import a two-part master as two tracks. On the single-track import, retain sounding bass pitches, four-string TAB tuning, note durations, tempo, and electric-bass instrument metadata. In Guitar Pro, users can enable both standard notation and TAB for one track.
- Do not promise Guitar Pro will honor tempo or RSE sound metadata on import. In the O-Hum case, it displayed 120 BPM despite an estimated tempo being written in MusicXML. Its local log also reported `Core::findSoundbankSet : id not found : Pre-Bass`; that is an application soundbank issue, separate from whether the XML contains notes.

## 4. Verification and handoff

Use `../scripts/validate_pack.py PACK_DIRECTORY` for structural checks if the output includes an O-Hum-style `manifest.json`. It checks source identity when available, event and MIDI presence, XML meter sums, PDF dimensions and page counts, and audio durations. Add `--previews` to render first/middle/last page images for visual inspection. The script cannot judge musical accuracy or whether Guitar Pro actually sounds.

Listen to representative passages of the separated bass and compare pitch and onset with the score, especially opening, fills, quiet sections, and ending. Record whether the transcription was algorithmic only or manually corrected. Compare the PDF to the user's reference at normal reading scale. Open a Guitar Pro import in the actual app if accessible and test sound, track count, tuning, and tempo. If silent, check track mute/volume, RSE or MIDI selection, output device, and soundbank installation before altering the score again.

Official Guitar Pro references: [MusicXML import](https://www.guitar-pro.com/docs/gp8/import-export/import/import-musicxml-powertab-tabledit), [track sound](https://www.guitar-pro.com/docs/gp8/audio/soundsetup/sound-settings), [audio/MIDI preferences](https://www.guitar-pro.com/docs/gp8/preferences-stylesheet/preferences/audio-midi), [no-sound troubleshooting](https://support.guitar-pro.com/hc/en-us/articles/19088288716957-GP8-No-sound-during-playback-with-Guitar-Pro-8).
