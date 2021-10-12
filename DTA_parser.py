from dataclasses import dataclass
import pandas as pd
import numpy as np
import scipy.integrate as integrate
import matplotlib.pyplot as plt
import os

plt.rc('font', **{'style' : 'normal'}, size=22)

folder = os.getcwd()        # Folder containing the data (assumes it's where the script is located)
cycles = []                 # Define the list containing all the cycles data

@dataclass
class halfcycle:
    """
    Contains the charge and discharge half-cycles
    """
    time: pd.core.frame.DataFrame
    voltage: pd.core.frame.DataFrame 
    current: pd.core.frame.DataFrame

    def plot_voltage(self):

        plt.plot(self.time, self.voltage, linewidth=0.5, marker="o", markersize=1, )

        plt.xlabel("Time (s)")
        plt.ylabel("Voltage vs. Reference (V)")
        plt.grid(which='major', c="#DDDDDD")
        plt.grid(which='minor', c="#EEEEEE")
        plt.legend()
        plt.tight_layout()
        plt.show()      

    def plot_current(self):

        plt.plot(self.time, self.current, linewidth=0.5, marker="o", markersize=1, )

        plt.xlabel("Time (s)")
        plt.ylabel("Current (A)")
        plt.grid(which='major', c="#DDDDDD")
        plt.grid(which='minor', c="#EEEEEE")
        plt.legend()
        plt.tight_layout()
        plt.show()  

class cycle:
    """
    Contains the charge and discharge half-cycles
    """
    def __init__(self):
        self.charge = None
        self.discharge = None

    def add_charge(self, charge):
        self.charge = charge

    def add_discharge(self, discharge):
        self.discharge = discharge


def read_DTA_files():
    
    cycle_num = 0

    # finding all files with the .DTA extension
    for filename in sorted(os.listdir(folder)):

        if filename.endswith(".DTA"):

            print("Loading: " + filename)
            path = os.path.join(folder, filename)                                             
        
            with open(path, "r") as file:
                
                beginning = None    # line at which the table begins
                npoints = None      # number of data points
                cycle_type = None   # 1 for charge, 0 for discharge

                # finding the "CURVE TABLE npoints" line in file
                for line_num, line in enumerate(file):
                    
                    if "Step 1 Current (A)" in line:
                        if float(line.split()[2]) > 0:
                            cycle_type = 1  # positive current = charge
                        elif float(line.split()[2]) < 0:
                            cycle_type = 0  # negative current = discharge

                    if "CURVE" in line:
                        beginning = line_num + 2
                        npoints = int(line.split()[-1])
                        break
              
                # reading data from file
                data = pd.read_table(
                        path, delimiter = '\t', skiprows=beginning, decimal=".", nrows=npoints
                )

                # renaming columns to standard format
                data.rename(
                    columns={
                        's': 'Time (s)', 
                        'V vs. Ref.': 'Voltage vs. Ref. (V)',
                        'A': 'Current (A)'
                    }, inplace=True
                )
                
                if cycle_type == 1:
                    cyc = cycle()
                    charge = halfcycle(
                        data['Time (s)'],
                        data['Voltage vs. Ref. (V)'],
                        data['Current (A)']
                    )
                    cyc.add_charge(charge)

                elif cycle_type == 0:
                    discharge = halfcycle(
                        data['Time (s)'],
                        data['Voltage vs. Ref. (V)'],
                        data['Current (A)']
                    )
                    cyc.add_discharge(discharge)
                    cycles.append(cyc)
               
                                         
def read_mpt_files():

    # finding all files with the .mpt extension
    for filename in sorted(os.listdir(folder)):
      
        if filename.endswith(".mpt"):

            print("Loading: " + filename)
            path = os.path.join(folder, filename)

            with open(path, "r", encoding="utf8", errors="ignore") as file:

                delims=[]   # contains cycle number, first and last line number
                beginning = None

                for line_num, line in enumerate(file):
                    if "Number of loops : " in line:
                        ncycles = int(line.split(" ")[-1])

                    # Before the output of the experiment, EClab lists the starting
                    # and ending line of each loop. These will be used to slice
                    # the pandas dataframe into the different cycles.
                    if "Loop " in line:
                        loop_num = int(line.split(" ")[1])
                        first_pos = int(line.split(" ")[-3])
                        second_pos = int(line.split(" ")[-1])
                        delims.append([loop_num, first_pos, second_pos])

                    if "mode\t" in line:
                        beginning = line_num
                        break

                # reading data from file    
                data = pd.read_table(
                        path, dtype=np.float64, delimiter = '\t', skiprows=beginning, decimal=","
                )

                # renaming columns to standard format
                data.rename(
                    columns={
                        'time/s': 'Time (s)', 
                        'Ewe/V': 'Voltage vs. Ref. (V)',
                        'I/mA': 'Current (A)'      # note: these are mA
                    }, inplace=True
                )  

                data['Current (A)'] = data['Current (A)'].divide(1000)    # convert mA to A

                cycle_num = 0

                # initiate Cycle object providing dataframe view within delims
                while cycle_num < ncycles:
                    first_row = delims[cycle_num][1]
                    last_row = delims[cycle_num][2]
                    
                    charge = halfcycle(
                        data['Time (s)'][first_row:last_row][data['ox/red'] == 1],
                        data['Voltage vs. Ref. (V)'][first_row:last_row][data['ox/red'] == 1],
                        data['Current (A)'][first_row:last_row][data['ox/red'] == 1]
                    )
                    
                    discharge = halfcycle(
                        data['Time (s)'][first_row:last_row][data["ox/red"] == 0],
                        data['Voltage vs. Ref. (V)'][first_row:last_row][data['ox/red'] == 0],
                        data['Current (A)'][first_row:last_row][data['ox/red'] == 0]
                    )

                    cyc = cycle()
                    cyc.add_charge(charge)
                    cyc.add_discharge(discharge)
                    
                    cycles.append(cyc)
                    cycle_num +=1               

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

#read_mpt_files()   
read_DTA_files()
