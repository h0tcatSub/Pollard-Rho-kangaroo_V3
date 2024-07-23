from Anomalous_secp256k1 import Point

import ECC
import time

## --- Thanks Bro
def hensel_lift(P, p = Point.order):
    a = 0
    b = 7
    x = P.x
    y = P.y
    s = ((x ** 3 + a*x + b - y ** 2) // p) % p
    s = pow(s, 2 * y, p)
    print(x, (y + p * s) % p)
    return (x, (y + p * s) % p)

def lambda_E(P):
    x1 = P.x
    y1 = P.y
    print(x1, y1)
    P2 = (P * (P.order - 1))
    xp_1 = P2.x
    yp_1 = P2.y
    print(xp_1, yp_1)
    res = (((((xp_1 - x1) / P.order)) % P.order) % P.order) / (yp_1 - y1)
    print(res)
    assert res != 0
    return res

def SSSA_attack(P, Q, p = Point.order):

    Px, Py = P = hensel_lift(P)
    Qx, Qy = Q = hensel_lift(Q)
    A = ((Qy ** 2 - Py ** 2) - (Qx ** 3 - Px ** 3)) / (Qx - Px)
    B = Py ** 2 - Px ** 3
    print(P)
    print(Q)
    #R = Zmod(p^2)
    R = p ** 2
    print(R)
    P = Point(Px, Py, R, R)
    Q = Point(Qx, Qy, R, R)
    print(P)
    print(Q)
    #lE = LE#(, A, B])
    #P, Q = lE(P), lE(Q)
    return lambda_E(Q) / lambda_E(P)


G = ECC.Point(ECC.Point.Gx, ECC.Point.Gy)
Y = G * 3
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
key = round(SSSA_attack(AY, AG)) + 1

found_key = False
print("その楕円曲線暗号をぶち壊す!!")

try:
    assert G * key == Y
    print("OK")
    print(f'Private Key : {format(key, "064x")}')
    found_key = True
except:
    print("Second Check...")
    if(key == 0): #ズレが生じた場合の処理
        print("Plus Check")
        if G * (key + 1) == Y:
            key += 1
            print(f'Private Key : {format(key, "064x")}')
            found_key = True
    else:
        if G * key == Y:
            print(f'Private Key : {format(key, "064x")}')
            found_key = True
        else:
            print("Minus Check")
            if G * (key - 1) == Y:
                key -= 1
                print(f'Private Key : {format(key, "064x")}')
                found_key = True
            else:
                print("Plus Check")
                if G * (key + 1) == Y:
                    key += 1
                    print(f'Private Key : {format(key, "064x")}')
                    found_key = True

if found_key:
    key = format(key, "064x")
    file = open("FOUND_KEY.txt", "a+")
    file.writelines(f"Private Key : {key}\n")
    file.close()
    print("Success !!")
else:
    print("Failed.... :(")