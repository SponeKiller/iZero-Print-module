"""
Visual check of a printed PDF against the approved images of its pages.

Every visual test file prints one PDF. Its pages are rendered to PNG and
compared pixel by pixel with the approved images, which are named after
the test file:

    images/<platform>/<test file>.png              one page
    images/<platform>/<test file>_page_<n>.png     more pages

Fonts are rasterized differently on every operating system, so each
platform (`win32`, `linux`, ...) has its own folder of images.

Approving the current look: run the visual tests with `UPDATE_VISUAL=1`,
look at the written images and commit them.

When the PDF differs, the test fails and writes the rendered pages and
masks of the changed pixels to `failed/<platform>/` next to `images/`.
"""
import os
import sys
from pathlib import Path

import pypdfium2
from PIL import Image, ImageChops

# Pixels per PDF point (72 per inch): 1.5 = 108 DPI
SCALE = 1.5
# A pixel counts as changed when one of its channels differs by more
# than this (ignores antialiasing noise)
PIXEL_TOLERANCE = 32
# The page fails when more pixels than this changed. Rendering on one
# platform is exact (0 changed pixels), one changed digit is ~60 pixels.
MAX_CHANGED_PIXELS = 10


def assert_pdf_looks_like(pdf: bytes, test_file: str) -> None:
    """
    Fail unless every page of the PDF looks like its approved image.

    Args:
        pdf: Content of the printed PDF
        test_file: Path of the visual test file (`__file__`), which names
         the images
    """
    folder = Path(test_file).parent
    name = Path(test_file).stem
    images = folder / "images" / sys.platform
    failed = folder / "failed" / sys.platform

    pages = _render(pdf)
    names = (
        [f"{name}.png"]
        if len(pages) == 1
        else [f"{name}_page_{number}.png" for number in range(1, len(pages) + 1)]
    )
    approved = sorted(
        path.name
        for pattern in (f"{name}.png", f"{name}_page_*.png")
        for path in images.glob(pattern)
    )

    if os.environ.get("UPDATE_VISUAL") == "1":
        images.mkdir(parents=True, exist_ok=True)
        for old in approved:
            (images / old).unlink()
        for image, page in zip(names, pages):
            page.save(images / image)
        return

    assert approved, (
        f"No approved images of '{name}' in {images}. "
        "Run the visual tests with UPDATE_VISUAL=1 and commit the images."
    )
    assert sorted(names) == approved, (
        f"'{name}' has {len(pages)} pages, approved images: {approved}"
    )

    problems = []
    for image, page in zip(names, pages):
        expected = Image.open(images / image).convert("RGB")

        if expected.size != page.size:
            problems.append(
                f"{image}: size {page.size}, approved {expected.size}"
            )
            continue

        mask = (
            ImageChops.difference(expected, page)
            .convert("L")
            .point(lambda value: 255 if value > PIXEL_TOLERANCE else 0)
        )
        changed = mask.histogram()[255]
        if changed > MAX_CHANGED_PIXELS:
            failed.mkdir(parents=True, exist_ok=True)
            page.save(failed / image)
            mask.save(failed / image.replace(".png", ".diff.png"))
            problems.append(f"{image}: {changed} pixels changed")

    assert not problems, (
        f"'{name}' does not look like the approved images "
        f"(rendered pages and diffs in {failed}): " + "; ".join(problems)
    )


def _render(pdf: bytes) -> list[Image.Image]:
    document = pypdfium2.PdfDocument(pdf)
    try:
        return [
            page.render(scale=SCALE).to_pil().convert("RGB")
            for page in document
        ]
    finally:
        document.close()
