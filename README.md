# Femap API Python

Python automation utilities for interacting with Siemens Femap through its COM API. This project provides scripts to connect to a running Femap session, create materials and layups, calculate element distances from model edges, and assign properties to elements based on a layup definition workbook.

## Overview

This repository is aimed at automating common Femap tasks from Python, especially for composite model setup workflows. The primary workflow is:

1. Connect to an active Femap model
2. Select model boundary nodes (leading edge, trailing edge, root)
3. Read a layup definition from Excel
4. Create materials and layups in Femap
5. Assign properties to elements based on their distance from selected boundaries

## Project structure

- `base/make_py.py`  
  Generates a Python wrapper for the Femap type library using `makepy`.

- `base/test.py`  
  Simple connection test to confirm the Femap COM API is available.

- `src/create_model/main.py`  
  Main workflow for building model properties and assigning them to elements.

- `src/create_model/get_elem_dist_from_edge.py`  
  Computes element distances relative to selected boundary sets.

- `src/composites/`  
  Scripts for composite property generation and fatigue-related outputs.

- `src/utils.py`  
  Shared utility functions.

- `requirements.txt`  
  Python dependencies for the project.

## Requirements

- Windows
- Siemens Femap installed on the machine
- Python 3.9+ recommended
- A running Femap session before executing automation scripts

## Setup

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
pip install -r requirements.txt
```

## Generate the Femap Python wrapper

If you need to generate the Python wrapper for the Femap type library:

```powershell
python .\base\make_py.py
```

This creates a generated file in the `base` folder for the Femap COM object model. If you have created a venv, copy this file into the `scripts` folder of the venv.

## Running the scripts

The scripts are intended to run while Femap is open and a model is loaded.

### Connectivity check

```powershell
python .\src\test.py
```

This should print a success message confirming the connection to Femap.

### Main model setup workflow

```powershell
python -m src.create_model.main
```

The script will:

- Prompt the user to select nodes on the leading edge, trailing edge, and root
- Open a file dialog for the layup Excel workbook. An example of the format for this is found in .\examples\create_model
- Create materials and layups in the active Femap model
- Assign those properties to elements based on distance boundaries

## Data input

The main workflow expects a layup definition in Excel format and uses columns similar to:

- `Material`
- thickness / ply thickness values
- boundary offsets for leading edge, trailing edge, and root regions

The exact schema depends on how the workflow is implemented in the scripts, so confirm the column names before running the model generation process.

## Important notes

- These scripts use the Femap COM API, so they require a live Femap application session.
- Most automation is Windows-specific because it relies on `pywin32` and the Femap COM interface.
- The repository is focused on engineering/model automation rather than a generic Python package.
