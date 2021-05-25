# Interoperation w/ existing tools ICMP

This experiment demonstrates how SAGE generated code interoperates with Linux built-in `ping` and `traceroute` in Mininet-configured network. Please find the provided [VM](https://drive.google.com/file/d/1fSXbRzxYUn8Vod_yfsFJ5qqyNPsI00-1/view?usp=sharing) to conduct this experiment. In this experiment, users will build a router program which includes static framework code and SAGE-generated code. Then, users will run four commands in Mininet as below to interact with router program.

# Executing the Experiment
The experiment contains a few simple steps:
1. Generate ICMP header and code files (Scripted in `run.sh`. Note the execution enables a flag `-o` so that the generated code with API syntax that matches with VM compiler version)

2. Properly patch header and code files ([Patching detail](#Patching) is noted below. Scripted in `run.sh`)
3. Compare against the expected header and code files (Scripted in `run.sh`). The expected header and code files are identical to the files already included in the VM.

(Optional) Copy/paste generated `gen.h` and `icmp_hdr.h` file to the specified folder in VM (Please follow the [instructions](#Execution-details-in-VM) to put files under sub-folder `router`.) It is okay to skip this step because the identical generated `gen.h` and `icmp_hdr.h` are already included.

4. Execute interoperability experiment([instructions](#Execution-details-in-VM))

## Patching
The detail of patching is to remove redundant comments, to match file naming in static framework code, and to add include guards to the code file so that the generated code can match with the static framework. We do NOT patch any extra functions/features in this step.

## Execution details in VM
Simple instructions on the execution steps are as following:
1. Import the [ova file](https://drive.google.com/file/d/1fSXbRzxYUn8Vod_yfsFJ5qqyNPsI00-1/view?usp=sharing) to Virtual Box
2. Login user account `CS 551 Student`  with password: `sage`
3. Go to terminal:\
   `> 551-Labs; cd exp`
4. Set up the hook-up environment with the script `run_all.sh`:\
   `> ./run_all.sh`
5. Set up mininet:\
   `> ./run_mininet`
6. Open another tab/window; go to sub-folder `router`; make the source code (a copy of SAGE generated code is already included) and run the program:\
   `> cd router; make; ./sr`
7. Go back to the window executing Mininet and run testing command.\
   For example, `> client ping -c 3 10.0.1.1`\
   (The mininet side receives packets successfully and the experiment is done)

   The four commands evaluated in the paper are:
   |Test Commands                          |Purpose                      |
   |:------------------------------------- |:----------------------------|
   |client ping -c 10 10.0.1.1             |Test Echo message            |
   |client ping -c 10 192.168.3.1          |Test Dest Unreachable message|
   |client ping -c 10 -t 1 192.168.2.2     |Test Time Exceeded message   |
   |client traceroute 10.0.1.1             |Test TRACEROUTE              |

8. (Optional) Switch back to router window to view the print out message.

Execution of the experiments would depend on user-configured resource for VM.
