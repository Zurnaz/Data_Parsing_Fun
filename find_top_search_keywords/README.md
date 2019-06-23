# Getting your most searched keywords from Firefox and Chrome

## Summary

Quick guide to pull data from Firefox and Chrome browser history and do some analysis on it.

### Prerequisites

```txt
Python 3
Jupyter
```

### Getting the data

Chrome on my machine was located in:

```bash
/home/bogdan/.config/google-chrome-unstable/Default/History
```

You can use this to find it (Linux)

```bash
find /home/ -name History
```

Firefox was located in:

```bash
/home/bogdan/.mozilla/firefox/1g46uy29.dev-edition-default/places.sqlite
```

Use this to find it (Linux again):

```bash
find /home/ -name places.sqlite
```

Note: I recommend copying the data from those location to where the Jupyter Notebook is located, you can get a database locked error if your reference it. I think it's probably due to the browser using it while your trying to access it.

### Run the book

Open the book and install the dependencies, setup an virtual environment if you like.

```bash
cd to/the/folder
python -m venv venv
source venv/bin/activate
pip install pandas openpyxl
jupyter notebook
```

* Select Search History
* Change the file locations of the respective browsers files if they are not in current folder
* Run the book

Note: If your only using chrome, then run the first step and move down to where it starts to say Google and run it.

It should create two xlsx files, now check them out. The regex I used was fairly basic to split up the words so you get the obvious ones that are part of the URL at the top like com or google but the interesting results are right after that.
