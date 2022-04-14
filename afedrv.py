# afedrv.py
import time
import pyb


def GetVer(id):
    print("Jestem GetVer()\n")
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    # can.clearfilter(0)
    can.send("\x00\x01", id)
    # time.sleep(1)
    # print(can.recv(0))
    buf = bytearray(8)
    lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    can.recv(0, lst)
    print("ID: ", lst[0])
    print("RTR: ", lst[1])
    print("FMI: ", lst[2])
    VerH = (lst[3][2] << 8) | (lst[3][3] & 0xff)
    print("VerH: ", VerH)
    VerL = (lst[3][4] << 8) | (lst[3][5] & 0xff)
    print("VerL: ", VerL)
    VerD = (lst[3][6] << 8) | (lst[3][7] & 0xff)
    print("VerD: ", VerD)


def GetAdc(id, chn):
    print("Jestem AFE_GetAdc()\n")
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    # Send the command to AFE:
    if chn >= 1 and chn <= 3:
        can.send("\x00\x10", id)
    elif chn >= 4 and chn <= 6:
        can.send("\x00\x11", id)
    # Wait and read response
    time.sleep(1)
    buf = bytearray(8)
    lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    can.recv(0, lst)
    print("ID: ", lst[0])
    print("RTR: ", lst[1])
    print("FMI: ", lst[2])
    if chn == 1:
        AdcValue = (lst[3][2] << 8) | (lst[3][3] & 0xff)
        print("adc value of ch", chn, ":", AdcValue, "V")
    elif chn == 2:
        AdcValue = (lst[3][4] << 8) | (lst[3][5] & 0xff)
        print("adc value of ch", chn, ":", AdcValue, "V")
    elif chn == 3:
        AdcValue = (lst[3][6] << 8) | (lst[3][7] & 0xff)
        #AdcValue = AdcValue * (70/4095)
        print("adc value of ch", chn, ":", AdcValue)
    elif chn == 4:
        AdcValue = (lst[3][2] << 8) | (lst[3][3] & 0xff)
        #AdcValue = AdcValue * (70/4095)
        print("adc value of ch", chn, ":", AdcValue)
    elif chn == 5:
        AdcValue = (lst[3][4] << 8) | (lst[3][5] & 0xff)
        print("raw adc value of ch", chn, ":", AdcValue, "I")
        print("adc value of ch [uA]", chn, ":", AdcValue, "I")
    elif chn == 6:
        AdcValue = (lst[3][6] << 8) | (lst[3][7] & 0xff)
        print("adc value of ch", chn, ":", AdcValue, "I")
    return AdcValue


def GetVoltageMasterV(id):
    voltage_bit = GetAdc(id, 3)
    return 0.0183 * voltage_bit - 1.197

def GetVoltageSlaveV(id):
    voltage_bit = GetAdc(id, 4)
    return 0.0183 * voltage_bit - 1.197

def SetDacRAW(id, val1, val2):
    print("Jestem AFE_SetDacRaw()\n")
    # convert data
    #val1conv = ((val1 - 60)/5.2)*255
    #val2conv = ((val2 - 60)/5.2)*255
    #print("dac1: ",int(val1conv),"dac2: ",int(val2conv))
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    # Send the command to AFE:
    buf = bytearray(6)
    buf[0] = 0x00
    buf[1] = 0x12
    buf[2] = (val1 >> 8) & 0xFF
    buf[3] = val1 & 0xFF
    buf[4] = (val2 >> 8) & 0xFF
    buf[5] = val2 & 0xFF
    #buf[2] = int(val1conv)
    #buf[3] = int(val2conv)
    can.send(buf, id)
    time.sleep(1)
    buf2 = bytearray(8)
    lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    print(can.recv(0))
    #can.recv(0, lst)


