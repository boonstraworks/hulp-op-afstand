"""Zet naam, bedrijf en logo van BoonstraWorks in de RustDesk-bron, vlak voor het bouwen.

Draait in .github/workflows/boonstraworks-windows.yml vanuit de hoofdmap van de repo.
De werkwijze volgt bryangerlach/rdgen (GPL-3.0): .github/workflows/generator-windows.yml
(naam en bedrijf vervangen in Cargo.toml en Runner.rc, iconen vervangen) en
.github/patches/allowCustom.py (custom.txt zonder handtekening van RustDesk toestaan).

Verschillen met rdgen:
- De teksten in src/lang worden niet aangepast: src/lang.rs vervangt "RustDesk" al
  tijdens het draaien door de app-naam uit custom.txt.
- Elke vervanging moet precies raak zijn. Verandert upstream een regel, dan stopt de
  bouw, in plaats van stil een half aangepaste app op te leveren.
"""

import re
import shutil
import sys
from pathlib import Path

APP_NAAM = "BoonstraWorks Hulp op afstand"
APP_INTERN = "BoonstraWorksHulp"
BEDRIJF = "BoonstraWorks"
WEBSITE = "https://boonstraworks.nl"
COPYRIGHT = "Copyright © 2026 BoonstraWorks. Gebaseerd op RustDesk (AGPL-3.0)."

ROOT = Path.cwd()
MERK = Path(__file__).resolve().parent / "merk"


def vervang(pad: str, regels: list[tuple[str, str]], regex: bool = False) -> None:
    """Vervangt elk patroon precies één keer; regeleinden blijven zoals ze waren."""
    bestand = ROOT / pad
    with open(bestand, encoding="utf-8", newline="") as f:
        tekst = f.read()
    eol = "\r\n" if "\r\n" in tekst else "\n"
    tekst = tekst.replace("\r\n", "\n")
    for oud, nieuw in regels:
        if regex:
            tekst, aantal = re.subn(oud, lambda _m: nieuw, tekst)
        else:
            aantal = tekst.count(oud)
            tekst = tekst.replace(oud, nieuw)
        if aantal != 1:
            sys.exit(f"FOUT {pad}: {aantal}x gevonden in plaats van 1x: {oud!r}")
    with open(bestand, "w", encoding="utf-8", newline="") as f:
        f.write(tekst.replace("\n", eol))
    print(f"aangepast: {pad} ({len(regels)} vervangingen)")


def versie_info() -> None:
    winres = [
        (r'LegalCopyright = ".*"', f'LegalCopyright = "{COPYRIGHT}"'),
        (r'ProductName = "RustDesk"', f'ProductName = "{APP_NAAM}"'),
        (r'FileDescription = "RustDesk Remote Desktop"', f'FileDescription = "{APP_NAAM}"'),
        (r'OriginalFilename = "rustdesk.exe"', f'OriginalFilename = "{APP_INTERN}.exe"'),
    ]
    vervang("Cargo.toml", winres, regex=True)
    vervang("libs/portable/Cargo.toml", winres, regex=True)
    rc = {
        "CompanyName": BEDRIJF,
        "FileDescription": APP_NAAM,
        "InternalName": APP_INTERN,
        "LegalCopyright": COPYRIGHT,
        "OriginalFilename": f"{APP_INTERN}.exe",
        "ProductName": APP_NAAM,
    }
    vervang("flutter/windows/runner/Runner.rc",
            [(rf'VALUE "{k}", "[^"]*" "\\0"', f'VALUE "{k}", "{v}" "\\0"') for k, v in rc.items()],
            regex=True)


def custom_txt_zonder_handtekening() -> None:
    # Zoals rdgen allowCustom.py: de controle op de handtekening van RustDesk vervalt,
    # zodat onze eigen custom.txt (base64 van JSON) gelezen wordt.
    vervang("src/common.rs", [(
        '    const KEY: &str = "5Qbwsde3unUcJBtrx9ZkvUmwFNoExHzpryHuPUdqlWM=";\n'
        '    let Some(pk) = get_rs_pk(KEY) else {\n'
        '        log::error!("Failed to parse public key of custom client");\n'
        '        return;\n'
        '    };\n'
        '    let Ok(data) = sign::verify(&data, &pk) else {\n'
        '        log::error!("Failed to dec custom client config");\n'
        '        return;\n'
        '    };\n',
        '    // BoonstraWorks: custom.txt is niet ondertekend (zie boonstraworks/merk_toepassen.py).\n',
    )])


def schermen() -> None:
    # Klantscherm: het puntjesmenu naast de code opent de instellingen; weg als die uit staan.
    vervang("flutter/lib/desktop/pages/desktop_home_page.dart", [(
        "                        buildPopupMenu(context)\n",
        "                        if (!bind.isDisableSettings()) buildPopupMenu(context)\n",
    )])
    # Over-pagina (alleen in de helper-app te zien): eigen naam en site, bron blijft vermeld.
    vervang("flutter/lib/desktop/pages/desktop_setting_page.dart", [
        ("launchUrlString('https://rustdesk.com/privacy.html');", f"launchUrlString('{WEBSITE}');"),
        ("launchUrlString('https://rustdesk.com');", f"launchUrlString('{WEBSITE}');"),
        ("Purslane Tech Pte. Ltd.\\n$license",
         f"{BEDRIJF}\\nGebaseerd op RustDesk, © Purslane Tech Pte. Ltd.\\n$license"),
    ])


def iconen() -> None:
    kopie = {
        "icon.ico": ["res/icon.ico", "flutter/windows/runner/resources/app_icon.ico",
                     "flutter/assets/icon.ico"],
        "tray-icon.ico": ["res/tray-icon.ico"],
        "icon.png": ["res/icon.png"],
        "32x32.png": ["res/32x32.png"],
        "64x64.png": ["res/64x64.png"],
        "128x128.png": ["res/128x128.png"],
        "128x128@2x.png": ["res/128x128@2x.png"],
        "icon.svg": ["flutter/assets/icon.svg"],
        "app-icon-48.png": ["flutter/assets/icon.png"],
        "logo.png": ["flutter/assets/logo.png"],
    }
    for bron, doelen in kopie.items():
        for doel in doelen:
            shutil.copyfile(MERK / bron, ROOT / doel)
            print(f"icoon: {bron} -> {doel}")


if __name__ == "__main__":
    versie_info()
    custom_txt_zonder_handtekening()
    schermen()
    iconen()
