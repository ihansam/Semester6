#! /usr/bin/env python
# SKKU KD JIN, ihansam@skku.edu
# OS Intro HW#1
# ver 2.2. exception revised 19.10.05.

# [time arrival option 설계]
# job의 runtime을 받는 jlist처럼, job의 arrival time을 직접 받을 수 있는 alist 구현

# <case 1 (random workLoad)>
# -a option 미사용시 arrival time은 모두 0이다
# -a option 사용시 적어도 한 숫자를 입력해야 하며, 어떤 수를 입력하든 random arrival time이 설정된다
# 이때 MAX arrival time은 jobs * maxlen로 가정했다

# <case 2 (given workLoad)>
# -a option 미사용시 arrival time은 모두 0이다
# -a option 사용시 alist의 각 값을 arrival time으로 설정한다
# alist size가 jlist size와 다를 때, 각 list에 음수가 들어왔을 때 exception을 발생시킨다

import sys
from optparse import OptionParser
import random

parser = OptionParser()
parser.add_option("-s", "--seed", default=0, help="the random seed", 
                  action="store", type="int", dest="seed")
parser.add_option("-j", "--jobs", default=3, help="number of jobs in the system",
                  action="store", type="int", dest="jobs")
parser.add_option("-l", "--jlist", default="", help="instead of random jobs, provide a comma-separated list of run times",
                  action="store", type="string", dest="jlist")
parser.add_option("-m", "--maxlen", default=10, help="max length of job",
                  action="store", type="int", dest="maxlen")
parser.add_option("-p", "--policy", default="FIFO", help="sched policy to use: FIFO, SJF, STCF, RR",
                  action="store", type="string", dest="policy")
parser.add_option("-q", "--quantum", help="length of time slice for RR policy", default=1, 
                  action="store", type="int", dest="quantum")
parser.add_option("-c", help="compute answers for me", action="store_true", default=False, dest="solve")
# arrival time을 list로 입력할 수 있는 옵션 -a
parser.add_option("-a", "--alist", default="", help="instead zero arrival time, provide arrival time assign option.",
                  action="store", type="string", dest="alist")

(options, args) = parser.parse_args()

random.seed(options.seed)

print('ARG policy', options.policy)
if options.jlist == '':
    print('ARG jobs', options.jobs)
    print('ARG maxlen', options.maxlen)
    print('ARG seed', options.seed)
else:
    print('ARG jlist', options.jlist)

if options.alist != '':                                                 # print alist ARG if not NULL
    print('ARG alist', options.alist)

print('')

print('Here is the job list, with the run time of each job: ')

import operator

# job list
joblist = []                                                            # joblist is the list of job [jobnum, runtime, arrival time]
if options.jlist == '':                                                 # <case 1> /Random workload/
    for jobnum in range(0,options.jobs):
        runtime = int(options.maxlen * random.random()) + 1             
        if options.alist == '':                                         # alist == NULL -> arr time = 0
            arrtime = 0
        else:                                                           # alist != NULL -> random arr time
            arrtime = int(options.maxlen*options.jobs*random.random())  
        joblist.append([jobnum, runtime, arrtime])                      
        print('  Job', jobnum, '( length = ' + str(runtime) + ', arrival time = ' + str(arrtime) + ' )')
else:                                                                   # <case 2> /Given workload/    
    RTlist = options.jlist.split(',')                                   # given run time list by jlist    
    ATlist = []                                                         # given arr time list by alist
    if options.alist == '':                                             # alist == NULL -> all arr time = 0
        for filler in range(0,len(RTlist)):
            ATlist.append(0)
    else:
        templist = options.alist.split(',')                             # alist != NULL -> given alist를 arr time으로 할당
        ATlist = list(map(int, templist))
        if len(RTlist)!=len(ATlist):                                    # alist와 jlist의 size가 다를 때 exception
            print('ERROR: number of alist args must be same of jlist')
            exit(1)
            
    jobnum = 0
    for runtime in RTlist:
        arrtime = ATlist[jobnum]
        if arrtime < 0:                                                      # alist에 음수 시간이 들어왔을 때 exception
            print('ERROR: provide unsigned integer value to alist args')
            exit(1)
        if int(runtime) < 0:                                                 # jlist에 음수 시간이 들어왔을 때 exception
            print('ERROR: provide unsiged integer value to jlist args')
            exit(1)
        joblist.append([jobnum, int(runtime), arrtime])               
        jobnum += 1

    for job in joblist:        
        print('  Job', job[0], '( length = ' + str(job[1]) + ', arrival time = ' + str(job[2]) + ' )')
print('\n')

