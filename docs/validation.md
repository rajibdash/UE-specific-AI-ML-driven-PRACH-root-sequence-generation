# Reproducible validation

Run commands from the repository root. Runtime code and tests need only Python
3 and a C++17 compiler; PDF extraction additionally uses Poppler.

## Baseline tests and examples

```sh
python3 -m unittest discover -s tests -v
python3 -m examples.python.reference_demo
g++ -std=c++17 -Wall -Wextra -pedantic -Icpp \
  cpp/prach_reference.cpp examples/cpp/main.cpp \
  -o /tmp/prach_reference
/tmp/prach_reference
```

Expected example output in both languages:

```text
Generated 64 preambles
First preamble: root=1, shift=0
Last preamble: root=1, shift=819
```

The unit suite checks the small ZC root's constant amplitude and periodic
autocorrelation, shift direction, ID/root/shift order, defaults, rejected
inputs, the Python example, and local Markdown link paths. The C++ example is
compiled and run explicitly because the repository has no C++ build/test
framework. It is not a gNB simulation or a test of the paper's receiver.

## Python and C++ equivalence

The two implementations should agree exactly on preamble count, IDs, root
indices, cyclic shifts, sequence length, and sample ordering for identical
valid inputs. To compare complex samples, evaluate the same root and shift in
both implementations and compare each sample by absolute complex error:

$$
|x_{\mathrm{Python}}[n]-x_{\mathrm{C++}}[n]| \le 10^{-12}.
$$

The tolerance allows for insignificant differences in standard-library
`exp`/`sin`/`cos` implementations; do not use exact textual float equality.
Both implementations use double precision. Check sequence metadata before
comparing samples so an ordering error is not hidden by a numerical tolerance.
No PHY performance or standards-conformance inference follows from parity.

## Internal Markdown links

The test `tests/test_markdown_links.py` scans Markdown files for local link
targets. Run it independently with:

```sh
python3 -m unittest discover -s tests -p 'test_markdown_links.py' -v
```

It ignores external URLs and checks target existence (not heading-fragment
spelling).

## Verify the moved PDFs and read the primary source

The moves preserve file bytes. Verify the primary PDF and the two supporting
PDFs with:

```sh
sha256sum \
  references/primary/PRACHPreambleDesignfor6GWirelessSystems_final.pdf \
  references/supporting/2401.12803v1.pdf \
  'references/supporting/6G AI-Driven Air Interface.pdf'
```

Expected SHA-256 values:

```text
7548dfe33f2952d4125e3d979887dde2b0077578a6f86b05fe06af2863ec4205  references/primary/PRACHPreambleDesignfor6GWirelessSystems_final.pdf
0a448a7f8ccd980e2512ea83a88a5360a57566318252d8988f029d3e0e7c678f  references/supporting/2401.12803v1.pdf
c39404bbe6f77744e43c74e979faa5eeff7676d430b76930e0c49f37ce90d618  references/supporting/6G AI-Driven Air Interface.pdf
```

The primary document has six pages. With Poppler installed, extract all pages
in layout-preserving text form for source review:

```sh
pdfinfo references/primary/PRACHPreambleDesignfor6GWirelessSystems_final.pdf \
  | grep '^Pages:'
pdftotext -layout \
  references/primary/PRACHPreambleDesignfor6GWirelessSystems_final.pdf \
  /tmp/prach-primary-paper.txt
```

`pdftotext -layout` is the extraction tool used to inspect the equations and
captions. It is not a project runtime dependency; the page images in the PDF
remain the authority if text extraction obscures a diagram or equation. The
paper summary documents which findings are reported by the paper and which
parts are absent from the implementation.

## Final local checks

```sh
git diff --check
git status --short
```

Do not check in generated binaries, extracted PDF text, caches, or temporary
files. The C++ example above writes its executable under `/tmp`.
