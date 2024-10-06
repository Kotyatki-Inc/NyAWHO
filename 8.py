# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 23:35:44 2024

@author: diana
"""


# COLUMN pl_name:        Planet Name
# COLUMN hostname:       Host Name
# COLUMN pl_letter:      Planet Letter
# COLUMN default_flag:   Default Parameter Set
# COLUMN sy_snum:        Number of Stars
# COLUMN sy_pnum:        Number of Planets
# COLUMN pl_orbper:      Orbital Period [days]
# COLUMN pl_orbsmax:     Orbit Semi-Major Axis [au]
# COLUMN pl_rade:        Planet Radius [Earth Radius]
# COLUMN pl_bmasse:      Planet Mass or Mass*sin(i) [Earth Mass]
# COLUMN pl_orbeccen:    Eccentricity
# COLUMN pl_eqt:         Equilibrium Temperature [K]
# COLUMN st_teff:        Stellar Effective Temperature [K]
# COLUMN st_rad:         Stellar Radius [Solar Radius]
# COLUMN st_mass:        Stellar Mass [Solar mass]
# COLUMN st_lum:         Stellar Luminosity [log(Solar)]
# COLUMN ra:             RA [deg]
# COLUMN dec:            Dec [deg]
# COLUMN sy_dist:        Distance [pc]
# COLUMN sy_vmag:        V (Johnson) Magnitude


pl_name=[]
hostname=[]
pl_letter=[]
def_flag=[]
sy_snum=[]
sy_pnum=[]
pl_orbper=[]
pl_orbsmax=[]
pl_rade=[]
pl_bmasse=[]
pl_orbeccen=[]
pl_eqt=[]
st_teff=[]
st_rad=[]
st_mass=[]
st_lum=[]
ra=[]
dec=[]
sy_dist=[]
sy_vmag=[]

P1=[]
P2=[]
P3=[]
P4=[]
P5=[]
 
f=open("D:/Nasa/New1.csv")
lines=f.readlines()

for i in range(29,len(lines)):
    b=lines[i].split(",")
    pl_name.append(b[0])
    hostname.append(b[1])
    pl_letter.append(b[2])
    def_flag.append(b[3])
    sy_snum.append(b[4])
    sy_pnum.append(b[5])
    pl_orbper.append(b[6])
    pl_orbsmax.append(b[7])
    pl_rade.append(b[8])
    pl_bmasse.append(b[9])
    pl_orbeccen.append(b[10])
    pl_eqt.append(b[11])
    st_teff.append(b[12])
    st_rad.append(b[13])
    st_mass.append(b[14])
    st_lum.append(b[15])
    ra.append(b[16])
    dec.append(b[17])
    sy_dist.append(b[18])
    sy_vmag.append(b[19])
    
f.close()
mag=[]
for i in sy_vmag:
    i=i.strip('\n')
    mag.append(i)
#print(mag)     
    
for i in range(len(pl_name)):
    P1.append(0)
    P2.append(0)
    P3.append(0)
    P4.append(0)
    P5.append(0)


def T(pl_name, pl_eqt):
    points=[]
    Tmin=273.0
    Ter=373
    Tmax=648.0
    plT=[] #sorted by T
    pldT=[] # there is no data about T
    for i in range(len(pl_name)):
        if pl_eqt[i]=='':
            pldT.append(pl_name[i])
                             
        else:
            if float(pl_eqt[i])>Tmin and float(pl_eqt[i])<Tmax:
                plT.append(pl_name[i])
                if float(pl_eqt[i])>Ter:
                    w=3/float(pl_eqt[i])*Ter
                    P1[i]+=w
                    points.append(w)
                else:
                    w=3
                    P1[i]+=w
                    points.append(w)
#    FT=open("D:/Nasa/Tpl.txt", "w")  
 #   FT.write("planet_name"+" "+"points_for_pl_T"+" "+"planet_T_in_K"+"\n")
  #  for i in range(len(plT)):
   #     k=str(plT[i])
    #    u=pl_name.index(k)
     #   FT.write(f"{plT[i]}"+" "+f"{points[i]}"+" "+f"{pl_eqt[u]}"+"\n")
   # for i in range(len(pldT)):
    #    FT.write(f"{pldT[i]}"+" "+"no data"+"\n")
    #FT.close()     
    
    return plT, pldT



def Tstar(pl_name, st_teff):
    points=[]
    Topt=7000.0
    Tc=4000.0
    plTs=[] #sorted by T star
    pldTs=[] # there is no data about T
    for i in range(len(st_teff)):
        if st_teff[i]!="":
            if float(st_teff[i])<Topt:
                plTs.append(pl_name[i])
                if float(st_teff[i])<Tc:
                    P2[i]+=2
                    points.append(2)
                else:
                    w=2*Tc/float(st_teff[i])
                    P2[i]+=w
                    points.append(w)
        else:
            pldTs.append(pl_name[i])
    #FT=open("D:/Nasa/Tstar.txt", "w")  
#    FT.write("planet_name"+" "+"points_for_star_T"+" "+"star_T_in_K"+"\n")
 #   for i in range(len(plTs)):
  #      k=str(plTs[i])
   #     u=pl_name.index(k)
    #    FT.write(f"{k}"+" "+f"{points[i]}"+" " +f"{st_teff[u]}"+"\n")
    #for i in range(len(pldTs)):
     #   FT.write(f"{pldTs[i]}"+" "+"no data"+"\n")
    #FT.close() 
    return plTs, pldTs            


def g(pl_name, pl_bmasse, pl_rade):
    points=[]
    G=[]
    gmin=0.5
    gmax=2
    plg=[] #sorted by g of planet
    pldg=[] # there is no data about g
    for i in range(len(pl_name)):
        if pl_bmasse[i]!="" and pl_rade[i]!="" :
            g=float(pl_bmasse[i])/(float(pl_rade[i]))**2
            G.append(g)
            if g<=gmax and g>=gmin:
                plg.append(pl_name[i])
                P3[i]+=1.5
                points.append(1.5)
            elif g>gmax:
                w=1.5/g*2 
                P3[i]+=w
                points.append(w)
            elif g<gmin:
                w=1.5*g*2
                P3[i]+=w
                points.append(w)
        else:
            pldg.append(pl_name[i])
        #FT=open("D:/Nasa/g.txt", "w")
        #FT.write("planet_name"+" "+"points_for_pl_g"+" "+"planet_g_in_Earth_g"+"\n")
        #for i in range(len(plg)):
          #  k=str(plg[i])
         #   FT.write(f"{k}"+" "+f"{points[i]}"+" "+f"{G[i]}"+"\n")
        #for i in range(len(pldg)):
         #   FT.write(f"{pldg[i]}"+" "+"no data"+"\n")
        #FT.close() 
    return plg, pldg           


def ro(pl_name, pl_bmasse, pl_rade):
    ro=0.35
    Rho=[]
    points=[]
    plro=[]
    pldro=[]
    for i in range(len(pl_name)):
        if pl_bmasse[i]!="" and pl_rade[i]!="" :
            rho=float(pl_bmasse[i])/(float(pl_rade[i]))**3
            Rho.append(rho)
            if rho>=ro:
                plro.append(pl_name[i])
                w=2*min(rho,1/rho)
                P4[i]+=w
                points.append(w)
            else: 
                points.append(0)
        else:
            pldro.append(pl_name[i])
        #FT=open("D:/Nasa/ro.txt", "w")
        #FT.write("planet_name"+" "+"points_for_pl_rho"+" "+"planet_rho_in_Earth_ro"+"\n")
       # for i in range(len(plro)):
        #   FT.write(f"{k}"+" "+f"{points[i]}"+" "+f"{Rho[i]}"+"\n")
       # for i in range(len(pldro)):
        #    FT.write(f"{pldro[i]}"+" "+"no data"+"\n")
        #FT.close()         
    return plro, pldro               
    
def pn(pl_name, sy_pnum):
    points=[]
    for i in range(len(pl_name)):
        P5[i]+=(int(sy_pnum[i])-1)
        points.append(int(sy_pnum[i])-1)
    #FT=open("D:/Nasa/pn.txt", "w")   
    #FT.write("planet_name"+" "+"count_of_other_planet"+"\n")
    #for i in range(len(pl_name)):
      #  FT.write(f"{pl_name[i]}"+" "+f"{points[i]}"+"\n")
   # FT.close()         

pn(pl_name, sy_pnum)
ro(pl_name, pl_bmasse, pl_rade)
Tstar(pl_name, st_teff)
g(pl_name, pl_bmasse, pl_rade)
T(pl_name, pl_eqt)

P=[]
for i in range(len(P1)):
    P.append(P1[i]+P2[i]+P3[i]+P4[i]+P5[i])

import numpy as np

N=[]
for i in range(20):
    N.append(0)
a=13/20
for i in P:
    for j in range(20):
        if i>=(j-1)*a and i<=j*a:
            N[j]+=1
X=[]
for i in range(20):
    X.append((i-0.5)*a)
       

from matplotlib import pyplot as plt 
plt.plot(X,N)
plt.xlabel("points for planet")
plt.ylabel("number of planets")
plt.title("Distribution of points")
plt.show()

# подивитися на розподіл 

def magn(pl_name, mag, pl_rade, pl_orbsmax):
    M=[]
    for i in range(len(pl_name)):
        if mag[i]!='' and pl_rade[i]!='' and pl_orbsmax[i]!='' :
            f=float(mag[i])-2.5*np.log10(0.05*float(pl_rade[i])**2/float(pl_orbsmax[i])**2/555000000)
            if f>=6. and f<=500.:
                M.append(f)
            else: 
                M.append("no data")
        else:
            M.append("no data")
    return M

#print(magn(pl_name, mag, pl_rade, pl_orbsmax))

def mas(pl_name, pl_orbsmax, sy_dist):
    A=[]
    for i in range(len(pl_name)):
        if sy_dist[i]!='' and pl_orbsmax[i]!='':
            A.append(float(pl_orbsmax[i])/float(sy_dist[i])*1000.)
        else:
            A.append("no data")
    return A
print(mas(pl_name, pl_orbsmax, sy_dist))        
def Final(pl_name, P, sy_dist, ra, dec, M, A):
    with open("D:/Nasa/final1.txt", "w") as F:
        F.write("pl_name, points, dist(pa), ra(deg), dec(deg), magn, mas"+"\n")
        for i in range(len(pl_name)):
            F.write(f"{pl_name[i]},"+f"{P[i]},"+f"{sy_dist[i]},"+f"{ra[i]},"+f"{dec[i]},"+f"{M[i]},"+f"{A[i]},"+"\n")    
            

Final(pl_name, P, sy_dist, ra, dec, magn(pl_name, mag, pl_rade, pl_orbsmax), mas(pl_name, pl_orbsmax, sy_dist)) 
   