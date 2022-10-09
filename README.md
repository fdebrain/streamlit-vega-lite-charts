# Streamlit Vega-Lite Charts

[Try the Online Demo](https://fdebrain-streamlit-vega-lite-charts-app-yjdqk5.streamlitapp.com/)

Explore tabular datasets using Streamlit and Vega-Lite.

## Requirements

Python 3.10

Poetry

## Installation

**Install dependencies:** `make install`

## Run the app

**Run Streamlit app:** `make run` (localhost:8501)

## Check code quality

We use Black, Flake8 and isort to ensure standard coding practices.

Each commit and pull request triggers a CI (Continuous Integration) pipeline job that runs code quality checks remotely (see Github Actions).

**(Optional) Run linters locally: pre-commit run -a**

## Features

- [x] Select one of 5 datasets from OpenML
- [x] Detecting continuous & categorical columns
- [x] Generate bar, histogram, timeseries, boxplot, scatter plots
- [ ] Detecting datetime columns
- [ ] Line, circular plots
- [ ] Upload custom dataset

## Contributing
To learn more about making a contribution to this repository, please see our [Contributing guide](https://github.com/fdebrain/streamlit-vega-lite-charts/blob/main/CONTRIBUTING.md).
