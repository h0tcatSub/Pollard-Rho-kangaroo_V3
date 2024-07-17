global modulo
class Point:
    modulo = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    order  = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
    x  = 0
    y  = 0

    def __init__(self, order = order, modulo = modulo, x=Gx, y=Gy):
        self.x = x
        self.y = y
        self.order  = order
        self.modulo = modulo
    
    def __str__(self):
        return f"{self.x}\t{self.y}"

    def __mod__(self, q):
        return Point(self.x % q, self.y % q)

    def __mul__(self, b):
        if type(b) == Point:
            return self.double(b)
        return self.mulk(b)
    
    def __eq__(self, Q):
        match_x = self.x == Q.x
        match_y = self.y == Q.y

        matched_point = match_x and match_y
        return matched_point


    def __sub__(self, Q): #これは普段使いません。 離散対数問題や攻撃には使えるかも...?
        diff_point = Point(self.x - Q.x, self.y - Q.y)
        return diff_point


    def __add__(self, q):
        if(q == self):
            tmp = ( (3 * (q.x ** 2)) * self.rev(2 * q.y) ) % self.modulo
            self.x   = (tmp ** 2 - 2 * q.x)    % self.modulo
            self.y   = (tmp * (q.x - self.x) - q.y) % self.modulo
        else:
            tmp = ( (q.y-self.y) * self.rev(q.x-self.x) ) % self.modulo
            self.x = (tmp ** 2 - self.x -q.x) % self.modulo
            self.y = (tmp * (self.x - self.x) - self.y) % self.modulo

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
        if type(b) == float:
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


    def mul2(self, P, R):
        c = 3*P.x*P.x*self.rev(2*P.y, self.modulo) % self.modulo
        R.x = (c*c-2*P.x) % self.modulo
        R.y = (c*(P.x - R.x)-P.y) % self.modulo
        return R

    def mulk(self, k):
        G = Point()
        G_p = Point()
        scalar_bin = str(bin(k))[2:]
        for i in range (1, len(scalar_bin)):
            G_p = self.double(G_p)#self.mul2(G_p, G_p)
            if scalar_bin[i] == "1":
                G_p = self.add(G_p, G)
        return G_p
