# Singleton for Grid Structure (including households)
import os
import numpy as np
import networkx as nx
import math
import cmath
import copy
import csv

from Messages import *

bDebug = False

class GridStructure:    

    # class variables    
    name = ""
    ## 
    b_Initialized = False    

    ## grid structure
    BS = []   # a.k.a V, list of BS (id only, string type)
    # BR = {}  # a.k.a E, dic of k: from BS, v: set of (from_BS, to_BS)    
    # BR_Z = {} # a.k.a weight on edges, dic of k: id, v: impedence of edges (3x3 matrix)
    # BR_id = {} # a.k.a E, dic of k: from BS, v: (from_BS, to_BS) 
    

    ## Household info
    HH_infos = {} # k: id, v: {LD, LD_P, LD_Q, DG_P, DG_Q, EV_P, EV_Q} --> household_info
    ESS_infos = {} # k: id, v: {LD, LD_P, LD_Q, DG_P, DG_Q, EV_P, EV_Q} --> household_info
    ## BR_info
    BR_infos = {} # k: id, v: BR_info    

    
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            print("Create instance")
            cls.instance =  super(GridStructure, cls).__new__(cls)
        return cls.instance    
    
    # initialize BS, BR, and BR_Z
    def initialize(self, config):

		# added by pietrok for reset class variables

        GridStructure.b_Initialized = False
        GridStructure.BS = []
        GridStructure.HH_infos = {}
        GridStructure.ESS_infos = {}
        GridStructure.BR_infos = {}
        GridStructure.name = ""
        # end of added

        self.result_dir = config.getConfiguration('result_dir')
        # result containers
        self.result_LDV =[]
        self.result_P_Loss =[]
        self.result_TR_S =[]
        self.result_TR_P =[]
        self.result_TR_Q =[]
        self.result_TR_I =[]
        self.result_UnstalbeRatio =[]
        self.result_PowerImbalance =[]


        if GridStructure.b_Initialized == False:
           GridStructure.b_Initialized = True
           GridStructure.name = "GridStructure"
        else:
            print("%s is Already Initialized" % GridStructure.name)
            return
        
        #v_slack = 252.1866 # from IEEE 
        self.v_slack = float(config.getConfiguration('v_slack')) # from IEEE     
    
        # read files from MATALB code
        BR_data_directory = os.path.join(config.getConfiguration('data_dir'), config.getConfiguration('BR csv'))
        BS_data_directory = os.path.join(config.getConfiguration('data_dir'), config.getConfiguration('BS csv'))
        BR_Z_data_directory = os.path.join(config.getConfiguration('data_dir'), config.getConfiguration('BR_Z csv'))

        GridStructure.BS = np.loadtxt(BS_data_directory, skiprows=0, delimiter=',')        
        BR = np.loadtxt(BR_data_directory,skiprows=1,delimiter =',',dtype=int)
        BR_Z_temp = np.loadtxt(BR_Z_data_directory, skiprows=0, delimiter=',',dtype='str')
        ## need to be fixed later
        BR_Z_new = []
        for i in range(len(BR)):
            BR_Z_new.append(BR_Z_temp[:,3*i:3*(i+1)])
        BR_Z_new = np.asarray(BR_Z_new,dtype=str)

        # storing BR_info (including BR and BR_Z) to GridStructure.BR_infos
        for i in range(len(BR)):
            if bDebug:
                print("ID of BRs: %d" % i)
            temp_br = BR[i] # read pandas
            temp_br_z = BR_Z_new[i]
            temp_br_info = BR_info(i, temp_br[0], temp_br[1], BR_Z_new[i])
            #temp_br_info.toString()
            GridStructure.BR_infos[i]=temp_br_info
        
        # make layer data
        self.make_layer_data()

        #define the stable range
        if self.v_slack == 220:
            self.lb_voltage = 207
            self.ub_voltage = 233
        else:
            self.lb_voltage = self.v_slack * 0.9
            self.ub_voltage = self.v_slack * 1.1
        
        #temporary: test householder ids
        self.ids = np.arange(55)
        self.generateOutputFiles()
    


    def generateOutputFiles(self):
        
        # LD_V files
        for id in self.ids:
            filename = os.path.join(self.result_dir, "LDV_" + str(id) + ".csv")
            #filename = "LDV_" + str(id) + ".csv"
            with open(filename, "w", encoding="utf-8",newline='') as ofile:
                ofile.write("time,voltage\n")
        
        # P_loss
        filename = os.path.join(self.result_dir, "P_Loss.csv")            
        with open(filename,'w',encoding='utf-8',newline='') as ofile:
            ofile.write("time,p_loss\n")
        
        # Voltage_Unstable_Ratio.csv
        filename = os.path.join(self.result_dir, "Voltage_Unstable_Ratio.csv") 
        with open(filename,'w',encoding='utf-8',newline='') as ofile:
            ofile.write("time,unstable_ratio\n")
        
        # Power_Imbalance.csv
        filename = os.path.join(self.result_dir, "Power_Imbalance.csv")         
        with open(filename,'w',encoding='utf-8',newline='') as ofile:
            ofile.write("time,power_imbalance\n")               

        # TR_I
        filename = os.path.join(self.result_dir, "TR_P.csv")                 
        with open(filename,'w',encoding='utf-8',newline='') as ofile:
            ofile.write("time,phase1,phase2,phase3\n")

        # TR_S
        filename = os.path.join(self.result_dir, "TR_S.csv")                         
        with open(filename,'w',encoding='utf-8',newline='') as ofile:
            ofile.write("time,phase1,phase2,phase3\n")
        
        # TR_P
        filename = os.path.join(self.result_dir, "TR_P.csv")                                 
        with open(filename,'w',encoding='utf-8',newline='') as ofile:
            ofile.write("time,phase1,phase2,phase3\n")
        
        # TR_Q
        filename = os.path.join(self.result_dir, "TR_Q.csv")                                         
        with open(filename,'w',encoding='utf-8',newline='') as ofile:
            ofile.write("time,phase1,phase2,phase3\n")     

    # ister Household at gridstructure
    def registerHousehold(self, hh_info):
        GridStructure.HH_infos[hh_info.id] = hh_info

    # register ESS at gridstructure
    def registerESS(self, ess_info):
        GridStructure.ESS_infos[ess_info.id] = ess_info
        
    def printGridStructure(self):
        #print BS
        print("BS info: Number of BS is %d" % len(GridStructure.BS))
        for bs in GridStructure.BS:
            print("BS ID: %s" % bs)

        #print BR
        print("BR info: Number of BR is %d" % len(GridStructure.BR_infos))
        for id, brinfo in GridStructure.BR_infos.items():
            print("BR ID: %s" % id)
            print("fromBS: %s, toBS: %s, BR_Z: %s"%(brinfo.fromBS, brinfo.toBS, brinfo.Z))
    
    def printHHinfos(self):
        #print HH
        print("Household info: Number of Households is %d " % len(GridStructure.HH_infos))
        for id, hhinfo in GridStructure.HH_infos.items():
            print("HH ID: %s" % id)
            print("ConnectedBS: %s, phase: %s, LD_P: %s, LD_Q: %s, DG_P: %s, DG_Q: %s, EV_P: %s, EV_Q: %s"%(hhinfo.BS, hhinfo.phase, hhinfo.LD_P, hhinfo.LD_Q, hhinfo.DG_P, hhinfo.DG_Q, hhinfo.EV_P, hhinfo.EV_Q))
    
    def printESSinfos(self):
        #print ESS
        print("ESS info: Number of ESS is %d " % len(GridStructure.ESS_infos))
        for id, essinfo in GridStructure.ESS_infos.items():
            print("ESS ID: %s" % id)
            print("ConnectedBS: %s, phase: %s, Power(W): %s, Efficiency(%): %s, Nominal Voltage (V): %s, Capcaity (Wh): %s, charge_starttime(min): %s, charge_endtime(min): %s"%(essinfo.LD, essinfo.LD_num, essinfo.power, essinfo.efficiency, essinfo.v, essinfo.capacity, essinfo.start, essinfo.end))

    # functions for calculating the metrics (from MATLAB)
    def analyzePowerFlow(self):
        
        # Start analyzing
        # 앞부분은 household, 뒤에는 ESS
        Sinj = np.zeros((len(GridStructure.HH_infos)+len(GridStructure.ESS_infos), 3), dtype='complex128')
        # household
        for hhinfo in GridStructure.HH_infos.values():
            Sinj[int(hhinfo.id)][0] = hhinfo.BS # connectedBS
            Sinj[int(hhinfo.id)][1] = hhinfo.phase # phase
            # if hhinfo.ESS_P == -1:
            #     Sinj[int(hhinfo.id)][2] = -(hhinfo.LD_P + 1j * hhinfo.LD_Q)
            # else:
            # no ESS --> ESS_P = 0 
            Sinj[int(hhinfo.id)][2] = -(hhinfo.LD_P + 1j * hhinfo.LD_Q)

        # ESS power is added to household_LD (need modification later)
        num_ESS=len(GridStructure.ESS_infos)
        for essinfo in GridStructure.ESS_infos.values(): 
            if not essinfo.Household == -1: # if ess is involved in hh
                hh_info = self.HH_infos.get(int(essinfo.Household))
                hh_info.ESS_P = essinfo.currentP
                Sinj[int(hhinfo.id)][2]-=hhinfo.ESS_P
                num_ESS-=1

            else: # independent ESS
                Sinj[len(GridStructure.HH_infos)+int(essinfo.id)][0] = essinfo.LD # connected BS
                Sinj[len(GridStructure.HH_infos)+int(essinfo.id)][1] = essinfo.LD_num # phase
                Sinj[len(GridStructure.HH_infos)+int(essinfo.id)][2] = -essinfo.power

        tol_max = 0.001
        iter_max = 500

        bs_num = len(GridStructure.BS)
        br_num = len(GridStructure.BR_infos)
        ld_num = len(GridStructure.HH_infos)+num_ESS

        #변수 초기화
        I_inj = np.zeros((3,bs_num),dtype='complex128')
        I_flow = np.zeros((3,br_num),dtype='complex128')       

        #변수 V를 슬랙 모선의 전압 기준으로 최소화 (V initialization)
        V = np.zeros((3,bs_num),dtype='complex128')
        t_B = -120/180*math.pi
        t_C = 120/180*math.pi

        V_slack_a = self.v_slack
        V_slack_b = self.v_slack * cmath.exp(complex(0,1)* t_B)
        V_slack_c = self.v_slack * cmath.exp(complex(0,1)* t_C)


        for bs_index in range(bs_num):
            V[0,bs_index] = V_slack_a
            V[1,bs_index] = V_slack_b
            V[2,bs_index] = V_slack_c
        
        #power flow start
        iter_num_pf = 0

        while True:
            iter_num_pf = iter_num_pf + 1

            #모선 유입 전류 계산 : 부한 연계점의 전압을 통해 유입 전류를 구함.
            for ld_index in range(ld_num):
                #부하 연결 모선#
                bs_index = Sinj[ld_index,0]
                #부하 연결 상#
                phase_index = Sinj[ld_index,1]
                #부하 연계점의 상 전압#
                V_p = np.asarray(V[int(phase_index)-1,int(bs_index)-1],dtype='complex128')
                #모선 유입 전류#
                I_inj[int(phase_index)-1,int(bs_index)-1] = np.asarray((Sinj[ld_index, 2]/V_p).conjugate(),dtype='complex128')


            #Backward Sweep
            for target_index in range(br_num):
                br_index = self.bw_order[target_index]-1
                #bs_index = BR_dic[br_index][2]  # need to be checked
                bs_index = GridStructure.BR_infos[br_index].toBS # need to be checked
                # print(bs_index)
                I_flow[:,br_index] = - I_inj[:,bs_index-1]
                down_br_num = 0
                down_br_index = self.down_br[br_index,down_br_num]
                while (down_br_index != 0):
                    I_flow[:,br_index] = I_flow[:,br_index] + I_flow[:,int(down_br_index)-1]
                    down_br_num = down_br_num+1
                    down_br_index = self.down_br[br_index,down_br_num]
            
            #Forward Sweep#
            del_Vmax = 0
            for target_index in range(br_num):
                br_index = self.fw_order[target_index]-1
                #fbs = BR_dic[br_index][1]
                fbs = GridStructure.BR_infos[br_index].fromBS
                #tbs = BR_dic[br_index][2]
                tbs = GridStructure.BR_infos[br_index].toBS
                V0 = copy.deepcopy(V[:,tbs-1])
                X = np.empty((3,3), dtype='complex128')
                for i in range(3):
                    for j in range(3):
                        a = GridStructure.BR_infos[br_index].Z[i][j]
                        a = a.replace('i','j')
                        b = I_flow[:,br_index][j]
                        X[i,j] = complex(''.join(a.split()))*complex(b)

                X = np.sum(X, axis=1)
                V[:,tbs-1] = V[:,fbs-1 ] - X
                del_Vmax = max(del_Vmax,max(abs(V0-V[:,tbs-1])))

            if del_Vmax < tol_max:
                #모선 전압 및 OLTC/SVR 출력 전력 저장#
                pf_flag = 1
                break

            if iter_num_pf >= iter_max:
                pf_flag = -1
                break

        return I_flow, V,Sinj, pf_flag

    def make_layer_data(self):
        # generate BRdata
        BRdata = []

        for brinfo in self.BR_infos.values():
            temp = []
            temp.append(brinfo.fromBS)
            temp.append(brinfo.toBS)
            BRdata.append(temp)

        slack_bs = 1
        # br_num = BRdata.shape[0]
        br_num = len(BRdata)
        #print(br_num)
        G = nx.Graph()

        for i in range(br_num):
            #print(i)
            G.add_node(BRdata[i][0])
            G.add_node(BRdata[i][1])
            G.add_edge(BRdata[i][0], BRdata[i][1])

        br_layer = np.zeros(br_num)
        for br_index in range(br_num):
            fbs = BRdata[br_index][0]
            tbs = BRdata[br_index][1]
            if nx.shortest_path_length(G, source=fbs, target=slack_bs) > nx.shortest_path_length(G, source=tbs,target=slack_bs):
                BRdata[br_index][0] = tbs
                BRdata[br_index][1] = fbs
            br_layer[br_index] = nx.shortest_path_length(G, source=BRdata[br_index][1], target=slack_bs)

        fw_order = []
        for indexnum in range(1, int(np.max(br_layer)) + 1):
            temp = np.argwhere(br_layer == indexnum)
            for tmpi in range(len(temp)):
                fw_order.append(temp[tmpi][0] + 1)

        bw_order = []
        for indexnum in range(1, int(np.max(br_layer)) + 1):
            temp = np.argwhere(br_layer == int(np.max(br_layer)) + 1 - indexnum)
            for tmpi in range(len(temp)):
                bw_order.append(temp[tmpi][0] + 1)

        down_br = np.zeros((br_num, 10))
        for br_index in range(br_num):
            layer_index = int(br_layer[br_index])
            temp = np.argwhere(br_layer == layer_index + 1)
            templist = []
            for tmpi in range(len(temp)):
                templist.append(temp[tmpi][0] + 1)
            if len(templist) > 0:
                down_br_num = -1
                for index in range(len(templist)):
                    if BRdata[br_index][1] == BRdata[int(temp[index])][0]:
                        down_br_num = down_br_num + 1
                        down_br[br_index][down_br_num] = templist[index]

                        # store as local variables
        self.fw_order = fw_order
        self.bw_order = bw_order
        self.down_br = down_br

        return


        # using methods from MATLAB code
    def calculateHouseholdVoltage(self, V):
        LD_V = []
        for hhinfo in GridStructure.HH_infos.values():
            # bs_index = LD_dic[ld_index][1]
            # phase_index = LD_dic[ld_index][2]
            LD_V.append(abs(V[int(hhinfo.phase)-1,int(hhinfo.BS)-1]))
        self.current_LD_V = LD_V
        return
    
    # using methods from MATLAB code
    def calculateTransformerPower(self, I_flow, V, Sinj):
        self.current_TR_S = V[:, 0] * (I_flow[:, 0].conjugate())
        self.current_TR_P = self.current_TR_S.real
        self.current_TR_Q = self.current_TR_S.imag 
        self.current_p_loss = sum(self.current_TR_P) + sum(Sinj[:, 2]).real
        return

    # using methods from MATLAB code
    def calculateTransformerCurrent(self, I_flow):
        self.current_TR_I = abs(I_flow[:,0])
        return

    ## need to be modified
    # define a metric for voltage stability
    def check_stability_voltage(self):
        unstable_num = 0 
        customer_list=[]

        for customer_id in range(len(self.current_LD_V)): # customer별로
           if self.current_LD_V[customer_id]>self.ub_voltage or self.current_LD_V[customer_id] < self.lb_voltage: # voltage가 안정적이지 않다
               unstable_num+=1
               customer_list.append('Unstable')
           else: # voltage variation이 범위 이내
               customer_list.append('Stable')

        self.unstable_voltage_ratio = 100*unstable_num/len(self.current_LD_V) # %
        return customer_list, self.unstable_voltage_ratio

    def check_stability_power(self):
        self.power=np.sqrt(self.current_TR_P**2+self.current_TR_Q**2)
        max_power = max(self.power)
        min_power = min(self.power)

        self.power_imbalance=100*(max_power-min_power)/(np.sum(self.power)/3)
        
        return 

    # store results 
    def storeResults(self):
        #LD_V
        ldv = []
        for id in self.ids:
            ldv.append(self.current_LD_V[id])

        self.result_LDV.append(ldv)    
        self.result_TR_I.append(self.current_TR_I)
        self.result_TR_P.append(self.current_TR_P)
        self.result_TR_Q.append(self.current_TR_Q)
        self.result_TR_S.append(self.current_TR_S)        

        self.result_P_Loss.append(self.current_p_loss)
        self.result_PowerImbalance.append(self.power_imbalance)
        self.result_UnstalbeRatio.append(self.unstable_voltage_ratio)

    # write results at every tick
    def writeResults(self, cur_time):
        #write LD_V        
        self.writeLD_V(cur_time)
        #write current_p_loss
        self.writeCurrent_P_Loss(cur_time)
        #write current_TR_S
        self.writeCurrent_TR_S(cur_time)
        #write current_TR_P
        self.writeCurrent_TR_P(cur_time)
        #write current_TR_Q
        self.writeCurrent_TR_Q(cur_time)        
        #write current_TR_I
        self.writeCurrent_TR_I(cur_time)        
        #write unstable_voltage_ratio
        self.writeUnstableRatio(cur_time)        
        #write power_imbalance
        self.writePowerImbalance(cur_time)

        self.writeEssEnergy(cur_time)

        # #write ESS charge
        # self.writeEssCharge(cur_time)
        # #write ESS discharge
        # self.writeEssDischarge(cur_time)
        # #write ESS total_energy
        # self.writeEssTotal(cur_time)

        return

    def writeCurrent_TR_P(self, cur_time):
        filename = os.path.join(self.result_dir, "TR_P.csv")
        #filename =  "TR_P.csv"
        with open(filename,'a',encoding='utf-8',newline='') as ofile:
            ofile.write("%s,"%cur_time)
            writer = csv.writer(ofile)
            writer.writerow(self.current_TR_P)            

    def writeCurrent_TR_Q(self, cur_time):
        filename = os.path.join(self.result_dir, "TR_Q.csv")        
        #filename = "TR_Q.csv"
        with open(filename,'a',encoding='utf-8',newline='') as ofile:
            ofile.write("%s,"%cur_time)
            writer = csv.writer(ofile)
            writer.writerow(self.current_TR_Q)  

    def writeCurrent_TR_I(self, cur_time):
        filename = os.path.join(self.result_dir, "TR_I.csv")
        #filename = "TR_I.csv"
        with open(filename,'a',encoding='utf-8',newline='') as ofile:
            ofile.write("%s,"%cur_time)
            writer = csv.writer(ofile)
            writer.writerow(self.current_TR_I)  

    def writeUnstableRatio(self, cur_time):
        filename = os.path.join(self.result_dir, "Voltage_Unstable_Ratio.csv")        
        #filename = "Voltage_Unstable_Ratio.csv"
        with open(filename,'a',encoding='utf-8',newline='') as ofile:
            ofile.write("%s,%s\n"%(cur_time, self.unstable_voltage_ratio))      
    
    def writePowerImbalance(self, cur_time):
        filename = os.path.join(self.result_dir, "Power_Imbalance.csv")                
        #filename = "Power_Imbalance.csv"
        with open(filename,'a',encoding='utf-8',newline='') as ofile:
            ofile.write("%s,%s\n"%(cur_time, self.power_imbalance))

    def writeLD_V(self, cur_time):
        for id in self.ids:            
            filename = os.path.join(self.result_dir, "LDV_" + str(id) + ".csv")                        
            #filename = "LDV_" + str(id) + ".csv"
            with open(filename,'a',encoding='utf-8',newline='') as ofile:
                ofile.write("%s,%s\n"%(cur_time, self.current_LD_V[id]))

    def writeCurrent_P_Loss(self, cur_time):
        filename = os.path.join(self.result_dir, "P_Loss.csv")                            
        #filename = "P_Loss.csv"
        with open(filename,'a',encoding='utf-8',newline='') as ofile:
            ofile.write("%s,%s\n"%(cur_time, self.current_p_loss))

    def writeCurrent_TR_S(self, cur_time):
        filename = os.path.join(self.result_dir, "TR_S.csv")                                    
        #filename = "TR_S.csv"
        with open(filename,'a',encoding='utf-8',newline='') as ofile:
            ofile.write("%s,"%cur_time)
            writer = csv.writer(ofile)
            writer.writerow(self.current_TR_S)  

    def writeEssCharge(self, cur_time):
        for id, essinfo in GridStructure.ESS_infos.items():
            filename = os.path.join('result', 'ESS_'+str(id) + '_'+  'charge' +".csv")
            with open(filename, 'a', encoding='utf-8', newline='') as ofile:
                if essinfo.currentP <= 0:
                    charge = 0
                else:
                    charge = (essinfo.currentP)/ 60 * float(essinfo.efficiency) * 0.01
                ofile.write("%s,%s\n" % (cur_time, charge))

    def writeEssDischarge(self, cur_time):
        for id, essinfo in GridStructure.ESS_infos.items():
            filename = os.path.join('result', 'ESS_'+str(id) + '_'+  'discharge' +".csv")
            with open(filename, 'a', encoding='utf-8', newline='') as ofile:
                if essinfo.currentP >= 0:
                    discharge = 0
                else:
                    discharge = -(essinfo.currentP) / 60
                ofile.write("%s,%s\n" % (cur_time, discharge))

    def writeEssTotal(self, cur_time):
        for id, essinfo in GridStructure.ESS_infos.items():
            filename = os.path.join('result', 'ESS_'+str(id) + '_'+  'total' +".csv")
            with open(filename, 'a', encoding='utf-8', newline='') as ofile:
                ofile.write("%s,%s\n" % (cur_time, essinfo.currentEnergy))

    def writeEssEnergy(self, cur_time):
        for id, essinfo in GridStructure.ESS_infos.items():
            filename = os.path.join('result', 'ESS_'+str(id) + '_'+  'totalE' +".csv")
            with open(filename, 'a', encoding='utf-8', newline='') as ofile:
                if essinfo.currentP < 0:
                    charge = 0
                    discharge = -(essinfo.currentP) / 60
                elif essinfo.currentP > 0:
                    discharge = 0
                    charge = (essinfo.currentP) / 60 * float(essinfo.efficiency) * 0.01
                else:
                    charge = 0
                    discharge = 0

                ofile.write("%s,%s,%s,%s\n" % (cur_time,charge,discharge,essinfo.currentEnergy))





    
        
        

        

        






    
        




