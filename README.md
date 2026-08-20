# Hill Curve Estimator

Single-stage Hill/Ramberg-Osgood tensile curve estimator.

Inputs: E, yield strength, UTS, maximum elongation.

The app calculates n from the UTS point, plots the estimated true stress-true strain curve, accepts pasted two-column test data, overlays the curves, saves plots and exports CSV.

## GitHub Actions

The workflow automatically builds a Windows standalone EXE using PyInstaller. It runs on push to `main` and can be started manually from the Actions tab.
