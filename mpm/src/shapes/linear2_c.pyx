# cython: profile=True
# cython: cdivision=True
# cython: boundscheck=False
cimport cython
import numpy as np
cimport numpy as np
ctypedef np.int_t ITYPE_t
ctypedef np.double_t FTYPE_t
cdef extern from "math.h":
    double sqrt(double x)
    double fabs(double x)
    double floor(double x)
    double copysign(double x, double y)
    
ITYPE = np.int
FTYPE = np.float


#===============================================================================    
def updateContribList( dw, patch, dwi ):
    # Update node contribution list
    nx = patch.Nc[0]
    th = patch.thick
    h = patch.dX
    dxdy = h[::-1]/h
    ng = patch.nGhost
    inpf = np.array([h,patch.X0, patch.dX])
    idxs = np.array([0,1,nx,nx+1])
    labels = ['px','gx','cIdx','cW','cGrad']
    px,gx,cIdx,cW,cGrad = dw.getMult(labels,dwi)
    updateContribs( inpf, idxs, ng, th, px, gx, cIdx, cW, cGrad )


#===============================================================================        
def updateContribs( np.ndarray[FTYPE_t, ndim=2] inpf, 
                    np.ndarray[ITYPE_t, ndim=1] idxs,
                    ITYPE_t ng, FTYPE_t th, np.ndarray[FTYPE_t, ndim=2] px, 
                    np.ndarray[FTYPE_t, ndim=2] gx, 
                    np.ndarray[ITYPE_t, ndim=2] cIdx, 
                    np.ndarray[FTYPE_t, ndim=2] cW, 
                    np.ndarray[FTYPE_t, ndim=3] cGrad ):
    # inpf - float input vector - h, dxdy, patch.X0, patch.dX
    cdef int nParts = px.shape[0]
    cdef int cc, idx 
    cdef int ii, jj, kk
    cdef double x, r, h, sgn
    cdef double* hh = [inpf[0,0],inpf[0,1]]
    cdef double* pp = [0.,0.]
    cdef double* S = [0.,0.]
    cdef double* G = [0.,0.]
    cdef int* cix = [0,0]
        
    for ii in range(nParts):
	    
	# Get Cell
        for kk in range(2):
            pp[kk] = px[ii,kk]
	    
            x = (pp[kk] - inpf[1,kk])/inpf[2,kk] + ng;
            cix[kk] = int(floor(x))
                
        cc = int(cix[1]*idxs[2] + cix[0]);

        for jj in range(4):
            idx = cc + idxs[jj];
		
            for kk in range(2):
                x = pp[kk] - gx[idx,kk]
                r = fabs(x)
                h = hh[kk]
                sgn = copysign(1.,x)
		
                if ( r < h ):
                    S[kk] = 1. - r/h
                    G[kk] = -sgn/h 
                else: 
                    S[kk] = 0.
                    G[kk] = 0.	

            cIdx[ii,jj] = idx
            cW[ii,jj] = S[0]*S[1]
            cGrad[ii,jj,0] = S[1]*G[0]
            cGrad[ii,jj,1] = S[0]*G[1]
	
    return 0