# BoonstraWorks Hulp op afstand

Eigen Windows-app van [BoonstraWorks](https://boonstraworks.nl) voor computerhulp op afstand.
De app is gebouwd op [RustDesk](https://github.com/rustdesk/rustdesk) (AGPL-3.0). Deze map bevat
alles wat BoonstraWorks eraan verandert; de rest van de repo volgt upstream.

BoonstraWorks is geen onderdeel van RustDesk of Purslane Tech Pte. Ltd.

## Twee exe's

| Bestand | Voor wie | Stand |
| --- | --- | --- |
| `BoonstraWorks-Hulp-op-afstand.exe` | klant | alleen inkomend: code en eenmalig wachtwoord, geen menu's of instellingen |
| `BoonstraWorks-Hulp-geven.exe` | helper | alleen uitgaand; de klant ziet de helper als "BoonstraWorks · Steven" |

Beide komen uit één bouw; alleen `custom.txt` verschilt (`custom-klant.json`, `custom-helper.json`).
Zonder eigen server gebruikt de app de openbare RustDesk-servers.

## Bouwen

GitHub Actions, workflow `.github/workflows/boonstraworks-windows.yml` (handmatig of bij een push in
deze map). Resultaat: artifact `boonstraworks-hulp-windows-x64`, ongetekend.

Tijdens de bouw past `merk_toepassen.py` de bron aan: naam en bedrijf in de versie-info
(`Cargo.toml`, `libs/portable/Cargo.toml`, `flutter/windows/runner/Runner.rc`), iconen en logo,
het menu naast de code op het klantscherm, de Over-pagina, en het lezen van een niet-ondertekende
`custom.txt`.

Iconen en logo staan in `merk/`; opnieuw maken met
`uv run --with pillow python boonstraworks/maak-merkbestanden.py`.

## Bronnen

- RustDesk, AGPL-3.0: de app zelf en de Windows-job in `.github/workflows/flutter-build.yml`.
- [bryangerlach/rdgen](https://github.com/bryangerlach/rdgen), GPL-3.0: `generator-windows.yml` en
  `.github/patches/allowCustom.py` dienden als voorbeeld voor het inbakken van naam, logo en
  `custom.txt`.

## Licentie

AGPL-3.0, net als RustDesk. De volledige broncode van deze app staat in deze repo.
