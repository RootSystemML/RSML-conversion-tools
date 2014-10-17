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
rsml_files = glob(rsml_dir/"AR570/*.rsml")

plt.ion()
plt.clf()
ax = None
for i,rsml_file in enumerate(sorted(rsml_files)):
    filename = os.path.split(rsml_file)[-1]
    print filename
    g = rsml.rsml2mtg(rsml_file)
    
    # extract properties & measurments for all roots
    root = measurements.root_order(g)               # ids of lalteral roots
    root = [r for r,o in root.iteritems() if o==2]
    length = measurements.root_length(g,root)       # length of roots
    ppos = measurements.parent_position(g,root)     # branching position on parent
    plant = dict((r,g.complex(r)) for r in root)    # plant id of all roots
    
    ax = plt.subplot(len(rsml_files),1,i+1, sharex=ax, sharey=ax)
    
    # plot root length w.r.t parent_position, for each plant
    for pid in sorted(set(plant.values())):
        rids = [r for r,p in plant.iteritems() if p==pid]
        x = np.array([ppos[r]   for r in rids])
        y = np.array([length[r] for r in rids])
        o = x.argsort()
        l = plt.plot(x[o],y[o], '.')[0]
        
        # fit and plot linear regression
        a,b = np.polyfit(x,y,1)
        X = np.array([0,x.max()])
        plt.plot(X,a*X+b,l.get_color(), label="a=%.2f"%a)
    
    ax.set_title(filename)    
    ax.legend(loc=0)
