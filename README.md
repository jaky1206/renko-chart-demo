# Renko Chart Demo 


## Conda related commads

### create a new environment
conda create -n renko-chart-demo 

### activate environment
conda activate renko-chart-demo

### export configuration to a file
conda env export > renko-chart-demo.yml

### create a new environment from config file
conda env create  -f renko-chart-demo.yml


## PIP related commads

### create a new environment
windows: py -m venv .venv 
unix/macOS: python3 -m venv .renko-chart-demo

### activate environment
windows: .venv/bin/python 
unix/macOS: source .venv/bin/activate

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