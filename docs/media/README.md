# Demo media

The README embeds [`demo.gif`](demo.gif) inline. It's rendered from
[`demo.cast`](demo.cast), an [asciinema v2](https://docs.asciinema.org/manual/asciicast/v2/)
recording. The cast itself is generated from [`../../tools/gen_demo_cast.py`](../../tools/gen_demo_cast.py),
hand-built from the real `bin/ctc` rendering (same glyphs, same 256-color
palette, same footer text) so the demo matches the tool.

## Regenerate

The cast is generated, not hand-edited — edit the generator and re-run:

```bash
python3 tools/gen_demo_cast.py docs/media/demo.cast
```

## Re-render the GIF

Needs [`agg`](https://github.com/asciinema/agg) (the asciinema GIF
converter):

```bash
agg --theme asciinema docs/media/demo.cast docs/media/demo.gif
```

## Optionally publish to asciinema.org

The README embeds the GIF, but the cast is also viewable interactively on
[asciinema.org](https://asciinema.org) if you want a clickable secondary
link:

```bash
asciinema upload docs/media/demo.cast
```

## Play locally

```bash
asciinema play docs/media/demo.cast
```