def SetDac(id, val1, val2):
    print("Jestem AFE_SetDac()\n")
    # convert data
    # val1conv = (-271.2)*val1 + 18142
    # val2conv = (-271.2)*val2 + 18142
    # New voltage calibration AFE v1.1 Kiecana&Bancer 2022-04-13
    val1conv = -0.0941 * val1**3 + 16.282 * val1**2 - 1197.1 * val1 + 34460
    val2conv = -0.0941 * val2**3 + 16.282 * val2**2 - 1197.1 * val2 + 34460

    if int(val1conv) < 0:
        val1conv = 0
    if int(val2conv) < 0:
        val2conv = 0

    print("dac1: ", int(val1conv), "dac2: ", int(val2conv))
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    # Send the command to AFE:
    buf = bytearray(6)
    buf[0] = 0x00
    buf[1] = 0x12
    buf[2] = (int(val1conv) >> 8) & 0xFF
    buf[3] = int(val1conv) & 0xFF
    buf[4] = (int(val2conv) >> 8) & 0xFF
    buf[5] = int(val2conv) & 0xFF
    can.send(buf, id)
    time.sleep(1)
    buf2 = bytearray(8)
    lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    print(can.recv(0))
    #can.recv(0, lst)
    return (int(val1conv), int(val2conv))


def GetTemp(id):
    print("Jestem AFE_Temp()\n")
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    can.send("\x00\x13", id)
    time.sleep(1)
    # print(can.recv(0))
    buf = bytearray(6)
    lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    can.recv(0, lst)
    print("ID: ", lst[0])
    print("RTR: ", lst[1])
    print("FMI: ", lst[2])
    TempVal1 = (lst[3][2] << 8) | (lst[3][3] & 0xff)
    print("temp value 1: ", TempVal1, "bits")
    TempVal2 = (lst[3][4] << 8) | (lst[3][5] & 0xff)
    print("temp value 2: ", TempVal2, "bits")
    return TempVal1,TempVal2


def SetDigRes(id, ch, val):
    print("Jestem SetDigRes()\n")
    # convert data
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    # Send the command to AFE:
    buf = bytearray(4)
    buf[0] = 0x00
    buf[1] = 0xA0
    buf[2] = ((ch) & 0xFF)
    buf[3] = ((val) & 0xFF)
    can.send(buf, id)
    time.sleep(1)
    buf2 = bytearray(8)
    lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    print(can.recv(0))
    #can.recv(0, lst)


def SetHV(id, val):
    print("Jestem SetHV()\n")
    # convert data
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    # Send the command to AFE:
    buf = bytearray(6)
    buf[0] = 0x00
    buf[1] = 0x40
    buf[2] = 0
    buf[3] = 0
    buf[4] = 0
    buf[5] = 1 << val
    can.send(buf, id)
    time.sleep(1)
    # buf2 = bytearray(8)
    # lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    print(can.recv(0))
    #can.recv(0, lst)


def SetAllHV(id):
    print("Jestem SetHV()\n")
    # convert data
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    # Send the command to AFE:
    buf = bytearray(6)
    buf[0] = 0x00
    buf[1] = 0x40
    buf[2] = 0
    buf[3] = 0
    buf[4] = 0
    buf[5] = 3
    can.send(buf, id)
    time.sleep(1)
    # buf2 = bytearray(8)
    # lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    print(can.recv(0))
    #can.recv(0, lst)


def ClrHV(id, val):
    print("Jestem ClrHV()\n")
    # convert data
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    # Send the command to AFE:
    buf = bytearray(6)
    buf[0] = 0x00
    buf[1] = 0x41
    buf[2] = 0
    buf[3] = 0
    buf[4] = 0
    buf[5] = 1 << val
    can.send(buf, id)
    time.sleep(1)
    # buf2 = bytearray(8)
    # lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    print(can.recv(0))
    #can.recv(0, lst)


def ClrAllHV(id):
    print("Jestem ClrHV()\n")
    # convert data
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    # Send the command to AFE:
    buf = bytearray(6)
    buf[0] = 0x00
    buf[1] = 0x41
    buf[2] = 0
    buf[3] = 0
    buf[4] = 0
    buf[5] = 3
    can.send(buf, id)
    time.sleep(1)
    # buf2 = bytearray(8)
    # lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    print(can.recv(0))
    #can.recv(0, lst)


