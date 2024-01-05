import numpy as np
import re
import sys
indices = [m.start() for m in re.finditer('/', __loader__.path)]
sys.path.insert(0, __loader__.path[:indices[-2] + 1] + 'host/lib/scope/')

import infiniium

sys.path = sys.path[1:]

import pickle

N_TRACES = 100
N_POINTS = 1500000

traces = np.zeros((N_TRACES, N_POINTS), dtype=np.int8)

# 070323 test speed compared to my lib - understand why acquisitions are so slow

inst = infiniium.infiniium('DSO90404A')
inst.setup('stm32_g4nucl_aes256_1_5M.set')

i = 0
while i < N_TRACES:
    inst.digit()
    inst.wait_acq()

    trace = inst.get_wave('CHAN3')
    trace = np.frombuffer(trace, dtype=np.int8)
    traces[i] = trace

    i += 1

f_traces = open('/media/varillon/My Book/test_jtag_free/traces', 'wb')
pickle.dump(traces, f_traces)
f_traces.close()
