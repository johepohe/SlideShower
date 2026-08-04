#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif

[Setup]
AppId={{155CBBA0-19D2-40C0-9082-BD514E9FC585}
AppName=SlideShower
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\SlideShower
DefaultGroupName=SlideShower
OutputDir=..\installers
OutputBaseFilename=SlideShower-{#MyAppVersion}-Windows-x64-Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
UninstallDisplayIcon={app}\SlideShower.exe

[Files]
Source: "..\dist\SlideShower\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\SlideShower"; Filename: "{app}\SlideShower.exe"
Name: "{autodesktop}\SlideShower"; Filename: "{app}\SlideShower.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Skapa en genväg på skrivbordet"; GroupDescription: "Genvägar:"

[Run]
Filename: "{app}\SlideShower.exe"; Description: "Starta SlideShower"; Flags: nowait postinstall skipifsilent
