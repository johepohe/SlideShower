# Installation och paketering av SlideShower

## Linux – färdig installationsfil

Den färdigbyggda installationsfilen finns här:

`installers/slideshower_1.0.0_amd64.deb`

Paketet är byggt för Debian/Ubuntu-liknande Linux på x86-64. Installera genom
att dubbelklicka på filen i filhanteraren eller genom att öppna en terminal i
projektmappen och köra:

```bash
sudo apt install ./installers/slideshower_1.0.0_amd64.deb
```

Efter installationen finns **SlideShower** i systemets programmeny. Det kan
också startas från terminalen:

```bash
slideshower
```

Avinstallera med:

```bash
sudo apt remove slideshower
```

## Bygga ett nytt Linux-paket

Kör följande i projektmappen:

```bash
.venv/bin/python -m pip install -r requirements-build.txt
packaging/build_linux_deb.sh 1.0.0
```

Byt `1.0.0` mot önskat versionsnummer. Den nya `.deb`-filen hamnar i mappen
`installers`.

## Windows

Windows-installationsfilen måste byggas på en Windows-dator. Installera först:

- Python 3.10 eller senare
- Inno Setup 6

Öppna PowerShell i projektmappen och kör:

```powershell
powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1 -Version 1.0.0
```

Skriptet installerar Python-beroenden, skapar den fristående appen och bygger
sedan en vanlig `Setup.exe`. Resultatet hamnar i mappen `installers`.

## macOS

macOS-paketet måste byggas på en Mac med Python 3.10 eller senare. Öppna
Terminal i projektmappen och kör:

```bash
chmod +x packaging/build_macos.sh
packaging/build_macos.sh 1.0.0
```

Resultatet blir en `.app` inuti en `.dmg` i mappen `installers`.

För användning på den egna datorn kan den osignerade appen öppnas via
kontrollklick och **Öppna**. För normal distribution till andra Mac-datorer bör
appen signeras och notariseras med ett Apple Developer-konto.

## Relevanta filer

- `slideshow.py` – programmets källkod
- `requirements.txt` – beroenden för att köra från Python
- `requirements-build.txt` – extra beroenden för paketering
- `packaging/build_linux_deb.sh` – Linux-bygge
- `packaging/build_windows.ps1` – Windows-bygge
- `packaging/windows-installer.iss` – Inno Setup-definition
- `packaging/build_macos.sh` – macOS-bygge
- `packaging/slideshower.desktop` – post i Linux programmeny
- `packaging/slideshower.svg` – programikon
