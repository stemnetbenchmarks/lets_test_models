
# To Use Linters and Formatters
- To activate a flake8 or pylint config file, rename with a . before the name
"-m" calls a python module, and is often recommended even if not strictly required
```bash
$ python -m black FILENAME.py

$ python -m flake8 FILENAME.py
$ python -m flake8 FILENAME.py --verbose

$ python -m pylint FILENAME.py

$ python -m mypy FILENAME.py
$ python -m pydocstyle FILENAME.py
```

# Check python version: (eventually will be upgraded, updated)
```bash
python --version
python3 --version
python3.11 --version
```

# Check github branch
```bash
git branch
git status
```

# To build env:
```bash
python -m venv env; source env/bin/activate
python -m pip install --upgrade pip; python -m pip install -r requirements.txt
python3.11 -m pip install git+https://github.com/psf/black pylint pydocstyle flake8
```

# To end frozen process:
Note: example here is 5000, use your port number
```bash
sudo lsof -n -i :5000 | grep LISTEN
kill -9 PID_NUMBER_HERE
```
