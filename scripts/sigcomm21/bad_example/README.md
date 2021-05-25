# Demonstration on human involvement for bad message

This short experiment presents when human involvement is required on a [poor/ambigous text](bad_echo.txt) describing the ICMP ECHO protocol header. In this experiment, we intentionally include two ambiguous sentences. One is an identical sentence presenting in current RFC 792, and it results in more than 1 LF, shown in Table 6 in the paper. The other is a made-up sentence intentionally added to the text, and it results in 0 LF before disambiguation check. In this short automated test, we run SAGE on the bad sentences and generate alarm/suggestion messages to users.

# Executing the Experiment

## Execution details
The experiments is fully scripted.

Execution of the experiments takes approx. 1.5 minutes.

## How to execute

1. Execute `./run.sh`
2. Check the results:
   * expect to see two ambiguous sentences marked in red on the output with suggestions on human actions.
