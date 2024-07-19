import math
from ECC import Point

import numpy as np
import random
import time
import sys

class ECCSolver_secp256k1:
    g_p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    t_r = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    g_a = 0
    g_b = 7
    st_bit = 16
    st_size = 2 << (st_bit - 1)
    st_n = 0
    G = Point(Point.Gx, Point.Gy)           # table size and number
    p_Q = Point(Point.Gx, Point.Gy)
    p_T = Point(0, 0)
    p_alp = 1
    p_bet = 1
    r_tbl = np.zeros(30)
    n_sol = np.zeros(30)
    n_lp  = np.zeros(30)            # n and loop list 
    n_tbl = None           # r-factor
    p_R = None
    g_r = None
    t_Q = Point(Point.Gx, Point.Gy)
    t_R = Point(Point.Gx, Point.Gy)

    st_tab = []#np.array([])                    # ECC point: R=n*Q, n:unknown                  
    
    def __init__(self, Y):
        self.p_R = Y
        self.st_bit = 23
        self.st_size = 2 << (self.st_bit - 1)
    #----- long table for eqaul search -----------------------#
    st_size = 2 << (st_bit - 1)

    r_tbl = [0]*30                # r_tbl list
    n_sol = [0]*30                # R=n*Q, solve n list
    n_lp  = [0]*30                # Rho loop list
    st_Tab = []                   # table for search
    st_ptr = np.zeros((st_size),dtype=np.int32)  #pointer table
    # ---- Forked by n0ri ---- 
    def rho_init(self):
        # set p_T,p_alp,p_bet
        self.p_T = self.p_Q + self.p_R           # T=Q+R on ECC 
        self.p_alp = 1
        self.p_bet = 1
        # set st_n,Tlim
        self.st_n = ((self.g_r ** 0.5) * 2).astype(int)
        Tlim   = np.array([])
        for i in range(len(self.p_Q)):
            Tlim = np.append(Tlim, self.p_Q[i].modulo)
            self.st_ptr = np.zeros(self.st_size)
            if self.st_n[i] > self.st_size:
                self.st_n[i] = self.st_size
                Tlim[i] = self.p_Q[i].modulo // 4
        # set st_ptr
        self.st_ptr[0:self.st_size] = -1 #  # all pointer is -1
        return Tlim

    #=========================================================#
    #  Rho step in Rho method                                 #
    #    ip = p_T[0] (mod 3)                                  #
    #    ip=0: T=2*T, alp=2*alp, bet=2*bet (mod r)            #
    #    ip=1: T=T*Q, alp=alp+1 (mod r)                       #
    #    ip=2: T=T*R, bet=bet+1 (mod r)                       #
    #---------------------------------------------------------#
    #  copy right : Ushiro Yasunori (ISCPC)                   #
    #    date : 2020/03/16                                    #
    #=========================================================#
    def rho_step(self):#, p_T):
        ip = p_T.x % 3                   # ip=p_T[0] (mod 3)
        if (ip == 0):
            p_T *= p_T            # p_T = 2*p_T on ECC
            self.p_alp = (2*self.p_alp) % self.g_r
            self.p_bet = (2*self.p_bet) % self.g_r
        if (ip == 1):
            self.p_T += self.p_Q        # p_T += p_Q on ECC
            self.p_alp = (self.p_alp + 1) % self.g_r
        if (ip == 2):
            self.p_T += self.p_R        # p_T += p_R on ECC
            p_bet = (p_bet + 1) % self.g_r
        print(self.p_T)

    #=========================================================#
    #  Set list plus Ty                                       #
    #    plas Ty : p_T[1] <= g_p/2                            #
    #    return : list = [p_T[0],p_alp,p_bet]                 #
    #---------------------------------------------------------#
    #  copy right : Ushiro Yasunori (ISCPC)                   #
    #    date : 2020/01/30                                    #
    #=========================================================#
    def plus_Ty(self, index):
        list = [self.p_T[index].x, self.p_alp, self.p_bet]
        if self.p_T[index].y > (self.p_T[index].order >> 1):
            list[1] = self.p_T[index].order - self.p_alp
            list[2] = self.p_T[index].order - self.p_bet
        return list

    def fermat(self, b, n):
        return pow(b, -1, n)

    def inv_mod(self, b, modulo):
        if b == 0:
            return None
        if (type(b) != int) or ((b >= 2) and (b % 2 == 0)):
            low, high = b % modulo, modulo
            c0, c1 = 1, 0
            while low > 1:
                r = high // low
                c2 = c1 - c0 * r
                new = high - low * r
                high = low
                low = new
                c1 = c0
                c0 = c2
            return c0 % modulo

        return self.fermat(b, modulo)
    inv_mod_vec = np.vectorize(inv_mod)
    #=========================================================#
    #  Solve n with T == old-T                                #
    #    n = (al-Tab[1])/(Tab[2]-bl) (mod g_r)                #
    #      Tab[1]=p_alp, Tab[2]=p_bet under p_T[0] > 0        #
    #---------------------------------------------------------#
    #  copy right : Ushiro Yasunori (ISCPC)                   #
    #    date : 2020/03/18                                    #
    #=========================================================#
    def sol_equal(self, loop, al, bl):
        self.Tab = self.plus_Ty()                 # get alp,bet : T[0]>0
        bval = self.Tab[2] - bl
        n = 0
        if bval != 0:
            binv = self.inv_mod_vec(bval, self.g_r)     # 1/bval (mod g_r)
            aval = al - self.Tab[1]
            n = (aval*binv) % self.g_r
            self.n_sol[self.n_tbl] = n             # set n (solve)
            self.n_lp[self.n_tbl] = loop           # set loop

    #=========================================================#
    #  Solve n with  T == 0                                   #
    #    n = Tab[1]/(g_r-Tab[2]) (mod g_r)                    #
    #      Tab[1]=p_alp, Tab[2]=p_bet under p_T[0] > 0        #
    #---------------------------------------------------------#
    #  copy right : Ushiro Yasunori (ISCPC)                   #
    #    date : 2020/03/18                                    #
    #=========================================================#

    
    def sol_zero(self, loop, index):
        self.Tab = self.plus_Ty(index)                 # get alp,bet : T[0]>0
        bval = self.g_r - self.p_bet
        binv = self.inv_mod_vec(bval, self.g_r)        # 1/bval (mod g_r)
        n = (self.p_alp*binv) % self.g_r
        self.n_sol[self.n_tbl] = n                # set n (solve)
        self.n_lp[self.n_tbl] = loop              # set loop

    #=========================================================#
    #  Equal check in Rho method                              #
    #    if pointer equal:                                    #
    #       if Tx equal:                                      #
    #          sol_equal()                                    #
    #          return 1           #solved by equal            #
    #       else:                                             #
    #          change st_Tab                                  #
    #    else:                                                #
    #       change st_ptr                                     #
    #       add st_Tab                                        #
    #    return 0                                             #
    #---------------------------------------------------------#
    #  copy right : Ushiro Yasunori (ISCPC)                   #
    #    date : 2020/01/30                                    #
    #=========================================================#
    def equal_ck(self, loop, index):
        #global st_Tab,st_ptr,st_n
        # check pointer equal
        pt = self.p_T[index].x % self.st_n                  # p_T[0] (mod st_n)
        stv = self.st_ptr[pt[0]]
        self.Tab = self.plus_Ty(index)
        stv = int(stv)                     
        if stv >= 0:                        # check used table      
            if self.p_T[index].x == self.st_tab[stv][0]:
                alp = self.st_tab[stv][1]          # alp in table
                bet = self.st_tab[stv][2]          # bet in table
                self.sol_equal(loop,alp,bet)       # solve equal
                return 1
        # change st_Tab
            else:
                self.st_tab[stv] = self.Tab
        # change st_ptr & add st_Tab
        else:
            self.st_ptr[pt[index]] = len(self.st_tab)         # point last
            self.st_tab.append(self.Tab)
        return 0

    #=========================================================#
    #  Rho method in ECC solver                               #
    #    set Rho table                                        #
    #    initialize Rho step                                  #
    #    loop from solve or limit                             #
    #       if p_T == zero: sol_zero                          #
    #---------------------------------------------------------#
    #  copy right : Ushiro Yasunori (ISCPC)                   #
    #    date : 2020/03/17                                    #
    #=========================================================#
    rho_step_vec = np.vectorize(rho_step)
    def rho_method(self):
        Tlim = self.rho_init()                   # Rho step initaial
        lpmx = int((self.g_r[len(self.g_r) - 1] ** 0.5)*10)       # Rho loop max
        # Rho step
        p_T_tail = len(self.p_T) - 1
        outc = 0
        ip = np.array([None] * p_T_tail)
        for lp in range(0,lpmx, p_T_tail):
            outc += p_T_tail#len(self.p_T)
            for i in range(p_T_tail):
                ip[i] = self.p_T[i].x % 3                   # ip=p_T[0] (mod 3)
            if np.any(ip == 0):
                for i in range(len(ip)):
                    if ip[i] == 0:
                        self.p_T[i] *= self.p_T[i]           # p_T = 2*p_T on ECC
                        self.p_alp = (2 * self.p_alp) % self.g_r
                        self.p_bet = (2 * self.p_bet) % self.g_r
            if np.any(ip == 1):
                for i in range(len(ip)):
                    if ip[i] == 1:
                        self.p_T[i] += self.p_Q[i]           # p_T = 2*p_T on ECC
                        self.p_alp = (self.p_alp + 1) % self.g_r
            if np.any(ip == 2):
                for i in range(len(ip)):
                    if ip[i] == 1:
                        self.p_T[i] += self.p_R[i]           # p_T = 2*p_T on ECC
                        self.p_bet = (self.p_bet + 1) % self.g_r
            print(self.p_T[p_T_tail])
            #self.rho_step_vec(self.p_T[:])
            print(f"[{lp} / {lpmx}]")
            for i in range(p_T_tail):
                if (self.p_T[i].x == 0) and (self.p_T.y[i] == 0):                 # solve by T=zero
                    self.sol_zero(lp+1) 
                    return 2
                if self.p_T[i].x < Tlim[i]:                # only feature poin
                    id = self.equal_ck(lp+1, i)           # check T=old T 
                    if id != 0:
                        return 1                   # solved by T= old T
            if outc >= 5000000:
                print("steps=",(lp+1)//1000000,"M")
                outc = 0
        return 0                            # not solve

    #=========================================================#
    #  Solve n for R=n*Q                                      #
    #     p_Q,p_R : Points on the ECC, n : small integer      #
    #---------------------------------------------------------#
    #  copy right : Ushiro Yasunori (ISCPC)                   #
    #    date : 2020/03/19                                    #
    #=========================================================#
    def SolRnQ(self, mlp):
        #global g_r, p_Q,p_R, fout
        #global fout, n_tbl, n_sol,n_lp
        Rck = self.p_Q

        for m in mlp:
            for k in range(m):
                if np.all(Rck == self.p_R):
                    n = (k + 1) % self.g_r
                    self.n_sol[self.n_tbl] = n               # set n (solve)
                    self.n_lp[self.n_tbl] = k + 1            # set loop
                    if np.all(n):
                        return n[0]
                    return n
                Rck += self.p_Q
        return -1

    #=========================================================#
    #  CRT (Chinese Remainder Theorem) with 2 number          #
    #---------------------------------------------------------#
    #  Get c from a=c (mod p), b=c (mod q), gcd(p,q)=1        #
    #    s=1/p (mod q), t=s*(b-a) (mod q)                     #
    #    c=a+p*t                                              #
    #---------------------------------------------------------#
    #  copy right : Ushiro Yasunori (ISCPC)                   #
    #    date : 2020/03/15                                    #
    #=========================================================#
    def CRT_2(self, a, b, p, q):
        s = self.inv_mod(p, q)                # s=1/p (mod q)
        t = ( s * (b - a) ) % q
        c = a + p * t
        return c

    #=========================================================#
    #  CRT (Chinese Remainder Theorem) with n number          #
    #---------------------------------------------------------#
    #  Get c from a[k]=c mod p[k], k=0,1,...,n-1              #
    #---------------------------------------------------------#
    #  copy right : Ushiro Yasunori (ISCPC)                   #
    #    date : 2020/03/15                                    #
    #=========================================================#
    def CRT_n(self, n, A, P):
        p = P[0]
        a = A[0]
        for k in range(n-1):
            q = P[k+1]
            b = A[k+1]
            c = self.CRT_2(a,b, p,q)
            p = p*q
            a = c
        return c
    
    def solve(self):
        self.r_tbl = np.array([3, 64, 149, 631, 107361793816595537, 174723607534414371449, 341948486974166000522343609283189])
        nv = len(self.r_tbl)
        tlp = 0
        rt = 1

        keys = np.arange(1, 0x1000 + 2)
        G = Point(Point.Gx, Point.Gy)
        Gs = (G * keys)
        start_time = time.time()
        for k in range(nv):
            self.n_tbl = k
            rt += self.r_tbl[k]
            self.g_r = self.r_tbl #[k]                    # r-factor
            self.s_r = self.t_r // self.g_r
            self.p_Q = self.t_Q * self.s_r
            self.p_R = self.t_R * self.s_r
            for k in range(len(self.p_Q)):
                if (self.p_Q[k].x == 0) and (self.p_Q[k].y == 0):
                    self.n_sol[k] = 0
                    self.n_lp[k]  = 0
                else:
                    if (self.g_r[k] % 2 != 0) and (self.g_r[k] % 3 != 0):
                        id = self.rho_method()                 # Rho method
                    else:
                        n = self.SolRnQ(self.g_r)                   # Direct Solve
                        G = Point(Point.Gx, Point.Gy)
                        if G * n == Y:
                            return n
            print(f"Time : {time.time() - start_time}")
            print(f'{k}, r : {self.g_r},  loop : {self.n_lp}')
            ot1 = " r="+format(self.g_r)+" sol="
            ot = ot1+format(self.n_sol)+" loop="+format(self.n_lp[k])+"\n"  
            print(ot1, file=sys.stderr)
            print(ot, file=sys.stderr)
            tlp += self.n_lp[k]
        return n


G = Point(Point.Gx, Point.Gy)
Y = G * 100
solver = ECCSolver_secp256k1(Y)
result = solver.solve()
print(result)