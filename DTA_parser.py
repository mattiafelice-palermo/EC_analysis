import numpy as np
import scipy.integrate as integrate
import matplotlib.pyplot as plt
import os

plt.rc('font', **{'style' : 'normal'}, size=22)

folder = "/home/luca/Downloads/"
cycles = []                                                 #Define the list containing all the cycles data
    
def read_DTA_files(folder):

    
    fig = plt.figure(figsize=(12, 10))

    # finding all files with the .DTA extension
    for filename in os.listdir(folder):
        if filename.endswith(".DTA"):

            print("Loading: " + filename)
            path = os.path.join(folder, filename)
            
            if ("Charge" in filename):
                tick = 0
                cycle = [[], [], []]                            # array containing the data (time, voltage, current)
                time_offset = float(0)
            else:
                tick = 1                                        # 0 for charge, 1 for discharge          
        
            with open(path, "r") as file:
                
                beginning = None                                # line at which the table begins
                npoints = None                                  # number of data points
                                
                # finding the "CURVE TABLE npoints" line in file
                for line_num, line in enumerate(file):

                    buffer = line.split()
                 
                    if "CURVE" in line:
                        beginning = line_num + 2
                        npoints = int(buffer[2])+1
                           
                    # start grabbing data
                    if (beginning != None and beginning < line_num < beginning+npoints):
                        cycle[0].append(float(buffer[1]) + time_offset)     # time (with offset for discharge)
                        cycle[1].append(float(buffer[2]))                   # voltage
                        cycle[2].append(float(buffer[3]))                   # current

                time_offset = cycle[0][-1]
                                           
            cycle.append(cycle)

            if tick == 1:
                cycles.append(cycle)
         
                                                                       
read_DTA_files(folder)   

for cycle_num, cycle in enumerate(cycles):

    plt.plot( cycle[0],cycle[1], linewidth=0.5, marker="o", markersize=1, label=("Cycle %d" % (cycle_num+1)))
    plt.xlabel("time (s)")
    plt.ylabel("Voltage vs Reference (V)")
    plt.grid(which='major', c="#DDDDDD")
    plt.grid(which='minor', c="#EEEEEE")
    plt.legend()
    plt.tight_layout()
    plt.show()   
   