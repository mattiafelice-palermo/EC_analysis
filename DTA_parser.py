import pandas as pd
import numpy as np
import scipy.integrate as integrate
import matplotlib.pyplot as plt
import os

plt.rc('font', **{'style' : 'normal'}, size=22)

folder = "/home/luca/Downloads/"                                # Folder containing the data
cycles = []                                                     # Define the list containing all the cycles data
    
def read_DTA_files():
    
    cycle_num = 1

    # finding all files with the .DTA extension
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".DTA"):

            print("Loading: " + filename)
            path = os.path.join(folder, filename)

            if ("Charge" in filename):
                cycle_type = 0
            elif ("Discharge" in filename):
                cycle_type = 1                                              
        
            with open(path, "r") as file:
                
                beginning = None                                # line at which the table begins
                npoints = None                                  # number of data points
                cycle = [[], [], [], [], []]                    # [cycle number, half-cycle type, time, voltage, current]

                # finding the "CURVE TABLE npoints" line in file
                for line_num, line in enumerate(file):

                    buffer = line.split()
                 
                    if "CURVE" in line:
                        beginning = line_num + 2
                        npoints = int(buffer[2])+1
 
                    if cycle_type == 0:                              
                        if (beginning != None and beginning < line_num < beginning+npoints):
                            cycle[0].append(cycle_num)                           
                            cycle[1].append("Charge")                           
                            cycle[2].append(float(buffer[1]))   # time (s)
                            cycle[3].append(float(buffer[2]))   # voltage (V)
                            cycle[4].append(float(buffer[3]))   # current (A)
                                            
                    elif cycle_type == 1:                                
                        if (beginning != None and beginning < line_num < beginning+npoints):
                            cycle[0].append(cycle_num)                           
                            cycle[1].append("Discharge")                           
                            cycle[2].append(float(buffer[1]))   # time (s)
                            cycle[3].append(float(buffer[2]))   # voltage (V)
                            cycle[4].append(float(buffer[3]))   # current (A)
                
                if cycle_type == 1:
                    cycle_num += 1

                
                cycle_df = pd.DataFrame(
                    {
                        "Cycle number": cycle[0],
                        "Half-cycle": cycle[1],
                        "Time (s)": cycle[2],
                        "Voltage vs Ref. (V)": cycle[3],
                        "Current (A)": cycle[4]
                    }
                )
                                          
            cycles.append(cycle_df)

def read_mpt_files():

    cycle_num = 1
    half_cycle = 0

    # finding all files with the .mpt extension
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".mpt"):

            print("Loading: " + filename)
            path = os.path.join(folder, filename)

            with open(path, "r", encoding="utf8", errors="ignore") as file:

                delims=[]                                       # contains cycle number, first and last line number
                beginning = None
                cycle = [[], [], [], [], []]                    # [cycle number, half-cycle type, time, voltage, current]

                for line_num, line in enumerate(file):

                    buffer = line.split()
                
                    if "mode\t" in line:
                        beginning = line_num

                    if (beginning != None and line_num == beginning+1):
                        cycle_type = buffer[1]                  # should be 1 for charge and 0 for discharge (check!!)

                    if (beginning != None and line_num > beginning and buffer[1] == cycle_type):
                        cycle[0].append(cycle_num)                           
                        cycle[1].append(("Charge"))                                 
                        cycle[2].append(float(buffer[4].replace(',', '.')))       # time (s)
                        cycle[3].append(float(buffer[6].replace(',', '.')))       # voltage (V)
                        cycle[4].append(float(buffer[8].replace(',', '.'))/1000)  # current (A)
                        
                    
                    elif (beginning != None and line_num > beginning and buffer[1] != cycle_type):
                        cycle_type = buffer[1]
                        half_cycle += 1
                        cycle_num = half_cycle // 2 + 1
                        
                        cycle_df = pd.DataFrame(
                            {
                                "Cycle number": cycle[0],
                                "Half-cycle": cycle[1],
                                "Time (s)": cycle[2],
                                "Voltage vs Ref. (V)": cycle[3],
                                "Current (A)": cycle[4]
                            }
                        )
                        cycles.append(cycle_df)
                        cycle = [[], [], [], [], []]

                        cycle[0].append(cycle_num)                           
                        cycle[1].append("Discharge")                                 
                        cycle[2].append(float(buffer[4].replace(',', '.')))       # time (s)
                        cycle[3].append(float(buffer[6].replace(',', '.')))       # voltage (V)
                        cycle[4].append(float(buffer[8].replace(',', '.'))/1000)  # current (A)
                

def calculate_capacity(cycle):
    """
    Calculates the cell capacity within a cycle as:
    C = i x t
    Where C is the capacity of the cell in Coulombs, i is the total current in Ampères, and t is time in seconds.
    The total current is calculated by integrating (trapezoid method) the instantaneous current through time.
    """
    current = integrate.trapezoid(cycle["Current (A)"], cycle["Time (s)"])
    time = cycle["Time (s)"].iloc[-1] - cycle["Time (s)"].iloc[0]
    capacity = current * time

    print("\nCycle %d, %s" % (cycle["Cycle number"].iloc[0], cycle["Half-cycle"].iloc[0]))
    print("Total time: %d s" % time)
    print("Total current: %d A" % current)
    print("Capacity: %d C\n" % capacity)

    return capacity

def plot_voltage(cycle):

    cycle.plot(x = "Time (s)", y = "Voltage vs Ref. (V)", figsize = (12, 10), 
    title = "Cycle %d (%s)" % (cycle["Cycle number"][0], cycle["Half-cycle"][0]))
    
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage vs. Reference (V)")
    plt.grid(which='major', c="#DDDDDD")
    plt.grid(which='minor', c="#EEEEEE")
    plt.legend()
    plt.tight_layout()
    plt.show()      

def plot_current(cycle):

    cycle.plot(x = "Time (s)", y = "Current (A)", figsize = (12, 10), 
    title = "Cycle %d (%s)" % (cycle["Cycle number"][0], cycle["Half-cycle"][0]))
    
    plt.xlabel("Time (s)")
    plt.ylabel("Current (A)")
    plt.grid(which='major', c="#DDDDDD")
    plt.grid(which='minor', c="#EEEEEE")
    plt.legend()
    plt.tight_layout()
    plt.show()  

read_mpt_files()   
#read_DTA_files()

for i in range(10):
    calculate_capacity(cycles[i])
