# Zhaomin Wu CV LaTeX Source

This directory contains the LaTeX template for `../pdf/ZhaominWu.pdf`.

The editable content lives in the semantic sources under
[`../../_data/content/`](../../_data/content/): `profile.yml`, `site.yml`, the
independent `cv/*.yml` files, `service/*.yml`, `teaching.yml`, `mentoring.yml`,
`talks.yml`, and one BibTeX file per publication
under `publications/`. `make` validates those sources and generates
`generated/*.tex` before compiling the PDF.

Build from this directory:

```bash
make
```

Rebuild automatically whenever a LaTeX source file changes:

```bash
make watch
```

Validate content without writing outputs:

```bash
make validate
```

Do not edit `generated/` manually. The PDF only inputs files from `generated/`.

The original uploaded archive is preserved under `archive/`.
