@echo off
echo Starting VET-Assistant2 project organization...
echo.

echo Step 1: Creating directory structure...
if not exist "src" mkdir src
if not exist "scripts" mkdir scripts  
if not exist "tests" mkdir tests
if not exist "data" mkdir data
if not exist "docs" mkdir docs
echo - Directories created successfully
echo.

echo Step 2: Moving Python source files to src/...
if exist "enhanced_post_generator.py" move "enhanced_post_generator.py" "src\"
if exist "ai_content_generator.py" move "ai_content_generator.py" "src\"
if exist "advanced_duplicate_monitor.py" move "advanced_duplicate_monitor.py" "src\"
if exist "google_sheets_uploader.py" move "google_sheets_uploader.py" "src\"
echo - Python source files moved to src/
echo.

echo Step 3: Moving test files to tests/...
if exist "test_char_count.py" move "test_char_count.py" "tests\"
echo - Test files moved to tests/
echo.

echo Step 4: Moving database to data/...
if exist "vet_assistant2_posts.db" move "vet_assistant2_posts.db" "data\"
echo - Database moved to data/
echo.

echo Step 5: Moving documentation to docs/...
if exist "README.md" move "README.md" "docs\"
if exist "GOOGLE_SHEETS_SETUP.md" move "GOOGLE_SHEETS_SETUP.md" "docs\"
echo - Documentation moved to docs/
echo.

echo Step 6: Removing empty files (0 bytes)...
if exist "check_dependencies.py" del "check_dependencies.py"
if exist "cleanup.bat" del "cleanup.bat"
if exist "delete_files.bat" del "delete_files.bat"
if exist "simple_ai_test.py" del "simple_ai_test.py"
if exist "simple_start.bat" del "simple_start.bat"
if exist "test_dog_posts.py" del "test_dog_posts.py"
if exist "test_full_generation.py" del "test_full_generation.py"
if exist "test_updated_posts.py" del "test_updated_posts.py"
echo - Empty files removed
echo.

echo Step 7: Moving batch files to scripts/...
for %%f in (*.bat) do (
    if not "%%f"=="organize_files.bat" (
        move "%%f" "scripts\"
    )
)
echo - Batch files moved to scripts/
echo.

echo Step 8: Moving this organization script to scripts/...
move "organize_files.bat" "scripts\"
echo - Organization script moved to scripts/
echo.

echo ===========================================
echo VET-Assistant2 project organization complete!
echo ===========================================
echo.
echo New directory structure:
echo - src/          : Python source files
echo - scripts/      : Batch scripts  
echo - tests/        : Test files
echo - data/         : Database files
echo - docs/         : Documentation
echo.
pause