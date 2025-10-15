@echo off
REM Start server for cat-incremental-search-filter
echo Starting cat-incremental-search-filter server...
echo.
echo Press Ctrl+C to stop the server
echo.
python server.py --config-filename config.toml
