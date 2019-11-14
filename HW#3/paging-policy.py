#! /usr/bin/env python
# SKKU EEE KD JIN. ihansam@skku.edu
# OS Intro HW#3
# ver 2.1 develop print format 19.11.15.

import sys
from optparse import OptionParser
import random
import math

def convert(size):
    length = len(size)
    lastchar = size[length-1]
    if (lastchar == 'k') or (lastchar == 'K'):
        m = 1024
        nsize = int(size[0:length-1]) * m
    elif (lastchar == 'm') or (lastchar == 'M'):
        m = 1024*1024
        nsize = int(size[0:length-1]) * m
    elif (lastchar == 'g') or (lastchar == 'G'):
        m = 1024*1024*1024
        nsize = int(size[0:length-1]) * m
    else:
        nsize = int(size)
    return nsize

def hfunc(index):
    if index == -1:
        return 'MISS'
    else:
        return 'HIT '

def vfunc(victim):
    if victim == -1:
        return '-'
    else:
        return str(victim)

#
# main program
#                           # clockbits의 default값을 1로 수정함
parser = OptionParser()
parser.add_option('-a', '--addresses', default='-1',   help='a set of comma-separated pages to access; -1 means randomly generate',  action='store', type='string', dest='addresses')
parser.add_option('-f', '--addressfile', default='',   help='a file with a bunch of addresses in it',                                action='store', type='string', dest='addressfile')
parser.add_option('-n', '--numaddrs', default='10',    help='if -a (--addresses) is -1, this is the number of addrs to generate',    action='store', type='string', dest='numaddrs')
parser.add_option('-p', '--policy', default='FIFO',    help='replacement policy: FIFO, LRU, OPT, UNOPT, RAND, CLOCK',                action='store', type='string', dest='policy')
parser.add_option('-b', '--clockbits', default=1,      help='for CLOCK policy, how many clock bits to use',                          action='store', type='int', dest='clockbits')
parser.add_option('-C', '--cachesize', default='3',    help='size of the page cache, in pages',                                      action='store', type='string', dest='cachesize')
parser.add_option('-m', '--maxpage', default='10',     help='if randomly generating page accesses, this is the max page number',     action='store', type='string', dest='maxpage')
parser.add_option('-s', '--seed', default='0',         help='random number seed',                                                    action='store', type='string', dest='seed')
parser.add_option('-N', '--notrace', default=False,    help='do not print out a detailed trace',                                     action='store_true', dest='notrace')
parser.add_option('-c', '--compute', default=False,    help='compute answers for me',                                                action='store_true', dest='solve')

(options, args) = parser.parse_args()

print('ARG addresses', options.addresses)
print('ARG addressfile', options.addressfile)
print('ARG numaddrs', options.numaddrs)
print('ARG policy', options.policy)
print('ARG clockbits', options.clockbits)
print('ARG cachesize', options.cachesize)
print('ARG maxpage', options.maxpage)
print('ARG seed', options.seed)
print('ARG notrace', options.notrace)
print('')

addresses   = str(options.addresses)
addressFile = str(options.addressfile)
numaddrs    = int(options.numaddrs)
cachesize   = int(options.cachesize)
seed        = int(options.seed)
maxpage     = int(options.maxpage)
policy      = str(options.policy)
notrace     = options.notrace
clockbits   = int(options.clockbits)

random.seed(seed)

addrList = []
if addressFile != '':
    fd = open(addressFile)
    for line in fd:
        addrList.append(int(line))
    fd.close()
else:
    if addresses == '-1':
        # need to generate addresses
        for i in range(0,numaddrs):
            n = int(maxpage * random.random())
            addrList.append(n)
    else:
        addrList = addresses.split(',')

if options.solve == False:
    print('Assuming a replacement policy of %s, and a cache of size %d pages,' % (policy, cachesize))
    print('figure out whether each of the following page references hit or miss')
    print('in the page cache.\n')

    for n in addrList:
        print('Access: %d  Hit/Miss?  State of Memory?' % int(n))
    print('')

