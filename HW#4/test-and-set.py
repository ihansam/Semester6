mutex = 0
count = 0

# acquire
def acquire():
    ax = 1
    while (ax != 0):        # test $0, %ax; jne  .acquire
        ax = 1                  # mov $1, %ax
        global mutex            
        ax, mutex = mutex, ax   # xchg %ax, mutex

# release lock
def release():
    global mutex    
    mutex = 0                   # mov  $0, mutex

# main
bx = 1
while bx > 0:               # test $0, %bx; jgt .top
    # critical section start
    acquire()
    count = count + 1           # mov  count, %ax; add  $1, %ax; mov  %ax, count
    release()
    # critical section end
    bx = bx - 1                 # sub  $1, %bx