def GetHV(id, val):
    print("Jestem GetHV()\n")
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    can.send("\x00\x42", id)
    time.sleep(1)
    # print(can.recv(0))
    buf = bytearray(6)
    lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    can.recv(0, lst)
    print("ID: ", lst[0])
    print("RTR: ", lst[1])
    print("FMI: ", lst[2])
    HVVal = ((lst[3][5] >> val) & 0x1)
    print("HV val: ", HVVal)


def GetAllHV(id):
    print("Jestem GetHV()\n")
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    can.send("\x00\x42", id)
    time.sleep(1)
    # print(can.recv(0))
    buf = bytearray(6)
    lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    can.recv(0, lst)
    print("ID: ", lst[0])
    print("RTR: ", lst[1])
    print("FMI: ", lst[2])
    HVVal1 = ((lst[3][5] >> 0) & 0x1)
    print("HV val 1: ", HVVal1)
    HVVal2 = ((lst[3][5] >> 1) & 0x1)
    print("HV val 2: ", HVVal2)


def SetCal(id, val):
    print("Jestem SetCal()\n")
    # convert data
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    # Send the command to AFE:
    buf = bytearray(6)
    buf[0] = 0x00
    buf[1] = 0x40
    buf[2] = 0
    buf[3] = 0
    buf[4] = 0
    buf[5] = 1 << (val+2)
    can.send(buf, id)
    time.sleep(1)
    # buf2 = bytearray(8)
    # lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    print(can.recv(0))
    #can.recv(0, lst)


def SetAllCal(id):
    print("Jestem SetCal()\n")
    # convert data
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    # Send the command to AFE:
    buf = bytearray(6)
    buf[0] = 0x00
    buf[1] = 0x40
    buf[2] = 0
    buf[3] = 0
    buf[4] = 0
    buf[5] = 0xC
    can.send(buf, id)
    time.sleep(1)
    # buf2 = bytearray(8)
    # lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    print(can.recv(0))
    #can.recv(0, lst)


def ClrCal(id, val):
    print("Jestem ClrCal()\n")
    # convert data
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    # Send the command to AFE:
    buf = bytearray(6)
    buf[0] = 0x00
    buf[1] = 0x41
    buf[2] = 0
    buf[3] = 0
    buf[4] = 0
    buf[5] = 1 << (val+2)
    can.send(buf, id)
    time.sleep(1)
    # buf2 = bytearray(8)
    # lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    print(can.recv(0))
    #can.recv(0, lst)


def ClrAllCal(id):
    print("Jestem ClrCal()\n")
    # convert data
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    # Send the command to AFE:
    buf = bytearray(6)
    buf[0] = 0x00
    buf[1] = 0x41
    buf[2] = 0
    buf[3] = 0
    buf[4] = 0
    buf[5] = 0xC
    can.send(buf, id)
    time.sleep(1)
    # buf2 = bytearray(8)
    # lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    print(can.recv(0))
    #can.recv(0, lst)


def GetCal(id, val):
    print("Jestem GetCal()\n")
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    can.send("\x00\x42", id)
    time.sleep(1)
    # print(can.recv(0))
    buf = bytearray(6)
    lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    can.recv(0, lst)
    print("ID: ", lst[0])
    print("RTR: ", lst[1])
    print("FMI: ", lst[2])
    HVVal = ((lst[3][5] >> (val+2)) & 0x1)
    print("HV val: ", HVVal)


def GetAllCal(id):
    print("Jestem GetCal()\n")
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    can.send("\x00\x42", id)
    time.sleep(1)
    # print(can.recv(0))
    buf = bytearray(6)
    lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    can.recv(0, lst)
    print("ID: ", lst[0])
    print("RTR: ", lst[1])
    print("FMI: ", lst[2])
    HVVal1 = ((lst[3][5] >> (0+2)) & 0x1)
    print("HV val 1: ", HVVal1)
    HVVal2 = ((lst[3][5] >> (1+2)) & 0x1)
    print("HV val 2: ", HVVal2)
    
   