if options.solve == True:
    print('** Solutions **\n')
    if options.policy == 'SJF':
        joblist = sorted(joblist, key=operator.itemgetter(1))
        options.policy = 'FIFO'
    
    if options.policy == 'FIFO':
        thetime = 0
        print('Execution trace:')
        for job in joblist:
            print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' % (thetime, job[0], job[1], thetime + job[1]))
            thetime += job[1]

        print('\nFinal statistics:')
        t     = 0.0
        count = 0
        turnaroundSum = 0.0
        waitSum       = 0.0
        responseSum   = 0.0
        for tmp in joblist:
            jobnum  = tmp[0]
            runtime = tmp[1]
            
            response   = t
            turnaround = t + runtime
            wait       = t
            print('  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (jobnum, response, turnaround, wait))
            responseSum   += response
            turnaroundSum += turnaround
            waitSum       += wait
            t += runtime
            count = count + 1
        print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count))
                     
    if options.policy == 'RR':
        print('Execution trace:')
        turnaround = {}
        response = {}
        lastran = {}
        wait = {}
        quantum  = float(options.quantum)
        jobcount = len(joblist)
        for i in range(0,jobcount):
            lastran[i] = 0.0
            wait[i] = 0.0
            turnaround[i] = 0.0
            response[i] = -1

        runlist = []
        for e in joblist:
            runlist.append(e)

        thetime  = 0.0
        while jobcount > 0:
            # print '%d jobs remaining' % jobcount
            job = runlist.pop(0)
            jobnum  = job[0]
            runtime = float(job[1])
            if response[jobnum] == -1:
                response[jobnum] = thetime
            currwait = thetime - lastran[jobnum]
            wait[jobnum] += currwait
            if runtime > quantum:
                runtime -= quantum
                ranfor = quantum
                print('  [ time %3d ] Run job %3d for %.2f secs' % (thetime, jobnum, ranfor))
                runlist.append([jobnum, runtime])
            else:
                ranfor = runtime
                print('  [ time %3d ] Run job %3d for %.2f secs ( DONE at %.2f )' % (thetime, jobnum, ranfor, thetime + ranfor))
                turnaround[jobnum] = thetime + ranfor
                jobcount -= 1
            thetime += ranfor
            lastran[jobnum] = thetime
        
        print('\nFinal statistics:')
        turnaroundSum = 0.0
        waitSum       = 0.0
        responseSum   = 0.0
        for i in range(0,len(joblist)):
            turnaroundSum += turnaround[i]
            responseSum += response[i]
            waitSum += wait[i]
            print('  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (i, response[i], turnaround[i], wait[i]))
        count = len(joblist)
        
        print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count))

    # [STCF Algorighm 구현] =================================================================================
    if options.policy == 'STCF':
        # Execution Trace
        print('Execution trace:')

        jobs = len(joblist)             # 처음 job 개수

        for i in range(0,jobs):         # job: [jobnum, runtime, arrival time, time left, response time, turnaround time, wait time]
            j = joblist.pop(0)          # 각 job에 남은 시간, 각 performance 원소를 추가
            j.extend([j[1],-1,0,0])            
            joblist.append(j)

        Decision_Times = []             # job arrival time마다 어떤 job을 실행할 지 결정해야한다          
        for j in joblist:
            Decision_Times.append(j[2])
        Decision_Times.sort()

        thetime = 0                     # 현재 시간.
        Memory = []                     # job이 도착해 wait하고 실행되는 공간
        Disk = []                       # 끝난 job이 옮겨지는 공간
        CPUrun = False                  # shecedule된 job이 있어 CPU가 실행상태인지 나타내는 flag
        Excution_Time = 0               # CPU가 한 job을 실행시킨 시간
        count = 0                       # 완료된 job의 개수

        while count < jobs:                 # job이 모두 끝날 때까지 반복
            if thetime in Decision_Times:       # [현재 시간이 decision time일 때]
                if CPUrun:                          # 실행중이던 job이 있으면 종료한다
                    CPUrun = False
                    print('  [ time %3d ] Run job %d for %.2f secs' % (thetime-Excution_Time, Memory[0][0], Excution_Time))
                    Excution_Time = 0
                                 
                for job in joblist:             # Desition time에 새로 arrival한 job들을 MEM으로 load한다
                    if job[2] == thetime:
                        Memory.append(job)

                Memory = sorted(Memory, key=operator.itemgetter(3))    # 스케쥴할 job을 정하기 위해 timeleft순으로 정렬한다 
                CPUrun = True

            else:                               # [현재 시간이 decition time이 아닐 때]
                if not CPUrun:                      # CPU가 쉬는 중일 때
                    if Memory == []:                # memory가 비어있으면 찰때까지 쉰다.
                        thetime += 1
                    else:                           # memory에 할 job이 있으면 다음 job을 스케쥴링한다. (재정렬할 필요는 없다)
                        CPUrun = True

            if CPUrun:                          # [CPU 동작] 스케쥴링이 완료되면 CPU를 1초간 실행시킨다
                if Memory[0][4] == -1:              # 처음 실행된 job은 response time을 기록한다
                    Memory[0][4] = thetime - Memory[0][2]

                thetime += 1
                Excution_Time += 1
                Memory[0][3] -= 1                   # timeleft 1 감소
                if len(Memory) > 1:                 # 실행중이 아닌 MEM의 job wait time을 1 증가
                    for i in range(1,len(Memory)):      
                        Memory[i][6] += 1
                
                if Memory[0][3] == 0:               # timeleft가 0일때, 즉 job이 끝나면 Disk로 옮긴다
                    CPUrun = False
                    print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' \
                        % (thetime-Excution_Time, Memory[0][0], Excution_Time, thetime))                    
                    Memory[0][5] = thetime - Memory[0][2]       # turnaround time 기록
                    Disk.append(Memory[0])
                    count += 1
                    Memory.pop(0)
                    Excution_Time = 0






    # ========================================================================================================    
    if options.policy != 'FIFO' and options.policy != 'SJF' and options.policy != 'STCF' and options.policy != 'RR': 
        print('Error: Policy', options.policy, 'is not available.')
        sys.exit(0)
else:
    print('Compute the turnaround time, response time, and wait time for each job.')
    print('When you are done, run this program again, with the same arguments,')
    print('but with -c, which will thus provide you with the answers. You can use')
    print('-s <somenumber> or your own job list (-l 10,15,20 for example)')
    print('to generate different problems for yourself.')
    print('')


