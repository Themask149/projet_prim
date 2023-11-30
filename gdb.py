#!/usr/bin/env python3

import gdb
import secrets
import re

import time

cycle_tab=[]
address_cyccnt="0xE0001004"

P = 2 ** 255 - 19
_A = 486662

def _point_add(point_n, point_m, point_diff):
    (xn, zn) = point_n
    (xm, zm) = point_m
    (x_diff, z_diff) = point_diff
    x = (z_diff << 2) * (xm * xn - zm * zn) ** 2
    z = (x_diff << 2) * (xm * zn - zm * xn) ** 2
    return x % P, z % P

def _point_double(point_n):
    (xn, zn) = point_n
    xn2 = xn ** 2
    zn2 = zn ** 2
    x = (xn2 - zn2) ** 2
    xzn = xn * zn
    z = 4 * xzn * (xn2 + _A * xzn + zn2)
    return x % P, z % P

def _const_time_swap(a, b, swap):
    index = int(swap) * 2
    temp = (a, b, b, a)
    return temp[index:index+2]

def _raw_curve25519(base, n):
    zero = (1, 0)
    one = (base, 1)
    mP, m1P = zero, one

    for i in reversed(range(256)):
        bit = bool(n & (1 << i))
        mP, m1P = _const_time_swap(mP, m1P, bit)
        mP, m1P = _point_double(mP), _point_add(mP, m1P, one)
        mP, m1P = _const_time_swap(mP, m1P, bit)

    x, z = mP
    inv_z = pow(z, P - 2, P)
    return (x * inv_z) % P

def curve25519_base(scalar):
    return _raw_curve25519(9, scalar)

class MyCommand(gdb.Command):
    def __init__(self):
        print("random_multiply init")
        super(MyCommand, self).__init__("random_multiply", gdb.COMMAND_USER)
        gdb.execute("target extended-remote :3333")
        gdb.execute("load")
        gdb.execute("mon reset halt")
        gdb.execute("b main")
        gdb.execute("continue")
        print("random_multiply init done")

    def invoke(self, arg, from_tty):
        print("random_multiply invoke")
        gdb.execute("b *0x800bdcc")
        gdb.execute("b *0x800bda2")
        gdb.execute("b *0x800bda6")
        gdb.execute("b *0x800bde0")
        #gdb.execute("b *main+8")
        #gdb.execute("b *main+58")
        #gdb.execute("b *multiply+24")
        #gdb.execute("b *multiply+28")
        #gdb.execute("continue")
        print("Setting number of test \n")
        nbloop=re.findall(r'\d+', arg)
        if len(nbloop) == 0:
            nbloop=1
        else:
            nbloop=int(nbloop[0])
        print(nbloop)
        gdb.execute("set nbtest="+str(nbloop))
        print("nbtest:")
        gdb.execute("p/d nbtest")
        gdb.execute("continue")
        gdb.execute("p/x $pc")
        for i in range(nbloop):
            print("Test "+str(i)+"\n")
            token=secrets.token_hex(32)
            for j in range(32):
                gdb.execute("set (char) s["+str(j)+"]=0x"+token[2*j:2*j+2])
            print("s:")
            gdb.execute("p/x s")
            print("Token : "+token+"\n")
            #PROBLEM
            gdb.execute("continue")
            gdb.execute("p/x $pc")
            gdb.execute("set *(int32_t*)("+address_cyccnt+")=0")
            gdb.execute("continue")
            #res=gdb.parse_and_eval(address_cyccnt) !!! WRONG
            res = int.from_bytes(gdb.selected_inferior().read_memory(int(address_cyccnt, 16), 4).tobytes(), 'little')
            cycle_tab.append(res)
            print("Cycle count : "+str(res)+"\n")
            gdb.execute("continue")
            print("x:")
            gdb.execute("p/x *s@32")
            print(hex(curve25519_base(int(token, 16))))
            time.sleep(5)
            gdb.execute("continue")
        print("C'est fini !\n")
        print(cycle_tab)

MyCommand()
