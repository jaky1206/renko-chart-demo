# Stock Charts Demo
This project provides a demo for generating Stock charts.

## Table of Contents
- [Project Overview](#project-overview)
- [Installation](#installation)
  - [Using Conda](#using-conda)
  - [Using Pip](#using-pip)
- [References](#reference)

## Project Overview
Charts used
- Renko
- Candlestick

## Installation

### Using Conda
To get started with this project using Conda, follow the steps below:

- **Create a new environment:**
   ```bash
   conda create -n stock-charts-demo
   ```
- **Activate the environment:**
   ```bash
   conda activate stock-charts-demo
   ```
- **Install the required dependencies:**
  After activating the environment, you can install the required packages:
  ```bash
  conda env create -f requirements.yml
  ```
- **Export your environment configuration:**
  If you need to share or replicate your environment, you can export it:
  ```bash
  conda env export > requirements.yml
   ```
- **Remove the environment:**
  If you need to clean up, you can remove the environment:
   ```bash
   conda env remove --name stock-charts-demo
   ```

### Using Pip
Alternatively, you can use pip to set up the environment:

- **Create a new virtual environment:**
  - **Windows:**
    ```powershell
    py -m venv .stock-charts-demo
    ```
  - **Unix/macOS:**
    ```bash
    python3 -m venv .stock-charts-demo
    ```
- **Activate the environment:**
  - **Windows:**
    ```powershell
    .stock-charts-demo\Scripts\activate
    ```
  - **Unix/macOS:**
    ```bash
    source .stock-charts-demo/bin/activate
    ```
- **Verify the environment:**
  - **Windows:**
    ```powershell
    where python
    ```
  - **Unix/macOS:**
    ```bash
    which python
    ```
- **Install required packages:**
  ```bash
  pip install -r requirements.txt
  ```
- **Export installed packages:**
  To export the installed packages to a file:
  ```bash
   pip list --format=freeze > requirements.txt
  ```

## Reference
1. [Rrenkocharts project on chranga's github account.](https://github.com/chranga/renkocharts)
2. [Renko Chart Demo on Google Colab.](https://colab.research.google.com/drive/1qHq4sjCf8zodROUDrtYFYeMiX6AvwDQQ?usp=sharing)
3. [How to Create a Candlestick Chart in Matplotlib - A tutorial from GeeksforGeeks on creating financial charts using matplotlib.](https://www.geeksforgeeks.org/how-to-create-a-candlestick-chart-in-matplotlib)

##
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black)

##
[![Codeium](https://codeium.com/badges/main)](https://codeium.com)

