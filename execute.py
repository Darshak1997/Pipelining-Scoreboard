#! python
# (c) DL, UTA, 2009 - 2018
import  sys, string, time
import numpy as np
import pandas as pd
wordsize = 31                                        # everything is a word
numregbits = 3                                       # actually +1, msb is indirect bit
opcodesize = 7
addrsize = wordsize - (opcodesize+numregbits+1)      # num bits in address
memloadsize = 1024                                   # change this for larger programs
numregs = 2**numregbits
regmask = (numregs*2)-1                              # including indirect bit
addmask = (2**(wordsize - addrsize)) -1
nummask = (2**(wordsize))-1
opcposition = wordsize - (opcodesize + 1)            # shift value to position opcode
reg1position = opcposition - (numregbits +1)            # first register position
reg2position = reg1position - (numregbits +1)
reg3position = reg2position - (numregbits +1)
reg5position = reg3position - (numregbits +1)
memaddrimmedposition = reg5position                  # mem address or immediate same place as reg2
realmemsize = memloadsize * 1                        # this is memory size, should be (much) bigger than a program
#memory management regs
codeseg = numregs - 1                                # last reg is a code segment pointer
dataseg = numregs - 2                                # next to last reg is a data segment pointer
#ints and traps
trapreglink = numregs - 3                            # store return value here
trapval     = numregs - 4                            # pass which trap/int
mem = [0] * realmemsize                              # this is memory, init to 0
reg = [0] * numregs                                  # registers
clock = 1                                            # clock starts ticking
ic = 0                                               # instruction count
numcoderefs = 0                                      # number of times instructions read
numdatarefs = 0                                      # number of times data read
starttime = time.time()
curtime = starttime
scoreboard=[100]
datahazards = 0


def startexechere ( p ):
    # start execution at this address
    reg[ codeseg ] = p
def loadmem():                                       # get binary load image
  curaddr = 0
  for line in open("a.out", 'r').readlines():
    token = string.split( string.lower( line ))      # first token on each line is mem word, ignore rest
    if ( token[ 0 ] == 'go' ):
        startexechere(  int( token[ 1 ] ) )
    else:
        mem[ curaddr ] = int( token[ 0 ], 0 )
        curaddr = curaddr = curaddr + 1
def getcodemem ( a ):
    # get code memory at this address
    memval = mem[ a + reg[ codeseg ] ]
    return ( memval )
def getdatamem ( a ):
    # get code memory at this address
    memval = mem[ a + reg[ dataseg ] ]
    return ( memval )
def getregval ( r ):
    # get reg or indirect value
    if ( (r & (1<<numregbits)) == 0 ):               # not indirect
       rval = reg[ r ]
    else:
       rval = getdatamem( reg[ r - numregs ] )       # indirect data with mem address
    return ( rval )
def checkres( v1, v2, res):
    v1sign = ( v1 >> (wordsize - 1) ) & 1
    v2sign = ( v2 >> (wordsize - 1) ) & 1
    ressign = ( res >> (wordsize - 1) ) & 1
    if ( ( v1sign ) & ( v2sign ) & ( not ressign ) ):
      return ( 1 )
    elif ( ( not v1sign ) & ( not v2sign ) & ( ressign ) ):
      return ( 1 )
    else:
      return( 0 )
def dumpstate ( d ):
    if ( d == 1 ):
        print reg
    elif ( d == 2 ):
        print mem
    elif ( d == 3 ):
        print 'clock=', clock, 'pipelined Clock=', pipelinedclock, 'IC=', ic, 'Coderefs=', numcoderefs,'Datarefs=', numdatarefs, 'Start Time=', starttime, 'Currently=', time.time()
        print 'datahazards : ', datahazards
        # print '------ | SCOREBOARD |-------'
        # print df
        print '------ | DIRECT MAPPED UNIFIED |-----'
        print dm11
        print '-------------'
        print dm22
        print '-------------------------'
        print dm3

def hazards(ip):
    global datahazards
    reg1 = (ir >> reg1position) & regmask
    reg2 = (ir >> reg2position) & regmask
    ip = ip + 1
    ij = getcodemem(m)
    reg3 = (ir >> reg3position) & regmask
    reg4 = (ir >> reg4position) & regmask
    ip = ip + 1
    ik = getcodemem(m)
    reg5 = (ir >> reg5position) & regmask
    reg6 = (ir >> reg6position) & regmask
    if((reg2 == reg3) | (reg2 == reg5) | (reg2 == reg1)):
        datahazards = datahazards + 1
    return ip

def trap ( t ):
    # unusual cases
    # trap 0 illegal instruction
    # trap 1 arithmetic overflow
    # trap 2 sys call
    # trap 3+ user
    rl = trapreglink                            # store return value here
    rv = trapval
    if ( ( t == 0 ) | ( t == 1 ) ):
       dumpstate( 1 )
       dumpstate( 2 )
       dumpstate( 3 )
       dumpstate( 4 )
    elif ( t == 2 ):                          # sys call, reg trapval has a parameter
       what = reg[ trapval ]
       if ( what == 1 ):
           a = a        #elapsed time
    return ( -1, -1 )
    return ( rv, rl )
# opcode type (1 reg, 2 reg, reg+addr, immed), mnemonic
opcodes = { 1: (2, 'add'), 2: ( 2, 'sub'),
            3: (1, 'dec'), 4: ( 1, 'inc' ),
            7: (3, 'ld'),  8: (3, 'st'), 9: (3, 'ldi'),
           12: (3, 'bnz'), 13: (3, 'brl'),
           14: (1, 'ret'),
           16: (3, 'int') }
startexechere( 0 )                                  # start execution here if no "go"
loadmem()                                           # load binary executable
ip = 0