else:
    if notrace == False:
        print('Solving...\n')

    # init memory structure
    count = 0
    memory = []
    hits = 0
    miss = 0

    if policy == 'FIFO':
        leftStr = 'FirstIn'
        riteStr = 'Lastin '
    elif policy == 'LRU':
        leftStr = 'LRU'
        riteStr = 'MRU'
    elif policy == 'MRU':
        leftStr = 'LRU'
        riteStr = 'MRU'
    elif policy == 'OPT' or policy == 'RAND' or policy == 'UNOPT' or policy == 'CLOCK':
        leftStr = 'Left '
        riteStr = 'Right'
    else:
        print('Policy %s is not yet implemented' % policy)
        exit(1)

    # track reference bits for clock
    ref   = {}

    cdebug = False

    # need to generate addresses
    addrIndex = 0
    clkptr = 0                                                  # clock pointer for CLOCK policy
    for nStr in addrList:
        # first, lookup
        n = int(nStr)
        try:                                                                # check hit case
            idx = memory.index(n)
            hits = hits + 1
            if policy == 'LRU' or policy == 'MRU':
                update = memory.remove(n)
                memory.append(n) # puts it on MRU side
        except:
            idx = -1
            miss = miss + 1

        victim = -1        
        if idx == -1:                                                       # miss case: cold miss, need replacement
            # miss, replace?
            # print 'BUG count, cachesize:', count, cachesize
            if count == cachesize:
                # must replace
                if policy == 'FIFO' or policy == 'LRU':
                    victim = memory.pop(0)
                elif policy == 'MRU':
                    victim = memory.pop(count-1)
                elif policy == 'RAND':
                    victim = memory.pop(int(random.random() * count))
                elif policy == 'CLOCK':
                    if cdebug:
                        print('REFERENCE TO PAGE', n)
                        print('MEMORY ', memory)
                        print('REF (b)', ref)

                    # hack: for now, do random                              # 간단한 구현을 위해, memory swap in을 여기서 처리하였음
                    # victim = memory.pop(int(random.random() * count))         # miss and full case이므로 replace 필요
                    victim = -1                                                 # swap out될 victim을 찾자
                    while victim == -1:
                        page = memory[clkptr]                                   # page: 포인터가 가리키는 페이지 번호
                        if cdebug:
                            print('  scan page:', page, ref[page])
                        if ref[page] >= 1:                                      # page의 usebit이 0이 아니면
                            ref[page] -= 1                                      # 1번의 기회를 더 줌 (usebit 차감)
                        else:
                            # this is our victim                                # page의 usebit이 0이면
                            victim = page                                       # replace할 victim이 정해짐
                            memory.remove(page)                                 # swap out
                            memory.insert(clkptr, n)                            # swap in
                                                                                # clock pointer update를 위해 break 제거
                        clkptr = (lambda x: 0 if x == cachesize-1 else x+1)(clkptr)      # clock pointer update (0->1->2->0...)

                    
                    # remove old page's ref count
                    if page in memory:
                        assert('BROKEN')
                    del ref[victim]
                    if cdebug:
                        print('VICTIM', page)
                        print('LEN', len(memory))
                        print('MEM', memory)
                        print('REF (a)', ref)

                elif policy == 'OPT':
                    maxReplace  = -1
                    replaceIdx  = -1
                    replacePage = -1
                    # print 'OPT: access %d, memory %s' % (n, memory) 
                    # print 'OPT: replace from FUTURE (%s)' % addrList[addrIndex+1:]
                    for pageIndex in range(0,count):
                        page = memory[pageIndex]
                        # now, have page 'page' at index 'pageIndex' in memory
                        whenReferenced = len(addrList)
                        # whenReferenced tells us when, in the future, this was referenced
                        for futureIdx in range(addrIndex+1,len(addrList)):
                            futurePage = int(addrList[futureIdx])
                            if page == futurePage:
                                whenReferenced = futureIdx
                                break
                        # print 'OPT: page %d is referenced at %d' % (page, whenReferenced)
                        if whenReferenced >= maxReplace:
                            # print 'OPT: ??? updating maxReplace (%d %d %d)' % (replaceIdx, replacePage, maxReplace)
                            replaceIdx  = pageIndex
                            replacePage = page
                            maxReplace  = whenReferenced
                            # print 'OPT: --> updating maxReplace (%d %d %d)' % (replaceIdx, replacePage, maxReplace)
                    victim = memory.pop(replaceIdx)
                    # print 'OPT: replacing page %d (idx:%d) because I saw it in future at %d' % (victim, replaceIdx, whenReferenced)
                elif policy == 'UNOPT':
                    minReplace  = len(addrList) + 1
                    replaceIdx  = -1
                    replacePage = -1
                    for pageIndex in range(0,count):
                        page = memory[pageIndex]
                        # now, have page 'page' at index 'pageIndex' in memory
                        whenReferenced = len(addrList)
                        # whenReferenced tells us when, in the future, this was referenced
                        for futureIdx in range(addrIndex+1,len(addrList)):
                            futurePage = int(addrList[futureIdx])
                            if page == futurePage:
                                whenReferenced = futureIdx
                                break
                        if whenReferenced < minReplace:
                            replaceIdx  = pageIndex
                            replacePage = page
                            minReplace  = whenReferenced
                    victim = memory.pop(replaceIdx)
            else:
                # miss, but no replacement needed (cache not full)      # cold miss case
                victim = -1
                count = count + 1
                if policy == 'CLOCK':                                   # clock policy에서
                    memory.append(n)                                    # cold miss에 대한 swap in

            # now add to memory
            if not(policy == 'CLOCK'):                      # clock policy에서 swap in 과정은 이미 위에서 했으므로 생략
                memory.append(n)
            if cdebug:
                print('LEN (a)', len(memory))
            if victim != -1:
                assert(victim not in memory)

        # after miss processing, update reference bit
        if n not in ref:                                    # 새로 swap in된 page의 usebit를 1로 set
            ref[n] = 1
        else:                                               # 기존에 있던 page의 usebit를 1 증가 (최대 clockbits까지만)
            ref[n] += 1
            if ref[n] > clockbits:
                ref[n] = clockbits
        
        if cdebug:
            print('REF (a)', ref)

        if notrace == False:
            if policy == 'CLOCK':                               # clock policy에 대한 출력
                usebitlist = [ref[item] for item in memory]     # ref에 저장된 usebit를 memory 순서로 정렬해 쉽게 확인할 수 있도록 함 
                print('Access: %d %s clock pointer-> %d MEMORY: %9s usebits: %9s Replaced:%s [Hits:%d Misses:%d]' \
                    % (n, hfunc(idx), clkptr, memory, usebitlist, vfunc(victim), hits, miss))
            else:
                print('Access: %d  %s %s -> %12s <- %s Replaced:%s [Hits:%d Misses:%d]' % (n, hfunc(idx), leftStr, memory, riteStr, vfunc(victim), hits, miss))
        addrIndex = addrIndex + 1
        
    print('')
    print('FINALSTATS hits %d   misses %d   hitrate %.2f' % (hits, miss, (100.0*float(hits))/(float(hits)+float(miss))))
    print('')
