@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo   NPP PORTAL - CAP NHAT DU LIEU
echo ============================================
echo.
echo [1/3] Dang doc allocation.xlsx va build lai trang web...
python build.py
if errorlevel 1 (
    echo.
    echo ============================================
    echo   CO LOI! Vui long doc thong bao loi phia tren.
    echo   Kiem tra lai file allocation.xlsx ^(ten sheet, ten cot^).
    echo ============================================
    pause
    exit /b 1
)

echo.
echo [2/3] Dang day du lieu len GitHub...
git add NPP_Portal.html allocation.xlsx
git commit -m "Update data %date% %time%"
if errorlevel 1 (
    echo Khong co thay doi nao de commit, hoac da commit roi.
)
git push

if errorlevel 1 (
    echo.
    echo ============================================
    echo   CO LOI khi push len GitHub.
    echo   Kiem tra ket noi mang hoac dang nhap Git.
    echo ============================================
    pause
    exit /b 1
)

echo.
echo [3/3] HOAN TAT!
echo Cho khoang 30-60 giay de GitHub Pages / Netlify deploy.
echo Sau do vao web va nhan Ctrl+Shift+R de tai lai du lieu moi.
echo.
pause
