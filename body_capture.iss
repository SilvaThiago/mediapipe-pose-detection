; Script de instalação para Inno Setup
[Setup]
AppName=BodyCapture
AppVersion=1.0
DefaultDirName={pf}\BodyCapture
DefaultGroupName=BodyCapture
OutputDir=.
OutputBaseFilename=Instalador_BodyCapture
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\body_capture_optimizadoc.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\BodyCapture"; Filename: "{app}\body_capture_mac.exe"
Name: "{commondesktop}\BodyCapture"; Filename: "{app}\body_capture_mac.exe"

[Run]
Filename: "{app}\body_capture_optimizado.exe"; Description: "Executar BodyCapture"; Flags: nowait postinstall skipifsilent
