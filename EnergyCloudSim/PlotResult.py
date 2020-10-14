

import numpy as np
import random
import math
import matplotlib.pyplot as plt
import csv

def plot_result(filename):
    directory = 'result/'+ filename
    data_list = []
    with open(directory) as csvfile:
        reader = csv.reader(csvfile,delimiter=',')
        if 'LDV' in filename:
            pass
        else:
            next(reader)
        for row in reader:
            data_list.append(row)
    csvfile.close()
    data_list = np.array(data_list,dtype=np.float32)
    plt.plot(data_list[:,0],data_list[:,1])
    plt.grid()
    plt.title(filename[:-4])
    plt.savefig('plot_result/'+filename[:-4])
    plt.close()

plot_result('Power_Imbalance.csv')
plot_result('P_Loss.csv')
plot_result('ESS_1_charge.csv')
plot_result('ESS_1_discharge.csv')
plot_result('ESS_1_total.csv')


# id_list = [0,31,52]#np.arange(53)
# for id in id_list:
#     plot_result('LDV_'+str(id)+'.csv')


        
