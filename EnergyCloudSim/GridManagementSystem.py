from SimulationEngine.ClassicDEVS.DEVSCoupledModel import DEVSCoupledModel
from GridEvaluator import GridEvaluator
from StabilityManager import StabilityManager
from GridStructure import GridStructure

class GridManagementSystem(DEVSCoupledModel):
    def __init__(self, objConfiguration):
        super().__init__("GridManagementSystem")

        grid = GridStructure()
        grid.initialize(objConfiguration)

        # X, Y
        self.addOutputPort("end")

        # M
        evaluator = GridEvaluator("GridEvaluator")
        self.addModel(evaluator)

        stable_checker = StabilityManager("StabilityManager", objConfiguration)
        self.addModel(stable_checker)

        # EIC, EOC, IC
        self.addExternalOutputCoupling(stable_checker, "end", "end")
        self.addInternalCoupling(stable_checker,"end", evaluator,"end")
        self.addInternalCoupling(evaluator,"report", stable_checker, "report")

