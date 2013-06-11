import numpy as np
import time
from mpm_imports import *

#===============================================================================
# Initial Velocity Function
def initVel(x):
    dv = 1.
    if (x[1]+x[0] > 2.):
        dv = -1.
    return dv * 0.1 * np.array([1.,1.])


#===============================================================================
# Initialize the simulation
def init( useCython ):
    # Initialize Simulation
    # Result File Name + Directory
    outputName = 'two'
    outputDir = 'test_data/two'

    
    # Domain Constants
    x0 = np.array([0.0,0.0]);                    # Bottom left corner
    x1 = np.array([2.,2.])                       # Top right corner
    nN = np.array([40,40])                       # Number of cells
    nG = 2                                       # Number of ghost nodes
    thick = 0.1                                  # Domain thickness
    ppe = 4                                      # Particles per element


    # Material Properties
    E1 = 1.0e3;    nu1 = 0.3;    rho1 = 1.0e3;    
    vWave1 = np.sqrt( E1/rho1 )
    matProps1 = {'modulus':E1, 'poisson':nu1, 'density':rho1 }
    matModelName = 'planeStrainNeoHookean'

    
    # Time Constants
    t0 = 0.0                                                  # Initial Time
    CFL = 0.4                                                 # CFL Condition
    dt = min((x1-x0)/nN) * CFL / vWave1;                      # Time interval
    tf = 10.                                                  # Final time
    outputInterval = 0.05                                     # Output interval
    
     
    # Create Data Warehouse, Patchs, Shape functions
    dw = Dw( outputDir, outputName, outputInterval )
    patch = Patch( x0, x1, nN, nG, t0, tf, dt, thick )
    shape = Shape( useCython )


    # Create boundary conditions
    patch.bcs = []                                 #  BC list

    
    # Create Objects
    mats = []    
    dwi = 1    
    dw.createGrid(dwi,patch)
    mats.append(Material( matProps1, matModelName, dwi, shape, useCython ))
    
    center1 = np.array([0.75,0.75])
    center2 = np.array([1.25,1.25])
    radii = np.array([0.0,0.2])
    density = matProps1['density']
    px1, vol1 = geomutils.fillAnnulus( center1, radii, ppe, patch )
    px2, vol2 = geomutils.fillAnnulus( center2, radii, ppe, patch )
    dw.addParticles( dwi, px1, vol1, density, shape.nSupport )
    dw.addParticles( dwi, px2, vol2, density, shape.nSupport )
    

    # Initialize Data Warehouse and Object Velocities
    mpm.updateMats( dw, patch, mats )
    mats[0].setVelocity( dw,  initVel )

    print 'dt = ' + str(patch.dt)        
    return (dw, patch, mats )


#===============================================================================
def stepTime( dw, patch, mats ):
    # Advance through time
    tbegin = time.time()
    try:
        while( (patch.t < patch.tf) and patch.allInPatch(dw.get('px',1)) ):
            mpm.timeAdvance( dw, patch, mats )
            dw.saveData( patch.dt, mats )
    except JacobianError:
        print 'Negative Jacobian'
            
    tend = time.time()
    print (str(dw.idx) + ' iterations in: ' + readTime(tend-tbegin) 
            + ' t=' + str(patch.t) )
    

#===============================================================================            
def run( useCython=True ):
    dw, patch, mats = init( useCython )
    stepTime( dw, patch, mats )
    return dw