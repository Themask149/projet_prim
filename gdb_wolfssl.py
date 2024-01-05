#!/usr/bin/env python3

import gdb
import secrets
import re
import matplotlib.pyplot as plt
import time 
import json
import numpy as np 

cycle_tab=[]
address_cyccnt="0xE0001004"


class MyCommand(gdb.Command):
    def __init__(self):
        print("random_multiply init")
        super(MyCommand, self).__init__("random_multiply", gdb.COMMAND_USER)
        gdb.execute("target extended-remote :3333")
        gdb.execute("load")
        gdb.execute("mon reset halt")
        gdb.execute("break main")
        gdb.execute("continue")
        gdb.execute("set pagination off")
        gdb.execute("set python print-stack full")
        print("random_multiply init done")

    def invoke(self, arg, from_tty):
        t = time.time()
        print("random_multiply invoke")
        #Ici on met les breakpoints pour la fonction que l'on veut tester
        gdb.execute("b *curve25519+354")
        gdb.execute("b *curve25519+358")
        gdb.execute("b *main+54")
        token=secrets.token_hex(32)
        for j in range(32):
            gdb.execute("set (byte) aes_key["+str(j)+"]=0x"+token[2*j:2*j+2])
        token=secrets.token_hex(16)
        for j in range(16):
            gdb.execute("set (byte) iv["+str(j)+"]=0x"+token[2*j:2*j+2])
        print("Setting number of test \n")
        nbloop=re.findall(r'\d+', arg)
        if len(nbloop) == 0:
            nbloop=1
        else:
            nbloop=int(nbloop[0])
        gdb.execute("set nbtest="+str(nbloop))
        gdb.execute("continue")
        for i in range(nbloop):
            print("")
            gdb.execute("p/a in")
            gdb.execute("set *(int*)("+address_cyccnt+")=0")
            gdb.execute("continue")
            res = int.from_bytes(gdb.selected_inferior().read_memory(int(address_cyccnt, 16), 4).tobytes(), 'little')
            cycle_tab.append(int(res))
            gdb.execute("continue")
            print("Cycle count : "+str(res)+"\n")
        print("C'est fini en +"+str(time.time()-t)+"!\n")
        save_results()

MyCommand()

def save_results():

    with open("results_wolfssl.txt",'a') as f:
        f.write("\n\nPour la fonction fe_cswap ter:")
        # json.dump(cycle_tab, f)
        f.write("\nVoici les valeurs uniques ")
        uniquetab=np.unique(cycle_tab)
        np.savetxt(f, uniquetab, fmt='%d')
        f.write("\nLe nombre de valeur unique est "+ str(len(uniquetab)))


    # plt.hist(cycle_tab, bins=25)

    # plt.xlabel('Nb of cycles')
    # plt.ylabel('Frequency')
    # plt.title('Histogram for multiply function')

    # plt.savefig('histogram.png')
