# How to Run Essence Bound on Windows

## Quick Start (Recommended)

To play the game, simply run the `run_windows.bat` file.
1. Double-click `run_windows.bat` in the project folder.
2. It will automatically check for Python, set up the environment, and launch the game.

## Manual Setup

This guide explains how to run the Essence Bound game manually as a native Windows application and how to package it into a standalone `.exe` file.

## Prerequisites

1.  **Python 3.8+**: Ensure Python is installed on your system.
2.  **Dependencies**: Install the required packages (standard library `tkinter` is usually included with Python).

## Running the App from Source

To run the game window directly from the source code without compiling:

1.  Open Command Prompt or PowerShell.
2.  Navigate to the repository root directory.
3.  Run the following command:

```bash
python src/game_app.py
```

This will launch the native Windows GUI.

## Building a Standalone .exe

To create a single executable file that you can share or run without opening a terminal, use `PyInstaller`.

### 1. Install PyInstaller

```bash
pip install pyinstaller
```

### 2. Build the Executable

Run the following command from the repository root. This command tells PyInstaller to:
*   `--onefile`: Bundle everything into a single `.exe`.
*   `--noconsole`: Don't show the black command window in the background.
*   `--name`: Name the output file "EssenceBound".
*   `--add-data`: Include the `data` folder (where game JSONs live) inside the app.

**Command (Windows):**

```bash
pyinstaller --noconsole --onefile --name "EssenceBound" --add-data "data;data" src/game_app.py
```

*Note: The `--add-data` syntax uses a semicolon `;` on Windows. If you are building on Linux/Mac for Windows (using Wine), use a colon `:`.*

### 3. Locate the App

After the build process finishes (it may take a minute):
1.  Go to the `dist/` folder in your project directory.
2.  You will find `EssenceBound.exe`.
3.  You can move this file anywhere, but **ensure the `data/` folder is accessible** if the build didn't package it correctly (PyInstaller sometimes struggles with dynamic paths).

**Robust Data Loading Tip:**
If the `.exe` crashes immediately, it usually means it can't find the `data` folder. Ensure a copy of the `data` folder exists next to the `.exe` file, or ensure the internal path handling in the code supports `sys._MEIPASS` (which `src/game_app.py` and `src/mechanics.py` should handle if using relative paths correctly).

## Troubleshooting

*   **Missing Data:** If the game starts but shows empty lists (no monsters, no items), copy the `data` folder from the source repository and paste it into the same folder as your `.exe`.
*   **Console Output:** If you want to see error messages for debugging, build without `--noconsole`.
