from multiprocessing import Process, Pipe
from datetime import datetime
from time import sleep

def local_time(counter):
    return ' (LAMPORT_TIME={}, LOCAL_TIME={})'.format(counter,datetime.now())

def calc_recv_timestamp(recv_time_stamp, counter,pid):
    for id in range(len(counter)):
        counter[id] = max(recv_time_stamp[id], counter[id])
    counter[pid]+=1
    return counter

def event(pid, counter):
    counter[pid] += 1
    print('Something happened in {} !'. \
          format(pid) + local_time(counter))
    return counter

def send_message(pipe, pid, counter):
    counter[pid] += 1
    pipe.send(('Empty shell', counter))
    print('Message sent from ' + str(pid) + local_time(counter))
    return counter

def recv_message(pipe, pid, counter):
    message, timestamp = pipe.recv()
    counter = calc_recv_timestamp(timestamp, counter,pid)
    print('Message received at ' + str(pid) + local_time(counter))
    return counter

def process_1(pipe12):
    pid = 0
    counter = [0, 0, 0]
    counter = send_message(pipe12, pid, counter)
    counter = send_message(pipe12, pid, counter)
    counter = event(pid, counter)
    counter = recv_message(pipe12, pid, counter)
    counter = event(pid, counter)
    counter = event(pid, counter)
    counter = recv_message(pipe12, pid, counter)

    sleep(2)
    print("\nFinal state of each process:")
    print("First process:", counter)

def process_2(pipe21, pipe23):
    pid = 1
    counter = [0, 0, 0]
    counter = recv_message(pipe21, pid, counter)
    counter = recv_message(pipe21, pid, counter)
    counter = send_message(pipe21, pid, counter)
    counter = recv_message(pipe23, pid, counter)
    counter = event(pid, counter)
    counter = send_message(pipe21, pid, counter)
    counter = send_message(pipe23, pid, counter)
    counter = send_message(pipe23, pid, counter)

    sleep(3)
    print("Second process:", counter)

def process_3(pipe32):
    pid = 2
    counter = [0, 0, 0]
    counter = send_message(pipe32, pid, counter)
    counter = recv_message(pipe32, pid, counter)
    counter = event(pid, counter)
    counter = recv_message(pipe32, pid, counter)

    sleep(4)
    print("Third process:", counter)

if __name__ == '__main__':
    oneandtwo, twoandone = Pipe()
    twoandthree, threeandtwo = Pipe()

    process1 = Process(target=process_1,
                       args=(oneandtwo,))
    process2 = Process(target=process_2,
                       args=(twoandone, twoandthree))
    process3 = Process(target=process_3,
                       args=(threeandtwo,))

    process1.start()
    process2.start()
    process3.start()

    process1.join()
    process2.join()
    process3.join()