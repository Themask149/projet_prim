#!/usr/bin/env python3

import gdb
import secrets
import re

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
        print("random_multiply init done")

    def invoke(self, arg, from_tty):
        print("random_multiply invoke")
        gdb.execute("b *main+8")
        gdb.execute("b *main+58")
        gdb.execute("b *multiply+24")
        gdb.execute("b *multiply+28")
        gdb.execute("continue")
        print("Setting number of test \n")
        nbloop=re.findall(r'\d+', arg)
        if len(nbloop) == 0:
            nbloop=1
        else:
            nbloop=int(nbloop[0])
        gdb.execute("set nbtest="+str(nbloop))
        gdb.execute("continue")
        gdb.execute("p/a nbtest")
        for i in range(nbloop):
            print("Test "+str(i)+"\n")
            token=secrets.token_hex(32)
            for j in range(32):
                gdb.execute("set (char) s["+str(j)+"]=0x"+token[2*j:2*j+2])
            print("Token : "+token+"\n")
            gdb.execute("continue")
            gdb.execute("set *(int32_t*)("+address_cyccnt+")=0")
            gdb.execute("continue")
            res=gdb.parse_and_eval(address_cyccnt)
            cycle_tab.append(res)
            gdb.execute("continue")
            print("Cycle count : "+str(res)+"\n")
        print("C'est fini !\n")
        print(cycle_tab)

MyCommand()