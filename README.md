# renko-demo 

# Reference
[chranga/renkocharts](https://github.com/chranga/renkocharts)
[renko1 - Google Colab](https://colab.research.google.com/drive/1qHq4sjCf8zodROUDrtYFYeMiX6AvwDQQ?usp=sharing)


# Conda related commads for this project

### create a new conda environment
conda create -n renko-chart-demo 

### activate environment
conda activate renko-chart-demo

### export configuration to a file
conda env export > renko-chart-demo.yml

### create a new conda environment from config file
conda env create  -f renko-chart-demo.yml