# **<u>`Warden MQP - SuS CFI README`</u>**

Kush Shah, Samuel Parks, Keith DeSantis

___

This is a README file for a Computer Science Major Qualifying Project at Worcester Polytechnic Institute 2022-23.

This directory includes the major files and source code we have developed while engineering <u>Warden: Multi-Layered Control Flow Integrity in Web Applications</u>

Within the `Final Submission` folder, you can find:

* `MQP_SuS_History.pdf` Our final report of the project.
* `C Term Peer Evals` An administrative peer evaluation for our final term on the project.
* `WardenSourceCode.zip` A zip file containing the source code of Warden, including the following files.

Source Code Files: 
* `Makefile` CFI Makefile used for building `warden` with command `make warden` 
* `warden` Compiled executable for WARDEN using bloom filter. Setup for use with SuS on our VM: 130.215.26.44
* `CFI_CONFIG.h` Config file that contains important global variables, filepaths, and modes of operation. Modes of operation include:
    * `DEBUG` Extra debugging statements are printed
    * `DISCOVERY` CFI will perform dynamic analysis, adding each function call to data structures and saving data to `dynamicAnalysisFunctions.txt`
    * `WRITE_LOGS_TO_FILE` The log parsing server will write log data to `wp_logs.txt`
    * `INCREMENTAL_MODE` The incremental filter will be used in place of the bloom filter for lightweight CFI. Called `Frequency Based Anomaly Detection: FBAD` in our report.
* `manager.c` Driver C file that populates CFI data structures and launches the threadpool and the log parsing server
* `server.c` Log parsing server source code, including log catching process and log parsing process
* `threadPool.c` Threadpool source code, including lightweight and robust (called weak and strong) CFI functionality and log assignment handling
* `bloomfilter.c` Bloom filter implementation and API
* `hashmap.c` Hashmap used by robust CFI implementation and API
* `incremental_filter.c` The incremental filter implemenation and API (uses hashmap)
* `log_handling.h` Shared h file containing unparsed and parsed log and queue structs
* `manager.h` manager h file
* `threadPool.h` threadPool h file
* `bloomfilter.h` bloom filter h file
* `hashmap.h` hashmap h file
* `incremental_filter.h` incremental filter h file
* `trustedFunctions.txt` A file of function calls learned by Warden while running in DISCOVERY mode and those collected during static analysis

**<u> In `static analysis` directory: </u>**
* `line_num_static_analysis.py` A python script used to parse Wordpress source code and record function calls associated with PHP scripts.
* `test_static_analysis.py` A python file used to test `line_num_static_analysis.py`

**<u> In `testing` directory: </u>**
* `measurements.py` A python script used to record CPU usage and memory usage of the Warden manager process and the entire host system while conducting stress testing.
* `graphUsageData.py` A python script used to quickly graph the data collected by `measurements.py` while testing
* The `data` directory, containing our CPU, RAM, and latency data from our tests.
