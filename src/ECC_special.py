import numpy as np
import random
import time
import sys
import ECC

class Point:
    modulo = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    order  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
    G = ECC.Point(Gx, Gy)
    x  = 0
    y  = 0

    def __init__(self, x, y, order = order, modulo = modulo):
        self.x = x
        self.y = y
        self.order  = order
        self.modulo = modulo
    
    def __str__(self):
        return f"{self.x}\t{self.y}"

    def __mod__(self, q):
        return self.x % q

    def __mul__(self, b):
        if type(b) == np.ndarray:
            mulk_vec = np.vectorize(self.mulk)
            mulk_vec(b)
        if type(b) == Point:
            self.double(b)
        else:
            self.mulk(b)
    
    def __eq__(self, Q):
        # 今回は離散対数問題用に作ったもの。新しいアプリを作るためのものではない。

        if type(Q) == int:
            return self == Q

        match_x = self.x == Q.x
        #match_y = self.y == Q.y

        #matched_point = match_x and match_y
        return match_x#matched_point
    
    def __sub__(self, Q): #これは普段使いません。 離散対数問題や攻撃には使えるかも...?
        if type(Q) == int:
            return self - Q
        #diff_point = Point((self.x - Q.x), (self.y - Q.y))
        self.x -= Q.x
        self.y -= Q.y#diff_point


    def __add__(self, q):
        if q.x != 0: # 単位元の場合は何もしない
            if(q == self):
                tmp = ( (3 * (q.x ** 2)) * self.rev(2 * q.y) ) % self.modulo
                x   = (tmp ** 2 - 2 * q.x)    % self.modulo
                y   = (tmp * (q.x - self.x) - q.y) % self.modulo
            else:
                tmp = ( (q.y-self.y) * self.rev(q.x-self.x) ) % self.modulo
                x = (tmp ** 2 - self.x -q.x) % self.modulo
                y = (tmp * (self.x - x) - self.y) % self.modulo
            self.x = x
            self.y = y
        #return Point(x, y)

    def double(self, P):
        tmp = ( (3 * (P.x ** 2)) * self.rev(2 * P.y) ) % self.modulo
        x   = (tmp ** 2 - 2 * P.x) % self.modulo
        y   = (tmp * (P.x - x) - P.y) % self.modulo
        self.x = x
        self.y = y
        #return Point(x, y)

    def add(self, p, q):
        tmp = ( (q.y-p.y) * self.rev(q.x-p.x) ) % self.modulo
        x = (tmp ** 2 - p.x -q.x) % self.modulo
        y = (tmp * (p.x - x) - p.y) % self.modulo
        self.x = x
        self.y = y

    def discrete_log_rho_vetor_method(self, bits_size = 8, random_mode = False):
        bits_size = 2 ** bits_size
        key = None
        alpha_vec = np.arange(1, bits_size, dtype=object)
        beta_vec  = np.arange(1, bits_size, dtype=object)
        X = np.array([])
        X2 = np.array([])
        global G
        G = Point(Point.Gx, Point.Gy)  #元

        print("Generating Vector...")
        _G  = Point(Point.x, Point.y)
        _G2 = Point(Point.x, Point.y)
        for i in range(1, bits_size):
            EG = ECC.Point(Point.Gx, Point.Gy) * (i)
            _G = Point(EG.x, EG.y)
            _G2 = Point(EG.x, EG.y)
            X = np.append(X, _G)
            X2 = np.append(X2, _G2)
        #X  = np.full(bits_size, _G)
        #X2 = np.full(bits_size, _G2)
            print(f"[{i} / [{bits_size}]\t{format(G.x, '064x')}\t{format(G.y, '064x')}", file=sys.stderr)

        #for i in range(0, bits_size):
        #e = Point(0, 0)  #単位元
        #X2[0:bits_size] = e
        #print(X2)
        #print(f"[{i + 1} / [{bits_size}]\t{format(G.x, '064x')}\t{format(G.y, '064x')}", file=sys.stderr)
        
        print("OK.", file=sys.stderr)
        print(file=sys.stderr)
        global mods_x

        mods_x = None

        alpha_vec_2 = np.arange(1, bits_size, dtype=object)
        beta_vec_2  = np.arange(1, bits_size, dtype=object)

        def f(x, a, b):
            global mods_x
            mods_x = x % 3

            x[mods_x == 0] + G#b[mods_x == 0]
            x[mods_x == 1] + x[mods_x == 1]
            x[mods_x == 2] + self#a[mods_x == 2]
            
            

            #x[mods_x == 0] = (x[mods_x == 0] * b[mods_x == 0]) % self.modulo
            #x[mods_x == 1] = (x[mods_x == 1] * x[mods_x == 1]) % self.modulo
            #x[mods_x == 2] = (x[mods_x == 2] * a[mods_x == 2]) % self.modulo
        
        def g(x, a, step = bits_size):
            global mods_x
            mods_x = x % 3
            a[mods_x == 1] *= 2
            a[mods_x == 1] %= self.order
            a[mods_x == 2] += step
            a[mods_x == 2] %= self.order

        def h(x, b, step = bits_size):
            global mods_x
            mods_x = x % 3
            b[mods_x == 0] += step
            b[mods_x == 0] %= self.order
            b[mods_x == 1] *= 2
            b[mods_x == 1] %= self.order



        f_vec = np.vectorize(f)
        starttime = time.time()
        print("[+] Start analysis... Kill that elliptic curve cryptography!!", file=sys.stderr)
        progress = 1
        for i in range(1, self.order, bits_size):

            print(f"Progress : {i}\t Alpha : {alpha_vec}\t Beta : {beta_vec}\tAlpha_2 : {alpha_vec_2}\t Beta_2 : {beta_vec_2}", file=sys.stderr)
            f(X[:], alpha_vec[:], beta_vec[:])
            g(X[:], alpha_vec[:])
            h(X[:], beta_vec[:])
            
            f(X2[:], alpha_vec_2[:], beta_vec_2[:])
            f(X2[:], alpha_vec_2[:], beta_vec_2[:])
            g(X2[:], alpha_vec[:])
            h(X2[:], beta_vec[:])
            #f(X2[:], alpha_vec_2[:], beta_vec_2[:])
            #f(X2[:], alpha_vec_2[:], beta_vec_2[:])
            #f(X2[:], alpha_vec_2[:], beta_vec_2[:])

            #f(X2[:], alpha_vec_2[:], beta_vec_2[:])
            #f(X2[:], alpha_vec_2[:], beta_vec_2[:])
            #f(X2[:], alpha_vec_2[:], beta_vec_2[:])
            #g(X2[:], alpha_vec_2[:])
            #h(X2[:], beta_vec_2[:])
            #g(X2[:], alpha_vec_2[:])
            
            #f(X2[:], alpha_vec_2[:], beta_vec_2[:])
            #h(X2[:], beta_vec_2[:])
            #f(X2[:])
            #h(X2[:], beta_vec_2[:])
            #h(X2[:], beta_vec_2[:])


            if np.all(X == X2):#np.any(X == self) and np.any(X2 == self): #np.any(X == X2):#np.any(X == self) and np.any(X2 == self):#np.any(X == self) and np.any(X2 == self):#(np.isin(X == X2, True)) > 0:
                #collision_index = np.where((X == self) == True)#np.where(X == X2)[0][0])
                b = beta_vec - beta_vec_2 #int(beta_vec[X == self] - beta_vec_2[X2 == self])
                print("[+] FOUND Point !!", file=sys.stderr)
                G = ECC.Point(Point.Gx, Point.Gy)
                try:
                    a = alpha_vec_2 - alpha_vec
                    #key = a * self.rev_vec(b, self.order) % self.order#self.rev_vec(r, self.order) * a % self.ordernp.gcd(a, b)#self.rev_vec(b, self.order) * a % self.order#self.rev_vec(r, self.order) * a % self.order
                    print("Validation...")

                    #key = beta_vec
                    #print(key, file=sys.stderr)
                    #found_key_index = (np.where(self in Y)[0])
                    #key = key[found_key_index[0]]
                    Y = G * key
                    print(f" G * {key} == {self}", file=sys.stderr)
                    assert self == Y
                    print("[+] OK", file=sys.stderr)
                    endtime = time.time() - starttime
                    print(f"sol time {endtime}", file=sys.stderr)
                    if random.randint(0, 100) >= 80: # 単純に楽しみたいだけ
                        print("Accelerator >> It's a one-way street from here on out!!", file=sys.stderr)
                        print(file=sys.stderr)
                        return key
                    print("Kamijo Touma >> Kill that illusion!!", file=sys.stderr)
                    print(file=sys.stderr)
                    return key
                except AssertionError:
                    break


            progress += bits_size
        print("Keys is Not Found... :(", file=sys.stderr)
        return None

    def rev(self, b, modulo = modulo):
        if b == 0:
            return None
        #if (type(b) != int) or ((b >= 2) and (b % 2 == 0)):
        #    low, high = b % modulo, modulo
        #    c0, c1 = 1, 0
        #    while low > 1:
        #        r = high // low
        #        c2 = c1 - c0 * r
        #        new = high - low * r
        #        high = low
        #        low = new
        #        c1 = c0
        #        c0 = c2
        #    return c0 % modulo

        return pow(int(b), -1, modulo) # special
    rev_vec = np.vectorize(rev)

    def mulk(self, k):
        scalar_bin = str(bin(k))[2:]
        gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
        gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
        G_p = Point(gx, gy)
        for i in range(1, len(scalar_bin)):
            G_p.double(self.G)
            #tmp = ( (3 * (G_p.x ** 2)) * self.rev(2 * G_p.y) ) % self.modulo
            #x   = (tmp ** 2 - 2 * G_p.x) % self.modulo
            #y   = (tmp * (G_p.x - x) - G_p.y) % self.modulo
            if scalar_bin[i] == "1":
                G_p + self.G
                #tmp = ( (self.y-G_p.y) * self.rev(self.x-G_p.x) ) % self.modulo
                #x = (tmp ** 2 - G_p.x -self.x) % self.modulo
                #y = (tmp * (G_p.x - x) - G_p.y) % self.modulo
        self.x = G_p.x
        self.y = G_p.y