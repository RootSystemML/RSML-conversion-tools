from openalea.deploy.shared_data import shared_data

import rsml
from rsml import misc
from rsml import measurements

import numpy as np
from matplotlib import pyplot as plt
from glob import glob
import os

# load rsml
rsml_dir = shared_data(rsml.__path__)#,'AR570/2012_11_25_09h00_chl110_1_1.rsml')
rsml_files = sorted(glob(rsml_dir/"AR570/*.rsml"))

def plot(x,y, label):
    l = plt.plot(x,y, '+')[0]
    
    # fit and plot linear regression
    #   add constraint on (0,0)    
    x = np.hstack(([0],x))
    y = np.hstack(([0],y))
    w = np.ones_like(x)
    w[0]=2*x.size
    
    #  fitting
    c = np.polyfit(x,y,2, w=w)
    
    # plot
    X = np.linspace(0,x.max(),5)
    def poly(x,c):
        return sum([ci*(X**i) for i,ci in enumerate(c)])
        
    plt.plot(X,poly(X,c[::-1]),l.get_color(), label=label, lw=2)

    ax.set_xlabel("Distance from ramification to primary tip")
    ax.set_ylabel("Lateral root length")
    
def plot_from_file(rsml_file, ax, split_plant, label=""):
    g = rsml.rsml2mtg(rsml_file)

    # extract properties & measurments for all roots
    root = measurements.root_order(g)               # ids of lateral roots
    root = [r for r,o in root.iteritems() if o==2]
    length = measurements.root_length(g,root)       # length of roots
    ppos = measurements.parent_position(g,roots=root,distance2tip=True)  # branching position on parent                
    plant = dict((r,g.complex(r)) for r in root)    # plant id of all roots
    
    if split_plant:
        # plot root length w.r.t parent_position, for each plant
        for i,pid in enumerate(sorted(set(plant.values()))):
            rids = [r for r,p in plant.iteritems() if p==pid]
            x = np.array([ppos[r]   for r in rids])
            y = np.array([length[r] for r in rids])
            plot(x,y,"plant %d"%(i+1))

    else:
        x = np.array([ppos[r]   for r in root])
        y = np.array([length[r] for r in root])
        plot(x,y, label)


plt.ion()
plt.clf()
                                       

# plot last time step, for each plant
#ax = plt.subplot(1,1,1) 
#filename = os.path.split(rsml_files[-1])[-1]
#plot_from_file(rsml_files[-1], ax, split_plant=True)
#ax.set_title("Individual plants at day 12")    
    
# plot for each time step, no plant distinction 
ax = plt.subplot(1,1,1)#, sharex=ax, sharey=ax)
days = [6,7,8,10,11,12]
for i,rsml_file in enumerate(rsml_files):
    plot_from_file(rsml_file, ax, split_plant=False, label="day %2d"%days[i])
ax.set_title("All plants from day 6 to 12")    
    
    

