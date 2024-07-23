from Anomalous_secp256k1 import Point

import ECC
import time
import math
## --- Thanks Bro
def hensel_lift(P, p = Point.order):
    a = 0
    b = 7
    x = P.x
    y = P.y
    s = ((x ** 3 + a*x + b - y ** 2) // p) % p
    t = pow(s, 2 * y, p)
    s = (s * t) % p
    return (x, (y + p * s) % p)

def lambda_E(P, p):
    x1 = P.x
    y1 = P.y
    P2 = (P * (p - 1))
    xp_1 = P2.x
    yp_1 = P2.y
    res = (((((((xp_1 - x1) / (p ** 2)) % (xp_1 - x1)))) / (yp_1 - y1)) % (p ** 2))
    #assert res != 0
    return res

def SSSA_attack(P, Q, p = Point.order):

    Px, Py = P = hensel_lift(P)
    Qx, Qy = Q = hensel_lift(Q)
    A = ((Qy ** 2 - Py ** 2) - (Qx ** 3 - Px ** 3)) / (Qx - Px)
    B = Py ** 2 - Px ** 3
    #R = Zmod(p^2)
    R = p ** 2
    P = Point(Px, Py, R, R)
    Q = Point(Qx, Qy, R, R)
    #lE = LE#(, A, B])
    #P, Q = lE(P), lE(Q)
    return lambda_E(P, Point.order) // lambda_E(Q, Point.order)

found_key_count = 0
test_count = 0x10000
found_key_list = []
for i in range(2, test_count + 1):
    G = ECC.Point(ECC.Point.Gx, ECC.Point.Gy)
    Y = G * i
    print("-" * 20)
    AG = Point(Point.Gx, Point.Gy)
    print(f"Target X: {format(Y.x, '064x')}")
    print(f"Target X: {format(Y.y, '064x')}")
    print()
    #AY  = AG * 10000000
    print()
    print("強固な楕円曲線暗号に対して強制干渉を開始 . . .")
    print("")
    AY = AG * Y
    print("S S S A")
    print()
    print(f"Forged X: {format(AY.x, '064x')}")
    print(f"Forged Y: {format(AY.y, '064x')}")
    print("")
    print("対secp256k1用の術式を組み込み中... 第一式、第二式、第三式。")
    print("命名、『神よ、何故私を見捨てたのですか』完全発動まで十二秒")
    print()
    time.sleep(1)
    #for i in range(12):
    #    print(f"{12 - i}...")
    #    time.sleep(1)
    print()
    print()
    print()
    key = int(((SSSA_attack(AY, AG))) + 1)

    found_key = False
    print("その楕円曲線暗号をぶち壊す!!")

    try:
        assert G * key == Y
        print("OK")
        found_key = True
    except:
        # -- Special Check
        print("Second Check...")
        print("Plus Check")
        rev_SSSA =  int((SSSA_attack(AG, AY))) + 1
        if G * rev_SSSA  == Y:
            key = rev_SSSA
            found_key = True
        if G * (key + 1) == Y:
            key += 1
            found_key = True
        else:
            if G * key == Y:
                found_key = True
            elif G * (key + 3) == Y:
                key += 3
                found_key = True
            elif G * (key + 7) == Y:
                key += 7
                found_key = True
            else:
                print("Minus Check")
                if G * (key - 1) == Y:
                    key -= 1
                    found_key = True
                elif G * (key * 2) == Y:
                    key *= 2
                    found_key = True
                elif G * (key // 2) == Y:
                    key //= 2
                    found_key = True
                else:
                    print("Plus Check")
                    if G * (key + 1) == Y:
                        key += 1
                        found_key = True

    if found_key:
        found_key_count += 1
        key = format(key, "064x")
        print(f"Private Key : {key}")
        print("Success !!")
        found_key_list.append(key)
    else:
        print("Failed.... :(")
    print(f"倒したsecp256k1の数 :  {found_key_count}")
    print(f"出題範囲 : 2 - {test_count}")
    print(f"倒せた率 : {(found_key_count / test_count) * 100}%")

print("-" * 20)
print(f"出題範囲 : 1 - {test_count}")
print(f"倒したsecp256k1の合計 :  {found_key_count}")
print(f"最終倒せた率 : {(found_key_count / test_count) * 100}%")
print(found_key_list)