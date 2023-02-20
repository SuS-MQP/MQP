import os
import csv
import statistics
import numpy as np
import matplotlib.pyplot as plt


"""Returns a list of file paths within "Latency" 
and its subdirectories that contain "PageLoadTime" in their file name."""
def get_latency_files() -> list[str]:
    files = []
    for root, dirs, filenames in os.walk("Latency"):
        for f in filenames:
            if "PageLoadTime" in f:
                files.append(os.path.join(root, f))
    return files

"""Returns a list of file paths within "Latency" 
and its subdirectories that contain "Manager_RAW" in their file name"""
def get_manager_system_usage_files() -> list[str]:
    files = []
    for root, dirs, filenames in os.walk("Latency"):
        for f in filenames:
            if "Manager_RAW" in f:
                files.append(os.path.join(root, f))
    return files

"""Returns a list of file paths within "Latency" 
and its subdirectories that contain "System_RAW" in their file name"""
def get_server_system_usage_files() -> list[str]:
    files = []
    for root, dirs, filenames in os.walk("Latency"):
        for f in filenames:
            if "System_RAW" in f:
                files.append(os.path.join(root, f))
    return files

"""Returns a tuple containing a boolean NumPy array that marks the outliers
 in the input data, as well as the lower and upper bounds of the interquartile 
 range calculated using the 25th and 75th percentiles of data."""
def find_outliers(data) -> tuple[np.ndarray[bool], float, float]:
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)
    return (np.array([True if x < lower_bound or x > upper_bound else False for x in data]), float(lower_bound), float(upper_bound))

