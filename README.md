# SlideShower

En lokal slideshow-app som söker igenom en vald huvudmapp och alla dess
undermappar. JPG- och HEIC-bilder sorteras efter fotograferingsdatum i EXIF.
Om en bild saknar fotograferingsdatum används filens ändringstid.

## Installation

Python 3.10 eller senare rekommenderas.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python slideshow.py
```

På Windows är de två sista kommandona i stället:

```powershell
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python slideshow.py
```

## Tangenter

- `F11`: helskärm eller tillbaka till fönster
- `Esc`: lämna helskärm
- `Mellanslag`: pausa eller fortsätt
- `←` / `→`: föregående eller nästa bild
- `+` / `-`: kortare eller längre bildtid (1–60 sekunder)
- `Ctrl+O`: välj en ny mapp

Slideshowen börjar automatiskt när bilderna har lästs in och går tillbaka till
den första bilden efter den sista.

## Installationspaket

Ett färdigbyggt Debian-paket läggs i `installers/`. Installera det genom att
dubbelklicka på filen eller med:

```bash
sudo apt install ./installers/slideshower_1.0.0_amd64.deb
```

Bygg ett nytt Linux-paket med:

```bash
.venv/bin/python -m pip install -r requirements-build.txt
packaging/build_linux_deb.sh 1.0.0
```

Windows-paket byggs på Windows med `packaging/build_windows.ps1`. Skriptet
skapar först programmet och använder sedan Inno Setup 6 för att skapa en vanlig
`Setup.exe` i `installers`.

macOS-paket måste byggas på macOS. Kör `packaging/build_macos.sh`; resultatet
blir en `.app` inuti en `.dmg` i `installers`. För distribution till andra
Mac-datorer bör paketet dessutom signeras och notariseras med ett Apple
Developer-konto.

## Publicera på GitHub

GitHub Actions bygger installationsfiler på Windows, macOS och Linux och
publicerar dem tillsammans i en GitHub Release. Skapa och skicka en versionstagg:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Workflowen kan även startas manuellt under **Actions → Build and publish
installers → Run workflow**. Ange då versionsnumret utan `v`, exempelvis
`1.0.0`.

Filerna som publiceras är en Windows-installation för x64, en osignerad macOS
DMG för Intel och ett Debian/Ubuntu-paket för x86-64. macOS-paketet behöver
senare signering och notarisering för att öppnas utan Gatekeeper-varning.