ip1 = range(26)
dict  = {0:'R0' , 1:'R1' , 2:'R2' , 3:'R3' , 4:'R4' , 5:'R5' , 6:'R6' , 7:'R7'}
df = pd.DataFrame( columns = ['Instructions','R0','R1','R2','R3','R4','R5','R6','R7'])
# data1 = '-'
dict1 = {55141496: 'Word0', 55141472: 'Word1'}
dm11 = pd.DataFrame(index=range(4), columns=['Word0', 'Word1'])
# dash1 = '-'
dm22 = pd.DataFrame(index=range(4), columns=['Word0', 'Word1', 'Word2', 'Word3'])
# dash2 = '-'
dm3 = pd.DataFrame( index = range(8) , columns = ['Word0' , 'Word1'])

                                            # start execution at codeseg location 0
# while instruction is not halt
while( 1 ):
   ir = getcodemem(ip)                            # - fetch
   ip = ip + 1
   data = ip
   for numdatarefs in range(1,ip):                 # Data Reference
       numdatarefs = numdatarefs + 1

   opcode = ir >> opcposition                       # - decode
   reg1   = (ir >> reg1position) & regmask
   reg2   = (ir >> reg2position) & regmask
   reg3   = (ir >> reg3position) & regmask
   reg5   = (ir >> reg5position) & regmask
   addr   = (ir) & addmask
   ic = ic + 1
   pipelinedclock = 5 + ic - 1
#   for data11 in range(1, 1):
   data11 = id(ip)
   print data11
#   xyz = dict1[data11]
#   dm11 = dm11.append({data11: ip}, ignore_index=True)
#   print dm11



   for numcoderefs in range(1,pipelinedclock):     # Code Reference
       numcoderefs = numcoderefs + 1

   if opcode ==12 or opcode == 13:                  # Control Hazard Implementation
       print '------Control Hazard-------'




#    if ip == 1:
#        print 'IF : ', reg1
# #       print 'ID  : ', opcode
#        if opcode == 7 or opcode == 9 and ip == ip + 1:
#            print 'read/write', reg1
#        elif opcode == 8 and ip == ip + 1:
#            print 'write', opcode







                                                    # - operand fetch
   if not (opcodes.has_key( opcode )):
      tval, treg = trap(0)
      if (tval == -1):                              # illegal instruction
         break
   memdata = 0                                      #     contents of memory for loads
   if opcodes[ opcode ] [0] == 1:                   #     dec, inc, ret type
      operand1 = getregval( reg1 )                  #       fetch operands
   elif opcodes[ opcode ] [0] == 2:                 #     add, sub type
      operand1 = getregval( reg1 )                  #       fetch operands
      operand2 = getregval( reg2 )
   elif opcodes[ opcode ] [0] == 3:                 #     ld, st, br type
      operand1 = getregval( reg1 )                  #       fetch operands
      operand2 = addr
   elif opcodes[ opcode ] [0] == 0:                 #     ? type
      break
   if (opcode == 7):                                # get data memory for loads
      memdata = getdatamem( operand2 )
   # execute
   if opcode == 1:                     # add
      result = (operand1 + operand2) & nummask
      if ( checkres( operand1, operand2, result )):
         tval, treg = trap(1)
         if (tval == -1):                           # overflow
            break
   elif opcode == 2:                   # sub
      result = (operand1 - operand2) & nummask
      if ( checkres( operand1, operand2, result )):
         tval, treg = trap(1)
         if (tval == -1):                           # overflow
            break
   elif opcode == 3:                   # dec
      result = operand1 - 1
   elif opcode == 4:                   # inc
      result = operand1 + 1
   elif opcode == 7:                   # load
      result = memdata
   elif opcode == 8:                   # store
       result = operand1
   elif opcode == 9:                   # load immediate
      result = operand2
   elif opcode == 12:                  # conditional branch
      result = operand1
      if result <> 0:
         ip = operand2
   elif opcode == 13:                  # branch and link
      result = ip
      ip = operand2
   elif opcode == 14:                   # return
      ip = operand1
   elif opcode == 16:                   # interrupt/sys call
      result = ip
      tval, treg = trap(reg1)
      if (tval == -1):
        break
      reg1 = treg
      ip = operand2
   # write back
   if ( (opcode == 1) | (opcode == 2 ) |
         (opcode == 3) | (opcode == 4 ) ):     # arithmetic
        reg[ reg1 ] = result
   elif ( (opcode == 7) | (opcode == 9 )):     # loads
        reg[ reg1 ] = result
   elif (opcode == 8 ):                        # store
       mem[addr + reg[dataseg]] = result
   elif (opcode == 13):                        # store return address
        reg[ reg1 ] = result
   elif (opcode == 16):                        # store return address
        reg[ reg1 ] = result

        # SCOREBOARD ##
   if ((opcode == 8) | (opcode == 12) | (opcode == 13)):
       data = reg1
       value = 'R'
       dm = dict[data]
       # print data
   elif ((opcode == 3) | (opcode == 4) | (opcode == 7) | (opcode == 9)):
       data1 = reg1
       value = 'W'
       dm = dict[data1]
#       print data1
   elif ((opcode == 1) | (opcode == 2)):
       data2 = reg1
       value1 = 'R'
       dm1 = dict[data2]
       data3 = reg2
       value2 = 'R/W'
       dm2 = dict[data3]
       df = df.append({'Instructions': ip, dm1: value1, dm2: value2}, ignore_index=True)
       continue
   df = df.append({'Instructions': ip, dm: value}, ignore_index=True)
   # end of instruction loop
df = df.fillna('-')
print '--------ScoreBoard---------'
print df
# end of execution









# Cache Implementation #
#dm11 = dm1.append(pd.DataFrame(data = id(ip))