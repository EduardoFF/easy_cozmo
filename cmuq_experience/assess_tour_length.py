# arguments: < SOL file> :ordered set of points (tour)

import sys
import math
P={}
P_by_index={}
pline=None

with_rot = True

def read_tsplib(tspfile):
    global P
    f = open(tspfile)
    lines=f.readlines()
    read_coo = False
    P=dict()
    ix=0
    for line in lines:
        s=line.split()
        if read_coo:
            if s[0] == "EOF":
                break
            P[s[0]] = (float(s[1]),float(s[2]))
            P_by_index[ix] = P[s[0]]
            ix += 1

        if s[0] == "NODE_COORD_SECTION":
            read_coo = True

def read_tour(tourfile):
    print(tourfile)
    f=open(tourfile)
    tour=[]
    for line in f.readlines():
        s=line.split()
        if len(s)==1:
            tour.append(int(s[0]))
    if tour[0] == tour[-1]:
        return tour[:-1]
    else:
        return tour


def read_sol(solfname):
    sol=[]
    f=open(solfname)
    lines = f.readlines()
    if not len(lines):
        print("ERROR Reading sol - empty or no file")
        exit(1)
    s = lines[0].split()
    if not len(s):
        print("ERROR Reading Sol: First line empty")
        exit(1)
    n = int(s[0])
    if n != len(P):
        print("ERROR solution length (%d) different from %d"%(n,len(P)))
        exit(1)
    for line in lines[1:]:
        s = line.split()
        for t in s:
            nid=int(t)
            sol.append(nid)
    if len(sol) != len(P):
        print("ERROR READ n_points (%d) different from %d"%(len(sol),len(P)))
        exit(1)
    return sol

linear_speed_mmps = 85
rot_speed_radps = (5 * math.pi / 180.)

def angle(X,Y, i, k, j):
#    print("angle ", i, k, j)
    dix = X[i] - X[k]
    diy = Y[i] - Y[k]
    djx = X[j] - X[k]
    djy = Y[j] - Y[k]
#    print(djx, djy)
    ni = ( dix**2 + diy**2) ** 0.5
    nj = ( djx**2 + djy**2) ** 0.5
#    print("ni ", ni, " nj ", nj)
    val = (dix*djx + diy*djy)/(ni*nj)
    if val < -1.0:
        val = -1.0
    if val > 1.0:
        val = 1.0
    alpha =  math.acos(val)
    return alpha


def tour_cost(tour):
    X = [P_by_index[i][0] for i in tour]
    Y = [P_by_index[i][1] for i in tour]
    n=len(X)
    cntheading = 0
    print("tour len ", n)
    distance = 0
    rotations = 0
    import math
    rotations =  math.atan2( Y[1] - Y[0], X[1] - X[0])
    for i in range(0,n):
        next=(i+1)%n
        if i < n:
            nextnext=(i+2)%n
            theta = angle(X,Y,i, next, nextnext)
#            print("angle ", i, next, nextnext, 180 * theta/ math.pi, theta, (math.pi - abs(theta)), rot_speed_radps, (math.pi - abs(theta)) / rot_speed_radps)

            if theta > math.pi:
                theta -= 2 * math.pi
            elif theta <= -math.pi:
                theta += 2 * math.pi
            rotations += (math.pi - abs(theta))

        dst = (X[i] - X[next])**2 + (Y[i] - Y[next])**2
        distance += (dst **0.5)

        cntheading = math.atan2( Y[next] - Y[i], X[next] - X[i])
        if cntheading > math.pi:
            cntheading -= 2 * math.pi
        elif cntheading <= -math.pi:
            cntheading += 2 * math.pi
    print("DISTANCE (mm) {:.2f} TURNS (deg) {:.2f}".format(distance * 10,  rotations * ( 180/math.pi)))

    return (distance * 10) / linear_speed_mmps + rotations / rot_speed_radps


""" must be in folder """
tsplib_fname = "cmuqexperience_25.tsp"
read_tsplib(tsplib_fname)

if len(sys.argv) == 2:
    sol=read_tour(sys.argv[1])
    print(sol)
    cost = tour_cost(sol)
    print("COST ", cost)
if len(sys.argv) > 3:
    maxcost = 0
    for tfile in sys.argv[2:]:
        print("READING ", tfile)
        sol=read_tour(tfile)
        print(sol)
        cost = tour_cost(sol)
        print("COST ", cost)
        maxcost = max(maxcost, cost)
    print("MAXCOST ", maxcost)
