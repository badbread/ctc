# Demo media

`demo.cast` is an [asciinema v2](https://docs.asciinema.org/manual/asciicast/v2/)
recording of the ctc TUI. Frames are built from the real `bin/ctc` rendering
(same glyphs, same 256-color palette, same footer text), so it matches the tool.

## Play it locally

```bash
asciinema play docs/media/demo.cast
```

## Publish (for the README badge)

Upload to asciinema.org and swap the `REPLACE_WITH_ID` placeholders in the
top-level README:

```bash
asciinema upload docs/media/demo.cast
# -> prints a URL like https://asciinema.org/a/123456 ; the id is 123456
```

## Render to a GIF (for inline embedding)

GIF needs [`agg`](https://github.com/asciinema/agg) (the official converter):

```bash
agg --theme asciinema docs/media/demo.cast docs/media/demo.gif
```

Then embed `docs/media/demo.gif` in the README instead of the asciinema badge.

## Regenerate the cast

The cast is generated, not hand-edited — edit the generator and re-run:

```bash
python3 tools/gen_demo_cast.py docs/media/demo.cast
```
