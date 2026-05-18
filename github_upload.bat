@echo off
echo ===================================================
echo GitHub One-Click Auto Uploader by SEMIDIGITAL
echo ===================================================
echo.

:: Repository URL
set REPO_URL=https://github.com/semidigital-kr/LUFS-Normalizer.git

if not exist ".git" (
    echo [INFO] Initializing Git repository...
    git init
    git remote add origin %REPO_URL%
)

git branch -M main

echo [INFO] Adding all files in the current folder...
git add .

echo.
set /p version_tag="Enter version tag (e.g., v0.0.2) and press ENTER: "

:: Commit and Tag (-f 옵션 추가: 기존 태그가 있으면 강제로 덮어씀)
git commit -m "Release %version_tag%"
git tag -f %version_tag%

echo.
echo [INFO] Uploading to GitHub. Please wait...

:: Push code and tags
git push -f origin main
git push -f origin %version_tag%

echo.
echo ===================================================
echo Upload complete! Check your GitHub repository.
echo ===================================================
pause