from pathlib import Path

import pypdfium2
from PIL import Image, ImageChops

from tests.visual.config import MAX_GRAY_DIFFERENCE, SCALE


def assert_pdf_looks_like(pdf: bytes, test_file: str) -> None:
    """
    Fail unless every page of the PDF looks like its approved image.

    Pages are compared in gray scale; a page fails when a single pixel
    differs by more than `MAX_GRAY_DIFFERENCE`.

    Args:
        pdf: Content of the printed PDF
        test_file: Path of the visual test file (`__file__`), which names
         the images
    """
    folder = Path(test_file).parent
    name = Path(test_file).stem
    images = folder / "images"

    pages: list[Image.Image] = []
    pdf_page: pypdfium2.PdfPage
    for pdf_page in pypdfium2.PdfDocument(pdf):
        bitmap: pypdfium2.PdfBitmap = pdf_page.render(scale=SCALE)
        rendered: Image.Image = bitmap.to_pil()
        pages.append(rendered.convert("L"))

    names = (
        [f"{name}.png"]
        if len(pages) == 1
        else [f"{name}_page_{number}.png" for number in range(1, len(pages) + 1)]
    )
    approved = {
        path.name
        for pattern in (f"{name}.png", f"{name}_page_*.png")
        for path in images.glob(pattern)
    }

    problems = [
        f"{image}: PDF has no such page"
        for image in sorted(approved - set(names))
    ]
    for image, page in zip(names, pages):
        if image not in approved:
            problems.append(f"{image}: not among approved images")
            continue

        expected = Image.open(images / image).convert("L")

        if expected.size != page.size:
            problems.append(
                f"{image}: size {page.size}, approved {expected.size}"
            )
            continue

        difference = ImageChops.difference(expected, page)
        largest = difference.getextrema()[1]
        if largest > MAX_GRAY_DIFFERENCE:
            left, top, right, bottom = difference.point(
                lambda value: 255 if value > MAX_GRAY_DIFFERENCE else 0
            ).getbbox()
            problems.append(
                f"{image}: pixels differ by up to {largest} in the area "
                f"x {left}-{right}, y {top}-{bottom} px"
            )

    assert not problems, (
        f"'{name}' does not look like the approved images in {images}: "
        + "; ".join(problems)
    )
