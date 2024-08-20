# Renko Chart Demo 


## Conda related commads

### create a new environment
conda create -n stock-charts-demo

### activate environment
conda activate stock-charts-demo

### export configuration to a file
conda env export > stock-charts-demo.yml

### create a new environment from config file
conda env create  -f requirements.yml


## PIP related commads

### create a new environment
windows: py -m venv .stock-charts-demo 
unix/macOS: python3 -m venv .stock-charts-demo

### activate environment
windows: .stock-charts-demo/bin/python 
unix/macOS: source .stock-charts-demo/bin/activate

### verify environment
windows: where python 
unix/macOS: which python

### install packagesfrom requirements.txt
pip install -r requirements. txt

### export configuration to a file
pip list --format=freeze > requirements.txt



## Reference
1. [chranga/renkocharts](https://github.com/chranga/renkocharts)
2. [renko1 - Google Colab](https://colab.research.google.com/drive/1qHq4sjCf8zodROUDrtYFYeMiX6AvwDQQ?usp=sharing)
3. [geek for geeks] (https://www.geeksforgeeks.org/how-to-create-a-candlestick-chart-in-matplotlib/)


[![built with Codeium](https://codeium.com/badges/main)](https://codeium.com)