def SetCtrlLoop(id, ch):
    print("Jestem SetCtrlLoop()\n")
    #convert data
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL,extframe=False,prescaler=54,sjw=1,bs1=7,bs2=2,auto_restart=True)
    #Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    #Send the command to AFE:
    buf = bytearray(6)
    buf[0] = 0x00
    buf[1] = 0x43
    buf[2] = 0
    buf[3] = 0
    buf[4] = 0
    buf[5] = 0x01 << ch
    can.send(buf,id)
    time.sleep(1)
    # buf2 = bytearray(8)
    # lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    print(can.recv(0))
    #can.recv(0, lst)
    
def ClrCtrlLoop(id, ch):
    print("Jestem ClrCtrlLoop()\n")
    #convert data
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL,extframe=False,prescaler=54,sjw=1,bs1=7,bs2=2,auto_restart=True)
    #Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    #Send the command to AFE:
    buf = bytearray(6)
    buf[0] = 0x00
    buf[1] = 0x44
    buf[2] = 0
    buf[3] = 0
    buf[4] = 0
    buf[5] = 0x01 << ch
    can.send(buf,id)
    time.sleep(1)
    # buf2 = bytearray(8)
    # lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    print(can.recv(0))
    #can.recv(0, lst)    
    
def SetConfRaw01(id, ch, vSet, vDelta):
    print("SetConf01()\n")
    #convert data
    #val1conv = ((val1 - 60)/5.2)*255
    #val2conv = ((val2 - 60)/5.2)*255
    #print("dac1: ",int(val1conv),"dac2: ",int(val2conv))
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL,extframe=False,prescaler=54,sjw=1,bs1=7,bs2=2,auto_restart=True)
    #Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    #Send the command to AFE:
    buf = bytearray(6)
    buf[0] = 0x00
    buf[1] = (0x80 + 2*ch)
    buf[2] = (vSet >> 8) & 0xFF
    buf[3] = vSet & 0xFF
    buf[4] = (vDelta >> 8) & 0xFF
    buf[5] = vDelta & 0xFF
    #buf[2] = int(val1conv)
    #buf[3] = int(val2conv)
    can.send(buf,id)
    time.sleep(1)
    buf2 = bytearray(6)
    lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    print(can.recv(0))
    #can.recv(0, lst)


def SetConfRaw02(id, ch, tDelta, filLen):
    print("SetConf02()\n")
    #convert data
    #val1conv = ((val1 - 60)/5.2)*255
    #val2conv = ((val2 - 60)/5.2)*255
    #print("dac1: ",int(val1conv),"dac2: ",int(val2conv))
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL,extframe=False,prescaler=54,sjw=1,bs1=7,bs2=2,auto_restart=True)
    #Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    #Send the command to AFE:
    buf = bytearray(6)
    buf[0] = 0x00
    buf[1] = (0x81 + 2*ch)
    buf[2] = (tDelta >> 8) & 0xFF
    buf[3] = tDelta & 0xFF
    buf[4] = (filLen >> 8) & 0xFF
    buf[5] = filLen & 0xFF
    #buf[2] = int(val1conv)
    #buf[3] = int(val2conv)
    can.send(buf,id)
    time.sleep(1)
    buf2 = bytearray(6)
    lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    print(can.recv(0))
    #can.recv(0, lst)

def GetCtrLoopData1(id, ch):
    print("GetCtrLoopData1\n")
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    buf = bytearray(6)
    buf[0] = 0x01
    buf[1] = 0x10
    buf[2] = 0
    buf[3] = 0
    buf[4] = 0
    buf[5] = 1 << ch
    can.send(buf, id)
    time.sleep(1)
    # print(can.recv(0))
    buf2 = bytearray(8)
    lst = [0, 0, 0, memoryview(buf2)]
    # No heap memory is allocated in the following call
    can.recv(0, lst)
    vDelta = (lst[3][2] << 8) | (lst[3][3] & 0xff)
    print("vDelta value: ", vDelta)
    tDelta = (lst[3][4] << 8) | (lst[3][5] & 0xff)
    print("tDelta value: ", tDelta)
    filLen = (lst[3][6] << 8) | (lst[3][7] & 0xff)
    print("filLen value: ", filLen)
    return vDelta, tDelta, filLen
    
