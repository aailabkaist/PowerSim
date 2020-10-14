# Class Information
class Household_info:
    def __init__(self, h_id, LD):
        self.id = h_id
        self.BS = LD[0]
        self.phase = LD[1]
        self.LD = LD              # unit: W
        self.LD_P = -1   
        self.LD_Q = -1
        self.DG_P = -1
        self.DG_Q = -1
        self.EV_P = -1
        self.EV_Q = -1
        self.ESS_P = -1
    
    def toString(self):
        print("Household_%s Information: "% self.id)
        print("connectedBS: %s"% self.BS)
        print("connctedPhase: %s" % self.phase)
        print("Current Active Power (LD_P): %s" % self.LD_P)
        print("Current Reactive Power(LD_Q): %s" % self.LD_Q)
        print("Current DG Active Power (DG_P): %s" % self.DG_P)
        print("Current DG Reactive Power(DG_Q): %s" % self.DG_Q)
        print("Current EV Active Power (EV_P): %s" % self.EV_P)
        print("Current EV Reactive Power(EV_Q): %s" % self.EV_Q)
        print("Current ESS Active Power(ESS_P): %s" % self.ESS_P)

class ESS_info:
    def __init__(self, ess_id, LD,LD_num,Household, charge_P, efficiency, nominal_V, capacity, charge_starttime, charge_endtime):
        # relations in gridnetwork
        self.id = ess_id    
        self.LD = int(LD) # BS 
        self.LD_num= int(LD_num) # phase
        self.Household = int(Household)

        # ESS spec.
        self.efficiency = efficiency    # unit: %
        self.power = float(charge_P)     # unit: W
        self.nominal_voltage = nominal_V    # unit: V
        self.capacity = capacity    # unit: Wh

        # ESS Operations
        self.charge_start = charge_starttime    # unit: min        
        self.charge_end = charge_endtime    #unit: min        

        # ESS Physical state
        self.currentEnergy = 0
        self.currentP = 0

    def toString(self):
        print("ESS_%s Information: "% self.id)
        print("ESS LD: %s" % self.LD)
        print("ESS phase: %s" % self.LD_num)
        print("ESS Efficienct (%): %s" % self.efficiency)
        print("ESS Power (W): %s" % self.power)
        print("ESS Nominal Voltage: %s" % self.nominal_voltage)
        print("ESS Capacity (Wh): %s" % self.capacity)
        print("ESS Charging Start Time (min): %s" % self.charge_start)
        print("ESS Charging End Time (min): %s" % self.charge_end)        

        
class BR_info:
    def __init__(self, id, fromBS, toBS, Z):
        self.id = id
        self.fromBS = fromBS
        self.toBS = toBS
        self.Z = Z
    
    def toString(self):
        print("BR_%s Information: "% self.id)
        print("fromBS: %s"% self.fromBS)
        print("toBS: %s"% self.toBS)
        print("impedence: %s"% self.Z)        


# Event Messages
class ReportMsg:
    def __init__(self):
        self.name = "report message"

class EndMsg:
    def __init__(self):
        self.name = "end message"

