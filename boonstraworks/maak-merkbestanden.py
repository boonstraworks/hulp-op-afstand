"""Maakt de iconen en het logo van BoonstraWorks Hulp op afstand.

Bron: merk/bron/beeldmerk-512.png (beeldmerk) en merk/bron/logo-website.png
(woordmerk van boonstraworks.nl). De uitvoer staat in merk/ en wordt
meegecommit, zodat de bouw in GitHub Actions geen beeldbewerking nodig heeft.

Opnieuw maken: uv run --with pillow python boonstraworks/maak-merkbestanden.py
"""

import base64
import io
from pathlib import Path

from PIL import Image

MAP = Path(__file__).resolve().parent / "merk"
BRON = MAP / "bron"
TEKSTKLEUR = (26, 29, 41)

ICO_MATEN = [16, 20, 24, 32, 40, 48, 64, 96, 128, 256]


def vierkant_beeldmerk() -> Image.Image:
    """Beeldmerk zonder de lege rand, op een vierkant met 4% marge."""
    beeld = Image.open(BRON / "beeldmerk-512.png").convert("RGBA")
    beeld = beeld.crop(beeld.getbbox())
    zijde = round(max(beeld.size) * 1.08)
    vlak = Image.new("RGBA", (zijde, zijde), (0, 0, 0, 0))
    vlak.paste(beeld, ((zijde - beeld.width) // 2, (zijde - beeld.height) // 2), beeld)
    return vlak


def woordmerk() -> Image.Image:
    """De regel 'Boonstra Works' uit het websitelogo, wit wordt doorzichtig."""
    logo = Image.open(BRON / "logo-website.png").convert("L")
    breedte, hoogte = logo.size
    # Rijen in de onderste helft met donkere pixels, gegroepeerd in aaneengesloten banden.
    # De hoogste band onder het beeldmerk is de naam (de ondertitel is lager).
    rijen = [y for y in range(hoogte // 2, hoogte)
             if any(logo.getpixel((x, y)) < 128 for x in range(0, breedte, 2))]
    banden = []
    for y in rijen:
        if banden and y == banden[-1][1] + 1:
            banden[-1][1] = y
        else:
            banden.append([y, y])
    banden = [b for b in banden if b[0] > hoogte * 0.66]
    boven, onder = max(banden, key=lambda b: b[1] - b[0])
    band = logo.crop((0, boven, breedte, onder + 1))
    # Donkerste tekstpixels (rond 30) volledig dekkend, wit volledig doorzichtig.
    alfa = band.point(lambda v: 0 if v > 240 else min(255, round((255 - v) * 255 / 215)))
    band = Image.new("RGBA", band.size, TEKSTKLEUR + (0,))
    band.putalpha(alfa)
    return band.crop(band.getbbox())


def liggend_logo(merk: Image.Image, naam: Image.Image) -> Image.Image:
    """Logo voor het klantscherm: maximaal 300x60 getoond, dus 2x zo groot gemaakt."""
    hoogte = 120
    merk = merk.resize((hoogte, hoogte), Image.LANCZOS)
    tekst_h = 54
    naam = naam.resize((round(naam.width * tekst_h / naam.height), tekst_h), Image.LANCZOS)
    tussenruimte = 18
    logo = Image.new("RGBA", (hoogte + tussenruimte + naam.width, hoogte), (0, 0, 0, 0))
    logo.paste(merk, (0, 0), merk)
    logo.paste(naam, (hoogte + tussenruimte, (hoogte - tekst_h) // 2), naam)
    return logo


def svg_met_png(beeld: Image.Image) -> str:
    buf = io.BytesIO()
    beeld.save(buf, "PNG")
    data = base64.b64encode(buf.getvalue()).decode("ascii")
    w, h = beeld.size
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<image width="{w}" height="{h}" xlink:href="data:image/png;base64,{data}"/></svg>\n')


def main() -> None:
    merk = vierkant_beeldmerk()
    groot = merk.resize((512, 512), Image.LANCZOS)
    groot.save(MAP / "icon.png")
    groot.save(MAP / "icon.ico", sizes=[(m, m) for m in ICO_MATEN])
    # Het systeemvak leest het grootste formaat; net als upstream één 32x32.
    merk.resize((32, 32), Image.LANCZOS).save(MAP / "tray-icon.ico", sizes=[(32, 32)])
    for maat, naam in [(32, "32x32.png"), (64, "64x64.png"), (128, "128x128.png"),
                       (256, "128x128@2x.png"), (48, "app-icon-48.png")]:
        merk.resize((maat, maat), Image.LANCZOS).save(MAP / naam)
    (MAP / "icon.svg").write_text(svg_met_png(merk.resize((256, 256), Image.LANCZOS)),
                                  encoding="ascii")
    liggend_logo(merk, woordmerk()).save(MAP / "logo.png")
    print("klaar:", sorted(p.name for p in MAP.iterdir() if p.is_file()))


if __name__ == "__main__":
    main()
