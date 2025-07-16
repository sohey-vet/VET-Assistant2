@echo off
echo VET-Assistant2 Project Structure Verification
echo ===========================================
echo.

echo Root directory contents:
dir /b
echo.

echo Checking src/ directory:
if exist "src" (
    echo Contents of src/:
    dir /b src\
) else (
    echo src/ directory not found
)
echo.

echo Checking scripts/ directory:
if exist "scripts" (
    echo Contents of scripts/:
    dir /b scripts\
) else (
    echo scripts/ directory not found
)
echo.

echo Checking tests/ directory:
if exist "tests" (
    echo Contents of tests/:
    dir /b tests\
) else (
    echo tests/ directory not found
)
echo.

echo Checking data/ directory:
if exist "data" (
    echo Contents of data/:
    dir /b data\
) else (
    echo data/ directory not found
)
echo.

echo Checking docs/ directory:
if exist "docs" (
    echo Contents of docs/:
    dir /b docs\
) else (
    echo docs/ directory not found
)
echo.

echo ===========================================
echo Verification complete!
pause