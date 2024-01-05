import socket
import time

# TODO here: ssh -4 -f -oProxyJump=ssh.enst.fr -L 18743:dso90404a.enst.fr:5025 attack7 -N
# auto choose port available, just ask user whether port forwarding should be performed
# ??? create another module for this (might be reused for other probes)
# TODO Programming Guide, Chapter 4: queries are (for the most part) blocking and commands can (for the most part) be run concurrently. WAVeform:DATA? = query -> blocking, so cannot rearm scope until trace has been completely sent by scope

class infiniium:
    '''
   Class for controlling Agilent Infiniium oscilloscopes.
   '''
    
    def __init__(self, HOST, PORT = 5025):
        self._infiniium__TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)

        forwarding_port = -1
        while forwarding_port < 0:
            try:
                forwarding_port = int(input(
                    'Is there a port forwarding via SSH running (indicate said '
                    'port, 0 means None)? '
                ))
            except:
                forwarding_port = -1

        self._infiniium__TCP.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        if forwarding_port != 0:
            self._infiniium__TCP.connect(('127.0.0.1', forwarding_port))
        else:
            self._infiniium__TCP.connect((HOST, PORT))
    
        self._infiniium__TCP.sendall('*RST\n'.encode())
        self._infiniium__TCP.sendall('*CLS\n'.encode())

    def __read__(self):
        '''
      Read data from the instrument until terminator character.
      '''
        resp = ''
        EOF = False
        while not EOF:
            buf = self._infiniium__TCP.recv(4096)
            for c in buf:
                if c == ord('\n'):
                    EOF = True
                    break
                resp += chr(c)
        return resp

    def sendcmd(self, cmd):
        '''
      Send the SCPI command <cmd> to the instrument and check if any error occurs.
      '''
        self._infiniium__TCP.sendall((cmd + '\n').encode())
        while True:
            if self.query(':PDER?') == '+0':
                continue
            (code, msg) = self.query('SYSTem:ERRor? STRing').split(',')
            if code != '0':
                self._infiniium__TCP.sendall('*CLS\n'.encode())
                raise RuntimeError(msg)
            return

    
    def query(self, query):
        '''
      Submit the <query> to the instrument, then receipt the response.
      '''
        self._infiniium__TCP.sendall((query + '\n').encode())
        return self.__read__()

    
    def get_ID(self):
        '''
      Return the instrument ID.
      '''
        return self.query('*IDN?')

    
    def setup(self, filename):
        '''
      Load setup <filename> from the disk.
      '''
        cmd = ':DISK:LOAD "%s"' % filename
        self.sendcmd(cmd)

    
    def digit(self):
        '''
      Initialize then acquire displayed channels and functions.
      '''
        self._infiniium__TCP.sendall(':DIGitize\n'.encode())

    
    def get_preamble(self):
        '''
      Output the preamble for the current waveform source.
      '''
        return self.query(':WAVeform:PREamble?')

    
    def wait_acq(self):
        '''
      Block until acquisition is done,
      '''
        while True:
            # TODO as a consequence, no need for a bp at the end of the code to call get_trace, call before encryption, right after probe.arm_scope()
            # change arm_scope to call (launch a thread with? -- append appears to be thread safe) wait_acq() then get_wave() -- I hope that when target reaches a bp and host is busy, requests get queued and are not discarded. CAREFUL, WAVeform:DATA? yields the data associated with the latest trigger only (triggering deletes old samples from memory?) -> single trace.
            # TODO to mitigate problem described in previous sentence, use (at least? compute how many are necessary using, among other things, disk write speed) two buffers in storage: one to store traces when probe adds them, and one being written on the disk in the meantime. Should allow use of thread for writing on disk only, NOT including get_wave (=blocking, see comment at the top)
            if self.query(':ASTate?') == 'ADONE':
                break

            time.sleep(0.001)
        return


    def get_wave(self, src, form = 'BYTE'):
        '''
      Output waveform data of <src>, with form = ASCii|BYTE.
      '''
        cmd = ':WAVeform:SOURce {};FORMat {}'.format(src, form)
        self.sendcmd(cmd)
        if form == 'ASCii':
            return self.query('WAVeform:DATA?').split(',')[:-1]
        if form == 'BYTE' or self.query(':WAVeform:STReaming?') == '0':
            self._infiniium__TCP.sendall('WAVeform:DATA?\n'.encode())
            if self._infiniium__TCP.recv(1) != '#'.encode():
                raise RuntimeError("Expecting '#' at start of response")
            N = int(self._infiniium__TCP.recv(1))
            L = int(self._infiniium__TCP.recv(N))
            wave = ''.encode()

            while len(wave) < L + 1:
                chunk = self._infiniium__TCP.recv(1024)
                if chunk == ''.encode():
                    raise Exception('Connection with probe is broken')
    
                wave += chunk

            wave, ter = wave[:-1], wave[-1]
            if ter != ord('\n'):
                raise RuntimeError("Expecting '\n' at end of response")
            return wave
        raise ValueError('Bad value for <form>')


