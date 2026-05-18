[Setup]
; 프로그램 기본 정보
AppName=LUFS Normalizer
AppVersion=0.0.2
AppPublisher=SEMIDIGITAL
AppPublisherURL=https://semidigital.co.kr
; 기본 설치 경로 (C:\Program Files (x86)\SEMIDIGITAL\LUFS Normalizer)
DefaultDirName={autopf}\SEMIDIGITAL\LUFS Normalizer
DefaultGroupName=SEMIDIGITAL
; 만들어질 설치 파일의 이름
OutputBaseFilename=LUFS_Normalizer_Setup_v0.0.2
; 설치 파일 아이콘 (방금 변환한 ico 파일 적용)
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
; 설치 후 컴퓨터 재시작 묻지 않음
DisableProgramGroupPage=yes

; ★ 제어판(프로그램 추가/제거) 표시 이름 및 아이콘 커스텀 설정 ★
UninstallDisplayName=LUFS Normalizer by SEMIDIGITAL 0.0.2
UninstallDisplayIcon={app}\icon.ico

[Tasks]
; 바탕화면 바로가기 생성 여부를 묻는 체크박스 추가 (기본값: 체크 해제 상태)
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; 설치될 파일들 목록 (현재 스크립트 파일이 있는 폴더 기준)
Source: "main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "ffmpeg.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "sd.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "PretendardVariable.ttf"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
; social 폴더 안의 내용물 전체 복사
Source: "social\*"; DestDir: "{app}\social"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; 시작 메뉴 및 바탕화면 아이콘 (바탕화면 아이콘은 위 Tasks의 체크 여부에 따라 생성됨)
Name: "{group}\LUFS Normalizer"; Filename: "{app}\main.exe"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\LUFS Normalizer"; Filename: "{app}\main.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
; 설치 완료 후 프로그램 바로 실행하기 옵션 추가
Filename: "{app}\main.exe"; Description: "Launch LUFS Normalizer"; Flags: nowait postinstall skipifsilent