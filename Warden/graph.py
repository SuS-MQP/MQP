# timeStamp,elapsed,label,responseCode,responseMessage,
# threadName,dataType,success,failureMessage,bytes,sentBytes,
# grpThreads,allThreads,URL,Latency,IdleTime,Connect

import os

import matplotlib.pyplot as plt
import numpy as np

PAGELOAD = "PageLoadTime.csv"





def get_data() -> dict:
    trial_data = {}
    os.chdir('Latency/BloomFilterAndHash')
    trials = [dir for dir in os.listdir() if os.path.isdir(dir)]
    for trial in trials:
        trial_data[trial] = [dir for dir in os.listdir(trial) if not os.path.isdir(dir)]
    return trial_data



data = get_data()

def graph_page_load_time() -> None:
    pages = {
        "index" : ([],[]),
        "author admin": ([],[]),
        "author admin-0": ([],[]),
        "author admin-1": ([],[]),
        "hello world": ([],[]),
        "hello world comments": ([],[]),
        "comments feed": ([],[]),
        "2019-04": ([],[]),
        "feed": ([],[]),
    }
    for trial, files in data.items():
        if not PAGELOAD in files:
            continue
        print(trial.upper())
        for file in files:
            if file == PAGELOAD:
                with open(os.path.join(trial, file), 'r') as f:
                    lines = f.readlines()
                    lines = [line.strip().split(',') for line in lines]
                    lines = [line for line in lines if line[0] != 'timeStamp']

                    for line in lines:
                        if line[7] == 'false':
                            continue
                        page = line[2] 
                        latency = line[14]
                        print(f"{page} {line[0]} {latency}")
                        pages[page][1].append(int(latency))
                        pages[page][0].append(int(line[0]))
    #graph a line for each page 
                    plt.plot(pages['index'][0],pages['index'][1], label='index')
                    plt.legend()
                    plt.show()

if __name__ == '__main__':
    graph_page_load_time()