def GetCtrLoopData2(id, ch):
    print("GetCtrLoopData2\n")
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    buf = bytearray(6)
    buf[0] = 0x01
    buf[1] = 0x11
    buf[2] = 0
    buf[3] = 0
    buf[4] = 0
    buf[5] = 1 << ch
    can.send(buf, id)
    time.sleep(1)
    # print(can.recv(0))
    buf2 = bytearray(8)
    lst = [0, 0, 0, memoryview(buf2)]
    # No heap memory is allocated in the following call
    can.recv(0, lst)
    vSetAct = (lst[3][2] << 8) | (lst[3][3] & 0xff)
    print("vSetAct value: ", vSetAct)
    tSetAct = (lst[3][4] << 8) | (lst[3][5] & 0xff)
    print("tSetAct value: ", tSetAct)
    avgFil = (lst[3][6] << 8) | (lst[3][7] & 0xff)
    print("avgFil value: ", avgFil)
    return vSetAct,tSetAct,avgFil
    
def GetCtrLoopData3(id, ch):
    print("GetCtrLoopData3\n")
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    buf = bytearray(6)
    buf[0] = 0x01
    buf[1] = 0x12
    buf[2] = 0
    buf[3] = 0
    buf[4] = 0
    buf[5] = 1 << ch
    can.send(buf, id)
    time.sleep(1)
    # print(can.recv(0))
    buf2 = bytearray(6)
    lst = [0, 0, 0, memoryview(buf2)]
    # No heap memory is allocated in the following call
    can.recv(0, lst)
    sumFil = (lst[3][2] << 24) | (lst[3][3] << 16) | (lst[3][4] << 8) | (lst[3][5] & 0xff)
    print("sumFil value: ", sumFil)
    return sumFil
    
def GetCtrLoopData4(id, ch):
    print("GetCtrLoopData4\n")
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    buf = bytearray(6)
    buf[0] = 0x01
    buf[1] = 0x13
    buf[2] = 0
    buf[3] = 0
    buf[4] = 0
    buf[5] = 1 << ch
    can.send(buf, id)
    time.sleep(1)
    # print(can.recv(0))
    buf2 = bytearray(7)
    lst = [0, 0, 0, memoryview(buf2)]
    # No heap memory is allocated in the following call
    can.recv(0, lst)
    filNewPtr = (lst[3][2] << 8) | (lst[3][3] & 0xff)
    print("filNewPtr value: ", filNewPtr)
    filOldPtr = (lst[3][4] << 8) | (lst[3][5] & 0xff)
    print("filOldPtr value: ", filOldPtr)
    CtreReg = (lst[3][6] & 0xff)
    print("CtreReg value: ", CtreReg)
    return filNewPtr,filOldPtr, CtreReg
    
def SetSimTempTest(id):
    print("setSimTempTest\n")
    #convert data
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL,extframe=False,prescaler=54,sjw=1,bs1=7,bs2=2,auto_restart=True)
    #Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    #Send the command to AFE:
    buf = bytearray(6)
    buf[0] = 0x00
    buf[1] = 0x43
    buf[2] = 0x01
    buf[3] = 0
    buf[4] = 0
    buf[5] = 0
    can.send(buf,id)
    time.sleep(1)
    # buf2 = bytearray(8)
    # lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    print(can.recv(0))
    #can.recv(0, lst)
    
def ClrSimTempTest(id):
    print("Jestem ClrCtrlLoop()\n")
    #convert data
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL,extframe=False,prescaler=54,sjw=1,bs1=7,bs2=2,auto_restart=True)
    #Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    #Send the command to AFE:
    buf = bytearray(6)
    buf[0] = 0x00
    buf[1] = 0x44
    buf[2] = 0x01
    buf[3] = 0
    buf[4] = 0
    buf[5] = 0
    can.send(buf,id)
    time.sleep(1)
    # buf2 = bytearray(8)
    # lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    print(can.recv(0))
    #can.recv(0, lst) 
    
