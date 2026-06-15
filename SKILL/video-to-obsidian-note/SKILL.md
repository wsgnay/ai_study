---
name: video-to-obsidian-note
description: Create illustrated Obsidian learning notes from video links or local video files. Use when the user asks to summarize, organize, transcribe, study, make notes from, or convert a video into a Markdown/Obsidian note, especially with screenshots, keyframes, chapter structure, examples, source metadata, or maintainable vault attachments. Supports workflows for Bilibili, YouTube-like pages, generic webpages, and local videos, with fallbacks when subtitles are unavailable.
---

# Video to Obsidian Note

## Goal

Turn a video source into a maintainable Obsidian note with source metadata, chapter outline, structured learning content, examples, and relevant local images. Prefer faithful coverage over a short summary.

## Workflow

1. Identify the vault root and target note location. If the user is already in an Obsidian workspace, create the note there.
2. Collect source metadata: URL, title, author/uploader, publish date, duration, description, cover image, chapter list, and transcript/subtitle availability.
3. Prefer official or page-provided subtitles/transcripts. If unavailable, use platform chapter data, visible frames, description, and optionally local audio/video transcription if tools are available.
4. Download or capture visual assets into an ASCII-safe attachment folder such as `assets/<slug>/`. Avoid Chinese or punctuation-heavy attachment directory names because local media tools may fail on those paths.
5. Extract or select key images that explain the content, not decorative transition frames. Use contact sheets when reviewing many candidates.
6. Write an Obsidian Markdown note with frontmatter, source link, chapter timeline, concept explanations, examples from the video, diagrams when useful, and a concise takeaway section.
7. Verify every local image link exists. Remove temporary downloads, scan frames, raw video files, and scrape caches unless the user asks to keep them.

## Source Collection

For Bilibili:

- Use `https://api.bilibili.com/x/web-interface/view?bvid=<BV>` for metadata, `aid`, `cid`, cover, pages, season entries, and subtitle list.
- Use `https://api.bilibili.com/x/player/v2?aid=<aid>&cid=<cid>` for chapters/view points and subtitle metadata.
- Use `https://api.bilibili.com/x/player/playurl?bvid=<BV>&cid=<cid>&qn=16&fnval=0` only when local keyframe extraction is needed and the user request justifies it.
- Set `User-Agent` and `Referer` headers for Bilibili API and asset requests.

For generic webpages:

- Use available scraping/search tools for metadata and transcript text.
- If the page exposes only a shell, inspect page JSON, captions endpoints, OpenGraph metadata, and embedded player data.

For local videos:

- Use the local filename as the source unless the user provides a URL.
- Extract keyframes directly from the local file.

## Visual Assets

Use images when they carry information: outlines, diagrams, examples, equations, UI states, tables, or process flows.

Recommended attachment layout:

```text
assets/<video-slug>/
  cover.jpg
  01-outline.jpg
  02-example.jpg
  03-process.jpg
```

Use `scripts/extract_keyframes.py` for repeatable frame extraction:

```bash
python <skill-dir>/scripts/extract_keyframes.py video.mp4 assets/my-video --times 45,125,215 --contact-sheet
python <skill-dir>/scripts/extract_keyframes.py video.mp4 assets/my-video --interval 30 --max-frames 40 --contact-sheet
```

After reviewing the contact sheet, keep only final images and rename them semantically. Delete raw `frame-*`, scan directories, contact sheets, and downloaded videos unless useful for later maintenance.

## Note Structure

Use this default structure unless the user asks otherwise:

```markdown
---
title: ...
source: ...
author: ...
created: YYYY-MM-DD
tags:
  - ...
---

# Title

![[assets/<slug>/cover.jpg]]

> One-paragraph source summary.

## Outline

| Time Range | Topic |
|---|---|

## Core Concepts

## Detailed Notes

## Examples From The Video

## Practical Notes

## Key Takeaways

## Next Study Steps
```

Keep the note useful as a study artifact:

- Explain concepts in the user's language.
- Include concrete examples from the video.
- Preserve source timestamps when available.
- Use Mermaid for clean process diagrams when screenshots alone are not enough.
- Avoid claiming a transcript exists when the note is reconstructed from chapters/keyframes.
- Localize headings to the user's language in the final note.

## Quality Checks

Run the link checker before finishing:

```bash
python <skill-dir>/scripts/check_obsidian_links.py note.md --vault-root <vault-root>
```

Also check:

- The note is valid UTF-8.
- Image embeds use Obsidian-friendly paths like `![[assets/<slug>/01-image.jpg]]`.
- All final images are informative and readable.
- Temporary files and scraping caches are removed.
- If subtitles were unavailable, mention that the note is not a verbatim transcript.
