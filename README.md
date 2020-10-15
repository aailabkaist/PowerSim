# PowerflowSimulation with Visualizer

This is a simulation program that computes the voltage of the busbar and the current of the line, 
and analyzes the loss power and the unbalance rate for a small-scale power system.

## Environments for Simulation
```shell script
csv
cmath
networkX
xlrd
pandas
```
Please install required packages through ``` python -m pip install xxx ``` in EnergyCloudSim folder.

## Run Simulation
We provide guidance document ''' EnergyCloudSim Manual.docx '''.

Related hyperparameters are in SimParameters.csv. 
Configuration can be controlled SimParameters.csv.

Run with the following script:

```python main_EnergyCloudSim.py```


## Environments for Visualizer
```shell script
certifi==2020.6.20
cycler==0.10.0
decorator==4.4.2
kiwisolver==1.1.0
matplotlib==3.0.3
networkx==2.4
numpy==1.18.0
Pillow==7.2.0
pyparsing==2.4.7
PyQt5==5.15.0
PyQt5-sip==12.8.1
python-dateutil==2.8.1
scipy==1.4.1
six==1.15.0
```
Please install required packages through ``` python -m pip install -r requirements.txt ``` in Visualizer folder.


## Run Visualizer
We provide guidance document ''' EnergyCloudSim Visualizer Manual.docx '''.

Run with the following script:

```python Visualizer.py``` in Visualizer folder.

