; Build with scripts/build_installer.py. Payload must be a verified portable ZIP.
#ifndef PayloadDir
  #error PayloadDir is required
#endif
#ifndef AppVersion
  #error AppVersion is required
#endif
#ifndef OutputDir
  #error OutputDir is required
#endif

[Setup]
AppId={{D9FB8823-266B-4DC7-942B-D838D0E9550A}
AppName=Imadeoconvert
AppVersion={#AppVersion}
VersionInfoVersion={#FileVersion}
VersionInfoDescription=Imadeoconvert Setup
AppPublisher=KLucen
AppPublisherURL=https://github.com/KLucen/Imadeoconvert
AppSupportURL=https://github.com/KLucen/Imadeoconvert/issues
AppUpdatesURL=https://github.com/KLucen/Imadeoconvert/releases
DefaultDirName={localappdata}\Programs\Imadeoconvert
DefaultGroupName=Imadeoconvert
AllowNoIcons=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64os
ArchitecturesInstallIn64BitMode=x64os
MinVersion=10.0
LicenseFile={#PayloadDir}\LICENSE
SetupIconFile=..\icon.ico
UninstallDisplayIcon={app}\Imadeoconvert.exe
OutputDir={#OutputDir}
OutputBaseFilename=Imadeoconvert-{#AppVersion}-windows-x64-setup
Compression=lzma2/fast
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
CloseApplications=yes
RestartApplications=no
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Files]
Source: "{#PayloadDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Imadeoconvert"; Filename: "{app}\Imadeoconvert.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\Imadeoconvert"; Filename: "{app}\Imadeoconvert.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\Imadeoconvert.exe"; Description: "Launch Imadeoconvert"; Flags: nowait postinstall skipifsilent

; No [UninstallDelete] rules: preserve converted files, user-added files and settings.
