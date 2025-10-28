@echo off
REM Start test client for cat-incremental-search-filter
echo Starting cat-incremental-search-filter test client...
echo.
echo Make sure the server is running first!
echo.
python src\client.py --config-filename config.toml
