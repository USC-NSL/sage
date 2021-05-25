# Validation of Checks on IGMP

This short experiment presents the effectivenes of inconsistency checks on a [short text](igmp.txt) describing the IGMP protocol header. For each ambiguous sentence, sequentially executing checks on LFs (base) reduces inconsistencies; after the last check, the final output (unique) is a single LF. In this short automated test we run SAGE on IGMP text and test against [results known a priori](expected_output.txt).

# Executing the Experiment

## Execution details
The experiments is fully scripted.

Execution of the experiments takes approx. 2 minutes.

## How to execute

1. Execute `./run.sh`
2. Check the results:
   * expect to see `Logical Forms OK` on the output
