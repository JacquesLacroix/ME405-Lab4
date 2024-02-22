"""!
@file basic_tasks.py
    This file contains a demonstration program that runs some tasks, an
    inter-task shared variable, and a queue. The tasks don't really @b do
    anything; the example just shows how these elements are created and run.

@author JR Ridgely
@date   2021-Dec-15 JRR Created from the remains of previous example
@copyright (c) 2015-2021 by JR Ridgely and released under the GNU
    Public License, Version 2. 
"""

import gc
import pyb
import cotask
import task_share
import motor_driver
import encoder_reader
import controller
import utime



# Task 1: call run() on controller
def task1(shares):
    """!

    """
    pinC1 = pyb.Pin(pyb.Pin.board.PC1, pyb.Pin.OUT_PP)
    pinA0 = pyb.Pin(pyb.Pin.board.PA0, pyb.Pin.OUT_PP) 
    pinA1 = pyb.Pin(pyb.Pin.board.PA1, pyb.Pin.OUT_PP)
    
    pinC6 = pyb.Pin(pyb.Pin.board.PC6, pyb.Pin.OUT_PP) 
    pinC7 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.OUT_PP)
    
    tim5 = pyb.Timer(5, freq=20000)   #Motor Controller Timer 
    tim8 = pyb.Timer(8, prescaler=1, period=65535)
    
    motor = motor_driver.MotorDriver(pinC1, pinA0, pinA1, tim5)
    encoder = encoder_reader.Encoder(pinC6, pinC7, tim8)

    ctrl = controller.Controller(encoder, motor, 8000, 1/16)
    ser = pyb.USB_VCP()
    while True:
        line = ser.readline()
        if line == None:
            yield 0
            continue
        elif line.decode() == "Begin\n":
            while True:
                line = ser.readline()
                if line == None:
                    yield 0
                    continue
                else:
                    kp = line.decode().split("\n")[0]
                    try:
                        kp = float(kp)
                    except:
                        print("End")
                        yield 0
                        break
                        
                    ctrl.set_kp(kp)
                    encoder.zero()
                        
                    startticks = utime.ticks_ms()
                    
                    last = 0
                    
                    while True:
                        current = ctrl.run()
                        if abs(current) < 15 and last - current < .5:
                            for i in range(10):
                                ctrl.run()
                                yield 0
                            break
                        last = current
                        yield 0
                        
                    ctrl.print_list(startticks)
                    print("End")
                    yield 0
                    break
                yield 0
            continue
        else:
            yield 0


# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":
#     print("Testing ME405 stuff in cotask.py and task_share.py\r\n"
#           "Press Ctrl-C to stop and show diagnostics.")

    # Create a share and a queue to test function and diagnostic printouts
    share0 = task_share.Share('h', thread_protect=False, name="Share 0")
    q0 = task_share.Queue('L', 16, thread_protect=False, overwrite=False,
                          name="Queue 0")

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    task1 = cotask.Task(task1, name="Task_1", priority=1, period=10,
                        profile=True, trace=False, shares=(share0, q0))
    cotask.task_list.append(task1)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break

    # Print a table of task data and a table of shared information data
#     print('\n' + str (cotask.task_list))
#     print(task_share.show_all())
#     print(task1.get_trace())
#     print('')
