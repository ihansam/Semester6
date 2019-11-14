# SKKU EEE 2015311951 Kidan Jin
# OS intro HW#3
# test implementation of clock algorithm
  
# variables
ref = [1,2,3,4,1,2,5,1,2,3,4,5]     # page reference (testcase)
mem = []                            # contents of memory
use = []                            # use bit of memory
size = 3                            # size of memory
clkptr = 0                          # clock pointer

# function
def clockreplacement(cp, refnum):   # 현재 clock 포인터와 reference page number를 받아
    replace_complete = False        # clock pointer를 갱신하고, swap out될 victim을 정하고, 메모리를 replacement하는 함수    
    while not replace_complete:            
        if use[cp] == 0:            # victime page found
            victim = mem.pop(cp)        # replace
            mem.insert(cp, refnum)
            use[cp] = 1                 # set usebit
            replace_complete = True
        else:                       # give used page second chance
            use[cp] = 0                 # reset use bit
                                    # update clock pointer
        cp = (lambda x: 0 if x == size-1 else x+1)(cp)      # 0->1->2->0...
    return cp, victim

# main
for page in ref:
    victim = " "                # reset victim
    if page in mem:             # hit case
        use[mem.index(page)] = 1    # set usebit
        state = "hit "
    elif len(mem) < size:       # cold miss case
        mem.append(page)            # swap in
        use.append(1)
        state = "miss"
    else:                       # miss case         
        clkptr, victim = clockreplacement(clkptr, page)     # run replacement algorithm
        state = "miss"
    print("Access: %d  %4s clock pointer->%d usebit: %9s memory: %9s Replaced: %s" %(page, state, clkptr, use, mem, victim))