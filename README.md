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

If you move the executable to another Windows computer, do not copy an old
`settings.json` next to it unless you want to keep its configured log folder.
By default the application writes logs to the current user's Dropbox folder:

```powershell
%USERPROFILE%\Dropbox\ari4kids
```


# TODO 1

При синхронизации через dropbox файл со списком имен перезаписывается более поздней (часто менее полной) версией. Нужно переделать механику хранения, чтобы добавленные пользователи не исчезали при запуске с другого подключенного к dropbox компьютера. Учесть, что пользователи могут создаваться и при работе программы без интернета, то есть новые пользователи и их логи могут доходить до облака с опозданием. Логи при этом сохраняются без проблем. Может быть стоит не хранить пользователей отдельно, а считывать их из названий логов. Этот способ исправления - желаемый.

# TODO 2

Сразу после выполнения задания интерфейс подвисает. Видимо, какое-то время тратися на чтение xlsx файлов. Это не удобно. Нужно окрывать страницу с результатами сразу, но до момента прогрузки данных показывать прогресс-бар. Прогресс нужно считать по числу файлов - каждый загрухенный из общего числа файлов файл должен давать одинаковый прирост прогресса на прогресс-баре.