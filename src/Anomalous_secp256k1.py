# Do not Use.

import numpy as np
import ECC

class Point:
    modulo = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F#0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141 #0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    order  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F #SSSA Forge #0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
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
        return Point(self.x % q, self.y % q)

    def __mul__(self, b):
        if (type(b) == Point) or (type(b) == ECC.Point):
            return self.double(b)
        if type(b) == np.ndarray:
            mulk_vec = np.vectorize(self.mulk)
            return mulk_vec(b)
        return self.mulk(b)
    
    def __eq__(self, Q):
        # 今回は離散対数問題用に作ったもの。新しいアプリを作るためのものではない。
        match_x = self.x == Q.x
        match_y = self.y == Q.y

        matched_point = match_x and match_y
        return matched_point
    
    def __sub__(self, Q): #これは普段使いません。 離散対数問題や攻撃には使えるかも...?
        #diff_point = Point((self.x - Q.x), (self.y - Q.y))
        if type(Q) == int:
            return self.x - Q
        return Point(self.x - Q.x, self.y - Q.y)#diff_point


    def __add__(self, q):
        if(q == self):
            tmp = ( (3 * (q.x ** 2)) * self.rev(2 * q.y) ) % self.modulo
            x   = (tmp ** 2 - 2 * q.x)    % self.modulo
            y   = (tmp * (q.x - self.x) - q.y) % self.modulo
        else:
            tmp = ( (q.y-self.y) * self.rev(q.x-self.x) ) % self.modulo
            x = (tmp ** 2 - self.x -q.x) % self.modulo
            y = (tmp * (self.x - x) - self.y) % self.modulo
        return Point(x, y)

    def double(self, P):
        tmp = ( (3 * (P.x ** 2)) * self.rev(2 * P.y) ) % self.modulo
        x   = (tmp ** 2 - 2 * P.x) % self.modulo
        y   = (tmp * (P.x - x) - P.y) % self.modulo
        return Point(x, y)

    def add(self, p, q):
        tmp = ( (q.y-p.y) * self.rev(q.x-p.x) ) % self.modulo
        x = (tmp ** 2 - p.x -q.x) % self.modulo
        y = (tmp * (p.x - x) - p.y) % self.modulo
        return Point(x, y)

        
    def fermat(self, b, n):
        return pow(b, -1, n)

    def rev(self, b, modulo = modulo):
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

    def mulk(self, k):
        scalar_bin = str(bin(k))[2:]
        G_p = Point(self.Gx, self.Gy)
        for i in range(1, len(scalar_bin)):
            tmp = ( (3 * (G_p.x ** 2)) * self.rev(2 * G_p.y) ) % self.modulo
            x   = (tmp ** 2 - 2 * G_p.x) % self.modulo
            y   = (tmp * (G_p.x - x) - G_p.y) % self.modulo
            G_p.x = x
            G_p.y = y
            if scalar_bin[i] == "1":
                tmp = ( (self.y-G_p.y) * self.rev(self.x-G_p.x) ) % self.modulo
                x = (tmp ** 2 - G_p.x -self.x) % self.modulo
                y = (tmp * (G_p.x - x) - G_p.y) % self.modulo
                G_p.x = x
                G_p.y = y
        return G_p
