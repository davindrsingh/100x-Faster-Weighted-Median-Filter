import numpy as np
import cv2
import math
import time
def create_histogram(Nf, Ni, I, F, r, p): # I - image F - feature map
    histogram = np.zeros((Nf, Ni)) #each cell stores number of pixels that have i and f vaues
    # Initializing Histogram for the first time
    for i in range(2*r+1):
        for j in range(2*r+1):
            f = F[i][j]
            in_ = I[i][j]
            histogram[f][in_] += 1

    cut_point = 0 #setting Initial cut point ==0
    # Initializing BCB counter
    BCB = np.zeros((Nf,1))
    necklace = set()
    for i in range(2*p[0]+1):
        for j in range(2*p[0]+1):
            f = F[i][j]
            necklace.add(f)
            if I[i][j]<=0:
                BCB[f]+=1
            else:
                BCB[f]-=1

    return histogram, BCB, necklace
#note that if we take images with >1 channels the f map will be a vector

def g(f1, f2):
    #print f1, f2
    #return min(f1,f2)/max(f1,f2,1)
    return math.sqrt(int(f1)**1+int(f2)**1)
    #return math.exp(-abs(int(f1)-int(f2)))
## Function to calculate balance
def calculate_balance(BCB, necklace, fp):
    b = 0
    for i in necklace:
        b += BCB[i] * g(i, fp)
   #print b
    return b[0]

## Function to update BCB during cut-point calculation
def update_BCB(histogrm, cutpoint, I, F, p, r):
    new_BCB = np.zeros((256,1))
    new_necklace = set()
    c = cutpoint
    for i in range(p[0]-r, p[0]+r+1):
        for j in range(p[1]-r, p[1]+r+1):
            f  = F[i][j]
            new_necklace.add(f)
            if I[i][j]<=c:
                new_BCB[f] += 1
            else:
                new_BCB[f] -= 1
    return new_BCB, new_necklace

# Function to find cutpoint
def find_cutpoint(initial_cut_point, histogram, BCB, necklace, fp, I, F, p, r):
    cp = initial_cut_point
    balance = calculate_balance(BCB, necklace, fp)
    if balance>=0: ## if balance >=0 shift cutpoint to left until negative
        flag = 0
        return_bcb = BCB
        return_balance = balance
        while(flag==0):
            cp = cp - 1
            nBCB, nNCK = update_BCB(histogram,cp,I, F, p, r)
            nbalance = calculate_balance(nBCB, nNCK, fp)
            if nbalance<0 or cp<0:
                flag=1
            else:
                return_bcb = nBCB
                return_balance = nbalance
        return cp+1, return_bcb, return_balance
    else:  ## if balance < 0 shift cutpoint to right until positive
        flag = 0
        while (flag == 0):
            cp = cp + 1
            nBCB, nNCK = update_BCB(histogram, cp,I, F, p, r)
            balance = calculate_balance(nBCB, nNCK, fp)
            if balance>=0 or cp>255:
                flag=1
        return cp, nBCB, balance # cp is the weighted median

# Function to update the histogram when window shifts
def update_histogram(histogram, flag, p,r, I, F):
    if flag == 'r':
        for i in range(p[0]-r, p[0]+r+1):
            f,iv = F[i][p[1]-r-1], I[i][p[1]-r-1]
            if histogram[f][iv]>0:
                histogram[f][iv] -= 1
            nf, niv = F[i][p[1]+r], I[i][p[1]+r]
            histogram[nf][niv] += 1
        return histogram
    if flag == 'd':
        nhistogram = np.zeros((256, 256))
        for i in range(p[0]-r, p[0]+r+1):
            for j in range(p[1]-r, p[1]+r+1):
                f = F[i][j]
                in_ = I[i][j]
                nhistogram[f][in_] += 1
        return nhistogram

def filter(IMG,p, F, r,a,b): #p is the starting pixel
    print "start!!!...please wait!!!!"
    New_IMG = np.zeros((a,b))
   
    #initialize histogram
    histogram, BCB, necklace = create_histogram(256, 256, IMG, F, r, p)
    #BCB = update_BCB(histogram, 0, IMG, F, p, r)
    w, BCB, bal = find_cutpoint(0,histogram, BCB, necklace, F[p[0]][p[1]], IMG, F, p, r)
    New_IMG[p[0]-r][p[1]-r] = w #resultant image
    flag = 0
    cp = w #initial cutpoint
   
    for i in range(p[0], IMG.shape[0]-r):
        for j in range(p[1], IMG.shape[1]-r):
            if flag == 1: ##if window shifts downward
                histogram = update_histogram(histogram, 'd', (i,j), r, IMG, F)
                flag = 0
            else:  ## if window moves right
                histogram = update_histogram(histogram, 'r', (i,j), r, IMG, F)

            BCB, nck = update_BCB(histogram, cp, IMG, F, (i,j), r)
            # find_cutpoint
            nw, BCB, bal = find_cutpoint(cp, histogram, BCB, nck, F[i][j], IMG, F, (i,j), r)
            
            New_IMG[i-r][j-r] = nw
           # print nw, IMG[i][j]
            cp = nw
            if j == IMG.shape[1]-r-1: #windows reached horizontal end...move the window downward in next iteration
                flag = 1
    
    return New_IMG


for i in range(1,5):
    print "Processing Image %d "%i
    img = cv2.imread(str(i)+".jpg",1)
    for j in range(1,4):
        rc = pow(0.5,j)
        img = cv2.resize(img, (0,0), fx = rc, fy = rc, interpolation=cv2.INTER_CUBIC)
        r = 4
        result = np.zeros((img.shape[0],img.shape[1],3))
       
        red = img[:,:,2]  
        red = cv2.copyMakeBorder(red,r,r,r,r,cv2.BORDER_CONSTANT,value=0)

        green = img[:,:,1]  
        green = cv2.copyMakeBorder(green,r,r,r,r,cv2.BORDER_CONSTANT,value=0)

        blue = img[:,:,0]
        blue = cv2.copyMakeBorder(blue,r,r,r,r,cv2.BORDER_CONSTANT,value=0)

        R = filter(red, (4,4), red, r, result.shape[0],result.shape[1])
        G = filter(green, (4,4), green, r, result.shape[0],result.shape[1])
        B = filter(blue, (4,4), blue, r, result.shape[0],result.shape[1])
        
        result[:,:,2] = R
        result[:,:,1] = G
        result[:,:,0] = B
        result = result.astype('uint8')
        
        cv2.imwrite("RGB_result"+str(i)+"_"+str(j)+".jpg", result)
        
        
print "Done!"

