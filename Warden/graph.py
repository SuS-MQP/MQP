from functools import cache
import os
import csv
import numpy as np
import matplotlib.pyplot as plt
#a function to get all PageLoadTimeTe.csv files from Latency/*/*/
# and put them into a list
def get_files() -> list[str]:
    files = []
    for root, dirs, filenames in os.walk("Latency"):
        for f in filenames:
            if "PageLoadTime" in f:
                files.append(os.path.join(root, f))
    return files

#a function that takes in a list and returns a list of boolens indicating if the value is an outlier via the IQR method
def find_outliers(data) -> tuple[np.ndarray[bool], float, float]:
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)
    return (np.array([True if x < lower_bound or x > upper_bound else False for x in data]), float(lower_bound), float(upper_bound))



#a function to loop though get_files() in the format of Latency/Type/Size/*.csv and create new csv files in the format of cleaned/Type_Size.csv
def clean_files() -> None:
    created_clean_files = []
    for f in get_files():
        with open(f, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            #skip the first line
            next(reader)
            #get the type and size from the file path
            type = f.split('/')[1]
            size = f.split('/')[2]
            #create a new csv file in the format of cleaned/Type_Size.csv
            with open('cleaned/' + type + '_' + size + '.csv', 'w+') as newfile:
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
                        writer.writerow([time,elapsed,label,
                                        responseCode,responseMessage,threadName,
                                        dataType,success,failureMessage,
                                        bytes,sentBytes,grpThreads,
                                        allThreads,url,latency,
                                        idleTime,connect])
    graph_CDFs(created_clean_files)


#a function to create Cumulative Distribution Functions for each cleaned csv file
def graph_CDFs(files:list[str]) -> None:
    TRIALS = [1,10,25,50]
    
    for trial in TRIALS:
        experiments = {
        "BloomAndHash" : [],
        "Hash": [],
        "PHPExt": [],
        "Vanilla": []
    }
        for f in files:
            experiment = f.split("_")[0].split("/")[-1]
            size = f.split("_")[-1].split(".csv")[0]
            if size == str(trial):
                #read in the latency data from the csv file
                with open(f, 'r') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    #skip the first line
                    next(reader)
                    #get the latency data from the csv file
                    experiments[experiment] = [float(row[14]) for row in reader]
    
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
                case "Hash":
                    color = "#72E1D1"
                case "PHPExt":
                    color = "#8892bf"
                case "Vanilla":
                    color = "#DE6E4B"
                case _:
                    color = "black"
            ax.plot(x, y, label=experiment, color=color)
        ax.set_ylabel("% of Trials")
        ax.set_xlabel("Latency (ms)")
        ax.set_title("Cumulative Distribution Function for " + str(trial) + " Containers")
        ax.legend()
        plt.savefig("CDFs/" + str(trial) + "_containers.png")

                



if __name__ == '__main__':
    clean_files()