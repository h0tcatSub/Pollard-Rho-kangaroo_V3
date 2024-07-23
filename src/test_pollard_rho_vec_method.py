import ECC_special as secc
import ECC as ecc

import argparse


def main():
    G  = ecc.Point(ecc.Point.Gx, ecc.Point.Gy)

    Y = G * 1000
    x = Y.x
    y = Y.y
    Y = secc.Point(x, y)
    bits_size = 8
    x = Y.discrete_log_rho_vetor_method(bits_size=bits_size)
    if x == None:
        print("Failed.")
        exit(0)
    print("Validation...")
    assert G * x == Y
    print("OK.")
    print(f"Private Key : {format(x, '064x')}")
    print("-" * 10)

    G  = ecc.Point(ecc.Point.Gx, ecc.Point.Gy)
    Y = (G * 300)
    x = Y.x
    y = Y.y
    Y = secc.Point(x, y)

    bits_size = 10
    x = Y.discrete_log_rho_vetor_method(bits_size=bits_size)
    if x == None:
        print("Failed.")
        exit(0)
    print("Validation...")
    assert G * x == Y
    print("OK.")
    print(f"Private Key : {format(x, '064x')}")
    print("-" * 10)
    G  = ecc.Point(ecc.Point.Gx, ecc.Point.Gy)
    Y = (G * 0x10000)
    x = Y.x
    y = Y.y
    Y = secc.Point(x, y)

    bits_size = 8
    x = Y.discrete_log_rho_vetor_method(bits_size=bits_size)
    if x == None:
        print("Failed.")
        exit(0)
    print("Validation...")
    assert G * x == Y
    print("OK.")
    print(f"Private Key : {format(x, '064x')}")
    bits_size = 10
    x = Y.discrete_log_rho_vetor_method(bits_size=bits_size)
    if x == None:
        print("Failed.")
        exit(0)
    print("Validation...")
    assert G * x == Y
    print("OK.")
    print(f"Private Key : {format(x, '064x')}")
    
    
if __name__ == "__main__":
    main()