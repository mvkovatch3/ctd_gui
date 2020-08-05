# ctd_gui

ctd_gui (name in progress) is a Python package for manually flagging oceanographic CTD data with a GUI. It was recently split off from the ctdcal package to better handle a wider variety of use cases.

## Quickstart

``` 
git clone https://github.com/mvkovatch3/ctd_gui.git
## Unzip the data zip file into the ctd_gui directory
conda env create -f ctd_gui.yml
bokeh serve --show ctd_gui.py
```

Once installed, code can be run by calling:
  bokeh serve [--show] ctd_gui.py
