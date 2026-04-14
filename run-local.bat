@echo off

@echo Browse to http://127.0.0.1:8000 to open the application UI
@echo Browse to http://127.0.0.1:8000/docs to get API docs

fastapi dev src\app.py