def SetSimTempValTest(id, val1, val2):
    print("Jestem SetSimTempValTest()\n")
    # convert data
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    # Send the command to AFE:
    buf = bytearray(6)
    buf[0] = 0x01
    buf[1] = 0x14
    buf[2] = (val1 >> 8) & 0xFF
    buf[3] = val1 & 0xFF
    buf[4] = (val2 >> 8) & 0xFF
    buf[5] = val2 & 0xFF
    can.send(buf, id)
    time.sleep(1)
    buf2 = bytearray(8)
    lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    print(can.recv(0))
    #can.recv(0, lst)
    
def GetAdcAvg(id, chn):
    print("Jestem AFE_GetAdcAvg()\n")
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    # Send the command to AFE:
    if chn >= 1 and chn <= 2:
        can.send("\x00\x14", id)
    elif chn >= 3 and chn <= 4:
        can.send("\x00\x15", id)
    elif chn >= 5 and chn <= 6:
        can.send("\x00\x16", id)    
    # Wait and read response
    time.sleep(1)
    buf = bytearray(8)
    lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    can.recv(0, lst)
    print("ID: ", lst[0])
    print("RTR: ", lst[1])
    print("FMI: ", lst[2])
    if chn == 1:
        AdcValue = (lst[3][2] << 16) | (lst[3][3] << 8) | (lst[3][4] & 0xff)
        print("adc value of ch", chn, ":", AdcValue, "V")
    elif chn == 2:
        AdcValue = (lst[3][5] << 16) | (lst[3][6] << 8) | (lst[3][7] & 0xff)
        print("adc value of ch", chn, ":", AdcValue, "V")
    elif chn == 3:
        AdcValue = (lst[3][2] << 16) | (lst[3][3] << 8) | (lst[3][4] & 0xff)
        #AdcValue = AdcValue * (70/4095)
        print("adc value of ch", chn, ":", AdcValue)
    elif chn == 4:
        AdcValue = (lst[3][5] << 16) | (lst[3][6] << 8) | (lst[3][7] & 0xff)
        #AdcValue = AdcValue * (70/4095)
        print("adc value of ch", chn, ":", AdcValue)
    elif chn == 5:
        AdcValue = (lst[3][2] << 16) | (lst[3][3] << 8) | (lst[3][4] & 0xff)
        print("raw adc value of ch", chn, ":", AdcValue, "I")
        print("adc value of ch [uA]", chn, ":", AdcValue, "I")
    elif chn == 6:
        AdcValue = (lst[3][5] << 16) | (lst[3][6] << 8) | (lst[3][7] & 0xff)
        print("adc value of ch", chn, ":", AdcValue, "I")
    return AdcValue
    
def GetTempAvg(id):
    print("Jestem AFE_TempAvg()\n")
    can = pyb.CAN(1)
    can.init(pyb.CAN.NORMAL, extframe=False, prescaler=54,
             sjw=1, bs1=7, bs2=2, auto_restart=True)
    # Set filer - all responses to FIFO 0
    #can.setfilter(0, can.LIST16, 0, (0, 1, 2, 4))
    can.setfilter(0, can.MASK16, 0, (0, 0, 0, 0))
    can.send("\x00\x17", id)
    time.sleep(1)
    # print(can.recv(0))
    buf = bytearray(8)
    lst = [0, 0, 0, memoryview(buf)]
    # No heap memory is allocated in the following call
    can.recv(0, lst)
    print("ID: ", lst[0])
    print("RTR: ", lst[1])
    print("FMI: ", lst[2])
    TempVal1 = (lst[3][2] << 16) | (lst[3][3] << 8) | (lst[3][4] & 0xff)
    print("temp value 1: ", TempVal1, "bits")
    TempVal2 = (lst[3][5] << 16) | (lst[3][6] << 8) | (lst[3][7] & 0xff)
    print("temp value 2: ", TempVal2, "bits")
    return TempVal1,TempVal2
