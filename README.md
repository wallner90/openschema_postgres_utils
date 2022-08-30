# openSCHEMA postgreSQL ORM and Interface Utils

## Structure
``` text
.
.devcontainer/              <-- VSCode devcontainer settings
.github/workflows/          <-- github specific workflow settings
.vscode/                    <-- VSCode specific settings, launch settings
src/
  ├─ model/                 <-- openSCHEMA ORM model
  ├─ openschema_utils/      <-- math and i/o utils
  ├─ openVSLAM_io/          <-- openVSLAM specific i/o utils
  ├─ openschema_loader.py   <-- tool to load data to and from the db
.gitignore
Dockerfile                  <-- Dockerfile used by VSCode with all deps
LICENSE
README.md
pyproject.toml
setup.cfg
setup.py
tox.ini
```

## Setup with Visual Studio Code (+devcontainer)
Navigate to base directory and open with VSCode:
``` bash
> cd openschema_postgres_utils
> code .
```
Use `Ctrl+Shift+P` and `Remote-Container: Reopen in Container`.

## .gitignore

The [.gitignore](.gitignore) file is a copy of the [Github C++.gitignore file](https://github.com/github/gitignore/blob/master/C%2B%2B.gitignore),
with the addition of ignoring the build directory (`build/`).

## FFG Project
[DE ]Die FFG ist die zentrale nationale Förderorganisation und stärkt Österreichs Innovationskraft. Dieses Projekt wird aus Mitteln der FFG gefördert. 

[EN] FFG is the central national funding organization and strengthens Austria's innovative power. This project is funded by the FFG. 

[www.ffg.at](www.ffg.at)

Projekt: [openSCHEMA](https://iktderzukunft.at/de/projekte/open-semantic-collaborative-hierarchical-environment-mapping.php)