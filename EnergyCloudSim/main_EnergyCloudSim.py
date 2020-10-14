from SimulationEngine.Utility.Configurator import Configurator
from SimulationEngine.SimulationEngine import SimulationEngine
from MicroGridSystem import MicroGridSystem
import csv

def readParameterFile(filename):
    config = Configurator()

    f = open(filename)
    rdr = csv.reader(f)
    for line in rdr:
        config.addConfiguration(line[0], line[1])
    
    f.close()
    return config

if __name__ == "__main__":    
    #read parameter file
    config = readParameterFile('SimParameters.csv')    

    microgrid = MicroGridSystem(config)
    engine = SimulationEngine()
    engine.setOutmostModel(microgrid)
    engine.run(logFileName="EnergyCloudSim_log.txt", maxTime=float(config.getConfiguration("end time")))