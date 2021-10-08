import numpy as np
import scipy.integrate as integrate
import matplotlib.pyplot as plt
import os

plt.rc('font', **{'style' : 'normal'}, size=22)

folder = "/home/ppravatto/Scrivania/LucaParser"
         
def read_DTA_files(folder):

    cycles = []                                                 #Define the list containing all the cycles data
    
    fig = plt.figure(figsize=(12, 10))

    # finding all files with the .DTA extension
    for filename in os.listdir(folder):
        if filename.endswith(".DTA"):

            print("Loading: " + filename)
            path = os.path.join(folder, filename)

            cycle = [[], [], []]                                # array containing the data (time, voltage, current)
            tick = 0 if ("Charge" in filename) else 1           # 0 for charge, 1 for discharge   
        
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
                        for field in range(3):
                            cycle[field].append(float(buffer[field+1]))
                        

            plt.plot( cycle[0],cycle[1], linewidth=0.5, marker="o", markersize=1, label=("Charge" if tick==0 else "Discharge"))
            cycles.append(cycle)
    
    plt.xlabel("time (s)")
    plt.ylabel("Voltage vs Reference (V)")
    plt.grid(which='major', c="#DDDDDD")
    plt.grid(which='minor', c="#EEEEEE")
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    
                                                                       
read_DTA_files(folder)            
   