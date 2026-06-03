# ari4kids

Curses based tool automizing child's learning of simple arithmetics.  

# install

## install conda and create conda env

conda config --add channels conda-forge  
conda config --set channel_priority strict  
conda create -n ari4kids python openpyxl pandas ncurses

## install curses via pip

conda activate ari4kids
pip install windows-curses

## download

or clone current repo

# run

navigate to run.py file

python3 run.py

# build exe for Windows

Create and activate a Python 3.11 environment, then install runtime dependencies:

```powershell
python -m pip install -r requirements.txt
python -m pip install windows-curses pyinstaller
```

Build the executable from the project root:

```powershell
python -m PyInstaller --onefile --name ari4kids run.py
```

The built application will be here:

```powershell
dist\ari4kids.exe
```

Run it from PowerShell or `cmd`:

```powershell
.\dist\ari4kids.exe
```

Do not use `--noconsole`: this is a curses console application, so it needs a terminal window.