"""
This function reads latency CSV files, 
removes outliers from the 'Latency' column, 
writes cleaned data to new CSV files, 
and graphs their Cumulative Distribution Functions (CDFs).
"""
def clean_latency_files() -> list[float]:
    latency_values_for_summary_stats = []
    created_clean_files = []
    for f in get_latency_files():
        with open(f, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            #skip the first line
            next(reader)
            #get the type and size from the file path
            type = f.split('/')[1]
            size = f.split('/')[2]
            #create a new csv file in the format of cleaned/Type_Size.csv
            with open('cleaned/' +'latency' +'_'+type + '_' + size + '.csv', 'w+') as newfile:
                created_clean_files.append(newfile.name)
                writer = csv.writer(newfile, delimiter=',')
                writer.writerow(
                    ['Time', 'Elapsed', 'Label', 
                     'ResponseCode', 'ResponseMessage', 'ThreadName', 
                     'DataType', 'Success', 'FailureMessage', 
                     'Bytes', 'SentBytes', 'grpThreads', 
                     'allThreads', 'URL', 'Latency', 
                     'IdleTime', 'Connect'])
                #get all the timestamps from the csv file
                timestamps = [row[0] for row in reader]

                #get the start and end time of the test
                test_start = int(timestamps[0])
                test_end = int(timestamps[-1])

                #get the time 1 minute after the test starts and 1 minute before the test ends 
                # to account for the waterfall of threads starting and stopping
                buildup_done = test_start + 60000
                teardown_begin = test_end - 60000
                #reset the reader to the beginning of the file
                csvfile.seek(0)
                #skip the first line
                next(reader)
                #get the Latency column from the csv file
                latencies = [int(row[14]) for row in reader if int(row[0]) > buildup_done and int(row[0]) < teardown_begin]
                #convert the Latency column to a numpy array
                #get the outliers from the numpy array
                outliers,lower_bound,upper_bound = find_outliers(latencies)
                #convert the outliers to a list
                outliers = outliers.tolist()
                #filter out the outliers from latencies using list comprehension and zip
                #reset the reader to the beginning of the file
                csvfile.seek(0)
                #skip the first line
                next(reader)
                #loop through the csv file
                for row in reader:
                    #timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,
                    # sentBytes,grpThreads,allThreads,URL,Latency,IdleTime,Connect
                    #get the time and latency from the csv file
                    time, elapsed, label, responseCode, responseMessage, threadName, dataType, \
                    success, failureMessage, bytes, sentBytes, grpThreads, allThreads, url, \
                    latency, idleTime, connect = row
                    if success == 'true' and (int(time) > buildup_done and int(time) < teardown_begin) and int(latency) < upper_bound and int(latency) > lower_bound:
                    #write the time and latency to the new csv file
                        latency_values_for_summary_stats.append(int(latency))
                        writer.writerow([time,elapsed,label,
                                        responseCode,responseMessage,threadName,
                                        dataType,success,failureMessage,
                                        bytes,sentBytes,grpThreads,
                                        allThreads,url,latency,
                                        idleTime,connect])
                                    
    graph_CDFs(created_clean_files,"latency")
    return latency_values_for_summary_stats

"""This function takes a scope parameter to either get the manager or server system usage files, 
cleans them by removing data outside the test build-up and tear-down periods and saves them to new files, 
and generates cumulative distribution function graphs for CPU and memory usage of the cleaned server files."""
def clean_system_usage_files(scope:str) -> tuple[list[float], list[float], list[float], list[float]]:
    created_clean_manager_CPU_files = []
    created_clean_manager_RAM_files = []
    created_clean_server_CPU_files = []
    created_clean_server_RAM_files = []
    manager_CPU_for_summary_stats = []
    manager_RAM_for_summary_stats = []
    server_CPU_for_summary_stats = []
    server_RAM_for_summary_stats = []

    files = get_manager_system_usage_files() if scope == "manager" else get_server_system_usage_files()
    for f in files:
        with open(f, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            #skip the first line
            next(reader)
            #get the type and size from the file path
            type = f.split('/')[1]
            size = f.split('/')[2]
            #create a new csv file in the format of cleaned/Type_Size.csv
            with open('cleaned/' +f'{scope}-CPU' +'_'+type + '_' + size + '.csv', 'w+') as newfile:
                if scope == "Manager":
                    created_clean_manager_CPU_files.append(newfile.name)
                else:
                    created_clean_server_CPU_files.append(newfile.name)
                writer = csv.writer(newfile, delimiter=',')
                # Time,CPU %,Memory (MB)
                writer.writerow(['Time','CPU %'])
                #get all the timestamps from the csv file
                timestamps = [row[0] for row in reader]
                test_start = float(timestamps[0])
                test_end = float(timestamps[-1])
                buildup_done = test_start + 60
                teardown_begin = test_end - 60
                #reset the reader to the beginning of the file
                csvfile.seek(0)
                #skip the first line
                next(reader)
                #loop through the csv file
                for row in reader:
                    #get the time and latency from the csv file
                    time, cpu, memory = row
                    if float(time) > buildup_done and float(time) < teardown_begin:
                    #write the time and latency to the new csv file
                        if scope == "Manager":
                            manager_CPU_for_summary_stats.append(float(cpu))
                            manager_RAM_for_summary_stats.append(float(memory))
                        else:
                            server_CPU_for_summary_stats.append(float(cpu))
                            server_RAM_for_summary_stats.append(float(memory))
                        writer.writerow([time,cpu])
                #reset the reader to the beginning of the file
                csvfile.seek(0)
                #skip the first line
                next(reader)
            with open('cleaned/' +f'{scope}-RAM' +'_'+type + '_' + size + '.csv', 'w+') as newfile:
                if scope == "Manager":
                    created_clean_manager_RAM_files.append(newfile.name)
                else:
                    created_clean_server_RAM_files.append(newfile.name)
                writer = csv.writer(newfile, delimiter=',')
                # Time,CPU %,Memory (MB)
                writer.writerow(['Time','Memory (MB)'])
                #get all the timestamps from the csv file
                timestamps = [row[0] for row in reader]
                test_start = float(timestamps[0])
                test_end = float(timestamps[-1])
                buildup_done = test_start + 60
                teardown_begin = test_end - 60
                #reset the reader to the beginning of the file
                csvfile.seek(0)
                #skip the first line
                next(reader)
                #loop through the csv file
                for row in reader:
                    #get the time and latency from the csv file
                    time, cpu, memory = row
                    if float(time) > buildup_done and float(time) < teardown_begin:
                    #write the time and latency to the new csv file
                        writer.writerow([time,memory])
    graph_CDFs(created_clean_server_CPU_files,f"{scope}-CPU")
    graph_CDFs(created_clean_server_RAM_files,f"{scope}-RAM")
    return manager_CPU_for_summary_stats, manager_RAM_for_summary_stats, server_CPU_for_summary_stats, server_RAM_for_summary_stats
    
"""
This function graphs cumulative distribution functions (CDFs) 
from latency data in csv files for different experiments and 
container trial sizes, and saves the plots as png files.
"""
def graph_CDFs(files:list[str],type:str) -> None:
    if "Manager" in type:
        return
    if "Server" in type:
        pass
    TRIALS = [1,10,25,50]
    
    for trial in TRIALS:
        experiments = {
        "BloomAndHash" : [],
        "Hash": [],
        "PHPExt": [],
        "Vanilla": []
    }
        for f in files:
            experiment = f.split("_")[1].split("/")[-1] 
            size = f.split("_")[-1].split(".csv")[0]
            if size == str(trial):
                #read in the latency data from the csv file
                with open(f, 'r') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    #skip the first line
                    next(reader)
                    if type=="latency":
                    #get the latency data from the csv file
                        experiments[experiment] = [float(row[14]) for row in reader]
                    else:
                        experiments[experiment] = [float(row[1]) for row in reader]

    
        #plot all the CDFs together
        fig, ax = plt.subplots()
        for experiment in experiments:
            data = experiments[experiment]
            if not data:
                continue
            x = np.sort(data)
            y = np.arange(1, len(x)+1) / len(x)
            match (experiment):
                case "BloomAndHash":
                    color = "#2D3B89"
                    label = "Warden"
                case "Hash":
                    continue
                case "PHPExt":
                    color = "#8892bf"
                    label = "PHP Profiling Extension"
                case "Vanilla":
                    color = "#DE6E4B"
                    label = "Vanilla"
                case "Nginx":
                    color = "#039138"
                    label = "Nginx"
                case _:
                    color = "black"
                    label = "Unknown"
            ax.plot(x, y, label=label, color=color)

        #specify the output demiensions
        if type == "latency":
            ax.set_xlabel("Latency (ms)")
        elif type == "Server-CPU":
            ax.set_xlabel("CPU Usage (%)")
        elif type == "Server-RAM":
            ax.set_xlabel("RAM Usage (MB)")
        ax.set_ylabel("% of Trials")
        ax.legend()
        plt.grid()
        # plt.show()
        plt.savefig("CDFs_NO_TITLE/" + f"{type.replace('-','_')}_"+str(trial) + "_containers.png",dpi=300)
        ax.set_title("Cumulative Distribution Function for " + str(trial) + " Containers",verticalalignment='baseline',fontsize=12)
        plt.savefig("CDFs/" + f"{type.replace('-','_')}_"+str(trial) + "_containers.png",dpi=300)


def calculate_summary_stats(samples:list[float]) -> tuple[float,float,float]:
    mean = sum(samples)/len(samples)
    std = statistics.stdev(samples)
    median = statistics.median(samples)
    return mean, std, median


if __name__ == '__main__':
    print("Cleaning latency data...")
    latency_stats = clean_latency_files()
    print("Cleaning Manager usage data...")
    manager_CPU, manager_RAM = clean_system_usage_files("Manager")[:2]
    print("Cleaning System usage data...")
    system_CPU, system_RAM = clean_system_usage_files("Server")[2:]

    manager_CPU_mean, manager_CPU_std, manager_CPU_median = calculate_summary_stats(manager_CPU)
    manager_RAM_mean, manager_RAM_std, manager_RAM_median = calculate_summary_stats(manager_RAM)
    system_CPU_mean, system_CPU_std, system_CPU_median = calculate_summary_stats(system_CPU)
    system_RAM_mean, system_RAM_std, system_RAM_median = calculate_summary_stats(system_RAM)

    print(f"{manager_CPU_mean=:.2f}% {manager_CPU_std=:.2f} {manager_CPU_median=:.2f}%")
    print(f"{manager_RAM_mean=:.2f}MB {manager_RAM_std=:.2f} {manager_RAM_median=:.2f}MB")
    print(f"{system_CPU_mean=:.2f}% {system_CPU_std=:.2f} {system_CPU_median=:.2f}%")
    print(f"{system_RAM_mean=:.2f}MB {system_RAM_std=:.2f} {system_RAM_median=:.2f}MB")
