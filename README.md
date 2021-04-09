# Github Course Teams Manager

Helps manage repos and teams for university courses on GitHub.

## Setup and usage

It is suggested to use GCTM in a virtual environment (virtualenv). To set that up, execute the following:

```bash
virtualenv ./venv             # Create virtualenv folder
source ./venv/bin/activate    # Enter the virtualenv
python -m pip install -r requirements.txt   # Install all dependencies
```

Acquire the database files from the gist project. You need the following files:

- stored_students.csv
- stored_teams.csv

These files should be put in the same folder as `gctm.py`.

### Authentication

`AUTH.py` should contain a GitHub Authentication Token registered to your account. You can generate one by navigating on [github.com](https://github.com) to the following: `Settings > Developer Settings > Personal Access Tokens > Generate new token`.

A template for `AUTH.py` is given in `AUTH.py.default`. Insert your token in between the single-quotes in `AUTH.py` when using `AUTH.py.default`.

### Usage

### Create repos

```bash
./gctm.py repo new --help
```

```txt
usage: gctm.py repo new [-h] [-n NUMBER] [-N NAME] [-t num [num ...]] [-T num [num ...]] [-d]

optional arguments:
  -h, --help            show this help message and exit
  -n NUMBER, --number NUMBER
                        The number for the lab repo to create
  -N NAME, --name NAME  The name of the repo to create
  -t num [num ...], --team-num num [num ...]
                        Create a repo for specific teams identified by the team number
  -T num [num ...], --team-num-negate num [num ...]
                        Do not create repos for teams identified by the following team numbers
  -d, --dry-run         Verify with Github but don't modify anything on Github
```

#### Numbered repos (labs)

```bash
./gctm.py repo new -n 5
```

The command shown above creates a repo numbered as lab 5.

#### Named repos (projects etc.)

```bash
./gctm.py repo new -N project
```

The command shown above creates a repo named as "project".

## Dependencies

All Python dependencies are listed in `requirements.txt`.
