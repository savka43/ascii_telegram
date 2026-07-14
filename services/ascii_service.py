from dataclasses import dataclass
from io import BytesIO

from PIL import Image, ImageDraw

from utils.fonts import load_monospace_font


@dataclass(frozen=True)
class AsciiResult:
    text: str
    lines: list[str]
    width: int
    mode: str
    colors: list[list[str]] | None = None


class AsciiService:
    def convert(self, image: Image.Image, mode: str, width: int) -> AsciiResult:
        result = self._convert_with_ascii_art_converter(image, mode=mode, width=width)
        return AsciiResult(
            text=result.text,
            lines=result.lines,
            width=width,
            mode=mode,
            colors=result.colors,
        )

    def render_png(self, result: AsciiResult) -> bytes:
        font = load_monospace_font(size=14)
        probe = Image.new("RGB", (1, 1))
        draw = ImageDraw.Draw(probe)
        bbox = draw.textbbox((0, 0), "M", font=font)
        char_width = max(1, bbox[2] - bbox[0])
        line_height = max(1, bbox[3] - bbox[1] + 4)

        padding = 16
        image_width = max(1, max((len(line) for line in result.lines), default=1) * char_width)
        image_height = max(1, len(result.lines) * line_height)
        canvas = Image.new(
            "RGB",
            (image_width + padding * 2, image_height + padding * 2),
            color=(12, 12, 12),
        )
        draw = ImageDraw.Draw(canvas)

        for y, line in enumerate(result.lines):
            for x, char in enumerate(line):
                fill = "#f2f2f2"
                if result.colors and y < len(result.colors) and x < len(result.colors[y]):
                    fill = result.colors[y][x]
                draw.text(
                    (padding + x * char_width, padding + y * line_height),
                    char,
                    font=font,
                    fill=fill,
                )

        output = BytesIO()
        canvas.save(output, format="PNG")
        return output.getvalue()

    def render_txt(self, result: AsciiResult) -> bytes:
        return result.text.encode("utf-8")

    def _convert_with_ascii_art_converter(self, image: Image.Image, mode: str, width: int):
        from ascii_art_converter.config import AsciiArtConfig
        from ascii_art_converter.constants import RenderMode
        from ascii_art_converter.generator import AsciiArtGenerator

        config = AsciiArtConfig(
            width=width,
            mode=RenderMode.DENSITY,
            char_aspect_ratio=0.45,
            colorize=mode == "color",
            color_depth=24,
            contrast=1.1,
        )
        generator = AsciiArtGenerator()
        return generator.convert(image, config)
