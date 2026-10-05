# Bass Score from Audio

A Codex plugin containing the `bass-score-from-audio` skill. It guides the creation of a bass practice pack from recordings supplied by the user: isolated bass and no-bass audio, bass-clef notation, four-string TAB, MIDI, MusicXML, and a visually checked PDF.

The plugin contains instructions and a validation script. Audio separation, transcription, engraving, and Guitar Pro playback depend on the tools available in the user's environment. Automatic transcription must be checked by ear; it is not guaranteed to be exact.

## Install

The public Codex plugin directory listing requires OpenAI review and publication. Until that process is complete, the source is available in [`plugins/bass-score-from-audio`](plugins/bass-score-from-audio), and the standalone skill is in [`skills/bass-score-from-audio`](plugins/bass-score-from-audio/skills/bass-score-from-audio).

### Claude Code

Claude Code can use the same skill. Copy the entire `plugins/bass-score-from-audio/skills/bass-score-from-audio` directory, including `references/` and `scripts/`, to `~/.claude/skills/bass-score-from-audio/` for use in every local project, or to `<project>/.claude/skills/bass-score-from-audio/` for one project. Then invoke `/bass-score-from-audio` in Claude Code, or ask for a bass practice pack and let Claude load the skill when relevant. The instructions still depend on local audio and notation tools; installing the skill does not install FFmpeg, Demucs, or Guitar Pro.

## Support

Report problems in [GitHub Issues](https://github.com/BenedictCoeiianae/audio-to-bass-score/issues).
