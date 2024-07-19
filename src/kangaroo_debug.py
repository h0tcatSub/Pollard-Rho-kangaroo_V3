from math import gcd
from ECC import Point

import random
import numpy as np
import time


def pollard_rho_factorization(n, limit=1000000):
    print("Performing Pollard's Rho factorization...")
    def f(x):
        return (x ** 2 + 1) % n

    x = random.randint(1, n - 1)
    y = x
    d = 1

    while d == 1:
        x = f(x)
        y = f(f(y))
        d = gcd(x - y, n)#(abs(x - y), -1, n) % n

    return d if d != n else None

# Function to perform the Kangaroo algorithm with factors
global starttime
starttime = time.time()
def kangaroo_algorithm(g, h, n, factors, B):
    global starttime

    print("Performing Kangaroo algorithm...")
    P = 0
    Q = 0
    wild_kangaroos = [(random.randint(1, n - 1), random.randint(1, n - 1)) for _ in range(10)]  # Multiple parallel wild kangaroos
    wild_jump_size = random.randint(1, B // 10)  # Randomized wild kangaroo step size
    
    _d = set()
    while True:
        for wild_x, wild_y in wild_kangaroos:
            print(P, B)
            u = wild_x
            v = wild_y
            for _ in range(wild_jump_size):
                u = (g * u) % n
                v = (v * h) % n
            for i in range(len(u)):
                _d[i] = gcd(u[i].x - v, n)
            if ((np.any(1 < _d) and np.any(_d < n))):
                    d = np.where((np.any(1 < _d) and np.any(_d < n)) == True)[0][0] + 1
                    if random.randint(0, 100) >= 20: # 単純に楽しみたいだけ
                        print("Accelerator >> It's a one-way street from here on out!!")
                        print()
                        return d

                    print("Kamijo Touma >> Kill that illusion!!")
                    print()
                    return d
            if np.isin(_d, 1)[0]:
                alpha = kangaroo_attack(P, Q, g, n, h, B, B)  # Using kangaroo_attack
                if np.any(alpha != None):
                    alpha = alpha[alpha != None][0]
                    print()
                    print(f"sol. time: {format((time.time()-starttime), '.2f')} sec")
                    print()
                    if random.randint(0, 100) >= 80: # 単純に楽しみたいだけ
                        print("Accelerator >> It's a one-way street from here on out!!")
                        print()
                        print(f"Alpha : {alpha}")
                        return alpha
                    print("Kamijo Touma >> Kill that illusion!!")
                    print()
                    print(f"Alpha : {alpha}")
                    return alpha
                P += B
                Q += B
            else:
                d = _d[_d != 1][0]
                return d

def kangaroo_attack(P, Q, g, n, h, B, bits_size):
    global starttime
    def inv(g, n = n):
        return pow(int(g), -1, n)
    inv_vec = np.vectorize(inv)
    u = P
    v = Q
    u_iterations = np.arange(0, bits_size)
    v_iterations = np.arange(0, bits_size)
    progress = 0
    while True:
        print(progress, u_iterations, v_iterations)
        # Tame Kangaroo
        u = (u * g) % n
        u_iterations += 1#bits_size

        # Wild Kangaroo
        v = (v * h) % n
        v_iterations += 1

        progress += 1#bits_size
        if np.any(u == v):
            #g = np.where((u == v) == True)[0] + 1
            alpha = ((P - Q) * inv_vec(g, n)) % n  # Inverse of g modulo n
            return alpha

        if (max(u_iterations) > B) and (max(u_iterations) > B):#np.any(max(u_iterations, v_iterations) > B):
            # Maximum iterations reached without collision
            return None


def main():
    G = Point(Point.Gx, Point.Gy)
    p = G.modulo
    n = G.order
    x = 0x5b2c6b57cfdc1bf86dfaadc3c7b10b7bebe5c5e1e415ca92d740c58f3b62e88e#x
    y = 0x5df3b7f51bb5b17ad971a6d0886ebd8b55895e4a62e90c4571662ddbe02e7f5b#y
    Q = Point(x, y)
    bits_size = 2 ** 10#int(args.bits_size)

    keys = np.arange(1, bits_size)
    print("公開鍵配列の生成中...")
    G *= keys#np.append(pub_keys, G * k)
    print("X座標の取得中...")
    print()
    try:
        factors = np.array([pollard_rho_factorization(number) for number in [x, y, x + y]])
        print("Factorization complete:", factors)
    except Exception as e:
        print("Error during factorization:", e)
    print("-" * 20)
    print()
    print(f"Modulo prime number    : {format(p, '064x')}")
    print(f"Order                  : {format(n, '064x')}")
    print(f"Base X                 : {format(Point.Gx, '064x')}")
    print(f"Base Y                 : {format(Point.Gy, '064x')}")
    print(f"Point X                : {format(x, '064x')}")
    print(f"Point Y                : {format(y, '064x')}")
    print()
    print("-" * 20)
    print()

    private_key = kangaroo_algorithm(G, Q, n, factors, bits_size)
    G = Point(Point.Gx, Point.Gy)
    assert (G * private_key) == Q #Final Check

    # ---- WIP ----
    print(f"Generating Public_keys.... ")
    print()
    print("[+] Start analysis... Kill that elliptic curve cryptography!!")
    #private_key = solve_rho(G, Q, bits_size)
    file = open("FOUND_KEYS.txt", "w+")
    file.writelines(format(private_key, '064x'))
    file.close()
    
if __name__ == "__main__":
    main()