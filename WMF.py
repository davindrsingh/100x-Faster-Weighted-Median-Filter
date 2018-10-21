import numpy as np
import cv2
import math



def create_histogram(Nf, Ni, I, F, r, p): # I - image F - feature map
    histogram = np.zeros(Nf, Ni) #each cell stors number of pixels that have i and f vaues
    # Initializing Histogram for the first time
    for i in range(2*r+1):
        for j in range(2*r+1):
            if (i,j) != p:
                f = F[i][j]
                in_ = I[i][j]
                histogram[f][in_] += 1

    cut_point = 0 #setting Initial cut point ==0

    # Initializing BCB counter
    BCB = np.zeros((Nf,1))
    for i in range(Nf):
        count = histogram[i][0]
        for j in range(1,Ni):
            count = count - histogram[i][j]
        BCB[i] = count

#note that if we take images with >1 channels the f map will be a vector

def g(f1, f2):
    return math.exp(-abs(f1-f2))
def calculate_balance(BCB, fp):
    b = 0
    for i in range(BCB.shape[0]):
        b += BCB[i] * g(i, fp)
    return b

def update_BCB(histogrm, cutpoint):
    new_BCB = np.zeros((histogrm.shape[0],1))
    for i in range(histogrm.shape[0]):
        count = 0
        for j in range(histogrm.shape[1]):
            if j <= cutpoint:
                count += 1
            else:
                count -= 1
        new_BCB[i] = count
    return  new_BCB

def find_cutpoint(initial_cut_point, histogram, BCB, fp):
    cp = initial_cut_point

    balance = calculate_balance(BCB, fp)
    if balance>=0:
        while(balance>=0):
            cp = cp - 1
            nBCB = update_BCB(histogram,cp)
            balance = calculate_balance(nBCB,fp)
        return cp+1, nBCB
    else:
        while (balance<0):
            cp = cp + 1
            nBCB = update_BCB(histogram, cp)
            balance = calculate_balance(nBCB, fp)
        return cp, nBCB, balance #cp is the weighted median

# Function to update the histogram when window moves
def update_histogram(histogram, flag, p,r, I, F):
    if flag == 'r':
        for i in range(p[0]-r, p[0]+r+1):
            f,iv = F[i][p[1]-r], I[i][p[1]-r]
            histogram[f][iv] -= 1
        for j in range(p[1]-r, p[1]+r+1):
            f,iv = F[p[0]-r][j],I[p[0]-r][j]
            histogram[f][iv] += 1
    histogram = np.zeros((histogram.shape[0],histogram.shape[1]))
    if flag == 'd':
        for i in range(p[0]-r, p[0]+r+1):
            for j in range(2 * r + 1):
                if (i, j) != p:
                    f = F[i][j]
                    in_ = I[i][j]
                    histogram[f][in_] += 1
    return histogram

