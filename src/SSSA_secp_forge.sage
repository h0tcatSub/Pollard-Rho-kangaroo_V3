#Thanks Bro

def hensel_lift(E, P):
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F#E.base_ring().order()
    a, b = map(ZZ, [E.a4(), E.a6()])
    x, y = map(ZZ, P.xy())
    s = (x^3 + a*x + b - y^2) // p
    s = lift(GF(p)(s) / (2*y))
    return (x, y + p * s)

def lambda_E(E, P):
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F#E.base_ring().order()
    x1, y1 = P.xy()
    xp_1, yp_1 = ((p - 1) * P).xy()
    res = Zmod(p^2)(ZZ(xp_1 - x1) / p) / (yp_1 - y1)
    assert res != 0
    return res

def SSSA_attack(E, P, Q):
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F#E.base_ring().order()
    a, b = E.a4(), E.a6()

    Px, Py = P = hensel_lift(E, P)
    Qx, Qy = Q = hensel_lift(E, Q)
    A = ((Qy^2 - Py^2) - (Qx^3 - Px^3)) / (Qx - Px)
    B = Py^2 - Px^3 - int(a)*Px
    R = Zmod(p^2)
    lE = EllipticCurve(R, [A, B])
    P, Q = lE(P), lE(Q)

    return lambda_E(E, P) / lambda_E(E, Q)


E = EllipticCurve(GF(2 ** 256 - 2 ** 32 - 977), [0, 7])
G = E([55066263022277343669578718895168534326250603453777594175500187360389116729240,
        32670510020758816978083085130507043184471273380659243275938904335757337482424])

SSSA_Attack()