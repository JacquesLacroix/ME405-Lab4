"""!
@file main.py
Tests input and output of the Nucleo board with a DC motor response.
"""

import pyb
import time
import utime
import motor_driver
import encoder_reader
import controller
import struct

pinC1 = pyb.Pin(pyb.Pin.board.PC1, pyb.Pin.OUT_PP)
pinA0 = pyb.Pin(pyb.Pin.board.PA0, pyb.Pin.OUT_PP) 
pinA1 = pyb.Pin(pyb.Pin.board.PA1, pyb.Pin.OUT_PP)
    
pinC6 = pyb.Pin(pyb.Pin.board.PC6, pyb.Pin.OUT_PP) 
pinC7 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.OUT_PP)
    
tim5 = pyb.Timer(5, freq=20000)   #Motor Controller Timer 
tim8 = pyb.Timer(8, prescaler=1, period=65535)
    
motor = motor_driver.MotorDriver(pinC1, pinA0, pinA1, tim5)
encoder = encoder_reader.Encoder(pinC6, pinC7, tim8)

    
controller = controller.Controller(encoder, motor, 8000, 1/16)

def wait_for_input():
    """!
    Wait for input from computer then run step_response()
    @returns None
    """
    ser = pyb.USB_VCP()
        
    while True:
        line = ser.readline()
        if line == None:
            continue
        elif line.decode() == "Begin\n":
            while True:
                line = ser.readline()
                if line == None:
                    continue
                else:
                    step_response(line.decode().split("\n")[0])
                    break

def step_response(kp):
    """!
    Enables timer interrupts and begins a step response. After the response is done, prints each value.
    @returns None
    """
    try:
        kp = float(kp)
    except:
        print("End")
        return
        
    controller.set_kp(kp)
    encoder.zero()
        
    startticks = utime.ticks_ms()
    
    last = 0
    
    while True:
        current = controller.run()
        if abs(current) < 15 and last - current < .5:
            for i in range(10):
                controller.run()
                utime.sleep_ms(10)
            break
        last = current
        utime.sleep_ms(10)
        
        
    controller.print_list(startticks)
    print("End")
    return

if __name__ == "__main__":
    wait_for_input()