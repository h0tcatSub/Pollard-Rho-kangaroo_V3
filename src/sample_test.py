from ECC import Point

import numpy as np
import time

def solve_rho(G, Y, bits_size):

    starttime = time.time()
    q = Y.order
    print(f'order = {q}')

    pub_keys = np.array([])
    for k in range(1, 4):
        pub_keys = np.append(pub_keys, G * k)

    if sum(np.isin(pub_keys - Y, G)) > 0:
        print(pub_keys)
        print()
        print(f"sol. time: {format((time.time()-starttime))} sec")
        print()
        print("Kamijo Touma >> Kill that illusion!!")
        key = np.where((pub_keys - Y) == G)[0]
        return key

    def new_xab(x, a, b, g, y, q):
        try:
            subset = Y.y % 3
        except ZeroDivisionError:
            subset = 2
        if subset == 0:
            return (x+x, (a*2) % q, (b*2) % q)
        if subset == 1:
            return (x+g, (a+1) % q, b        )
        if subset == 2:
            return (x+y, a        , (b+1) % q)
    x, a, b = Y, np.arange(bits_size), np.arange(bits_size)
    X, A, B = x, np.arange(bits_size), np.arange(bits_size)
    for i in range(1, q, bits_size):
        x, a, b = new_xab(x, a, b,  G, Y, q)
        X, A, B = new_xab(X, A, B,  G, Y, q)
        X, A, B = new_xab(X, A, B,  G, Y, q)
        print(f"{x} , {X}")
        if sum(np.isin((x - X), e)) > 0:
            print("[+] Found Collision Pair!!")
            break

    print()
    print(f"sol. time: {format((time.time()-starttime), '%.2f')} sec")
    print()
    print("Kamijo Touma >> Kill that illusion!!")
    print()
    res = ((a - A) * pow(B - b, -1, q)) % q
    if G * res == Y:
        print(f"Private Key : 0x{format(res, '064x')}")
        assert G * res == Y
        print("[+] OK.")
        return res

    return None


def main():
    x = 0xf9308a019258c31049344f85f89d5229b531c845836f99b08601f113bce036f9
    y = 0x388f7b0f632de8140fe337e62a37f3566500a99934c2231b6cb9fd7584b8e672
    bits_size = 2 ** 16
    G = Point()
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
    #keys = np.arange(1, bits_size)
    #for k in keys:
    #    pub_keys = np.append(pub_keys, G * k)
    #    print(f"Generating Public_keys.... [{k} / {bits_size}]", end="\r")
    print()
    print("[+] Start analysis... Kill that elliptic curve cryptography!!")
    private_key = solve_rho(G, Q, bits_size)
    file = open("FOUND_KEYS.txt", "w+")
    file.writelines(format(private_key, '064x'))
    file.close()
    
if __name__ == "__main__":
    main()