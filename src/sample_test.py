from ECC import Point

import numpy as np
import time

def solve_rho(G, Y, bits_size):

    starttime = time.time()
    q = Y.order

    print(f'order = {q}')

    if sum(np.isin(G, Y)) > 0:
        print(G)
        print()
        print(f"sol. time: {format((time.time()-starttime))} sec")
        print()
        print("Kamijo Touma >> Kill that illusion!!")
        key = np.where(G == Y)[0][0] + 1
        assert G * key == Y
        print(f"Private Key : 0x{format(key, '064x')}")
        print("[+] OK.")
        return key

    def new_xab(x, a, b, g, y, q):
        try:
            subset = Y.x % 3
        except ZeroDivisionError:
            subset = 2
        if subset == 0:
            return (x+x, (a*2) % q, (b*2) % q)
        if subset == 1:
            return (x+g, (a+1) % q, b        )
        if subset == 2:
            return (x+y, a        , (b+1) % q)
    print("Please wait...")
    x, a, b = G, np.arange(1, bits_size), np.arange(1, bits_size)
    X, A, B = x, np.arange(1, bits_size), np.arange(1, bits_size)
    for i in range(17, q, bits_size):
        x, a, b = new_xab(x, a, b,  G, Y, q)
        X, A, B = new_xab(X, A, B,  G, Y, q)
        X, A, B = new_xab(X, A, B,  G, Y, q)
        print(f"{i}: {x} , {X}", end="\r")
        if np.any(x == X):#sum(x == X) > 0:
            print()
            print("[+] Found Collision Pair!!")
            break

    print()
    print(f"sol. time: {(time.time()-starttime)} sec")
    print()
    print("Kamijo Touma >> Kill that illusion!!")
    print()
    def calculate_key_from_aAbB(a, A, b, B):
        return ((a - A) * pow(B - b, -1, q)) % q
    calculate_key_from_aAbB = np.vectorize(calculate_key_from_aAbB)
    res = calculate_key_from_aAbB(a, A, b, B)#((a - A) * pow(B - b, -1, q)) % q

    check_point = G * res
    if sum(check_point == Y) > 0:

        res = np.where(check_point == Y)[0][0] + 1
        print(f"Private Key : 0x{format(res, '064x')}")
        assert G * res == Y
        print("[+] OK.")
        return res

    return None


def main():
    #x  = 0xc6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7abac09b95c709ee5
    #y  = 0x1ae168fea63dc339a3c58419466ceaeef7f632653266d0e1236431a950cfe52a
    # 0x20000 Point
    x = 0x4c1b9866ed9a7e9b553973c6c93b02bf0b62fb012edfb59dd2712a5caf92c541
    y = 0xe60fce93b59e9ec53011aabc21c23e97b2a31369b87a5ae9c44ee89e2a6dec0a #0xc1f792d320be8a0f7fbcb753ce56e69cc652ead7e43eb1ad72c4f3fdc68fe020
    bits_size = 2 ** 10
    G = Point(Point.Gx, Point.Gy)
    Q = Point(x, y)
    
    print("-" * 20)
    print()
    print(f"Prime   : {format(G.modulo, '064x')}")
    print(f"Order   : {format(G.order, '064x')}")
    print(f"Point X : {format(x, '064x')}")
    print(f"Point y : {format(y, '064x')}")
    print()
    print("-" * 20)
    print()
    # ---- WIP ----
    keys = np.arange(1, bits_size)
    pub_keys = np.array([])
    for k in keys:
        pub_keys = np.append(pub_keys, G * k)
        print(f"Generating Public_keys.... [{k} / {bits_size}]", end="\r")
    print()
    print("[+] Start analysis... Kill that elliptic curve cryptography!!")
    private_key = solve_rho(pub_keys, Q, bits_size)
    file = open("FOUND_KEYS.txt", "w+")
    file.writelines(format(private_key, '064x'))
    file.close()
    
if __name__ == "__main__":
    main()