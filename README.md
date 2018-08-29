# sd2-github-automation

Helps manage repos for the Software Development 2 course.

## Setup and usage

It is suggested to use sd2 in a virtual environement (virtualenv). To set that up execute the following:

```bash
virtualenv ./venv             # Create virtualenv folder
source ./venv/bin/activate    # Enter the virtualenv
pip install -r requirements   # Install all dependencies
```

Acquire the database files from the gist project. You need the following files:

- stored_students.csv
- stored_teams.csv

These files should be put in the same folder as ```sd2.py```.

### Authentication

```AUTH.py``` should contain a Github Authentication Token registered to your account. You can generate one by navigating on Github.com to the following: ```Settings > Developer Settings > Personal Access Tokens > Generate new token```.

A template for ```AUTH.py``` is given in ```AUTH.py.default```. Insert your token inbetween the single-quotes in ```AUTH.py``` when using ```AUTH.py.default```.

### Usage

### Create repos

```bash
./sd2.py repo new --help
usage: sd2.py repo new [-h] [-n NUMBER] [-N NAME] [-t num [num ...]]
                       [-T num [num ...]] [-d]

optional arguments:
  -h, --help            show this help message and exit
  -n NUMBER, --number NUMBER
                        The number for the lab repo to create
  -N NAME, --name NAME  The name of the repo to create
  -t num [num ...], --team-num num [num ...]
                        Create a repo for specific teams identified by the
                        team number
  -T num [num ...], --team-num-negate num [num ...]
                        Do not create repos for teams identified by the
                        following team numbers
```

#### Numbered repos (labs)

```bash
./sd2.py repo new -n 5
```

The command shown above creates a repo numbered as lab 5.

#### Named repos (projects etc.)

```bash
./sd2.py repo new -N project
```

The command shown above creates a repo named as "project".

## Dependencies

All Python dependencies are listed in ```requirements.txt```.
