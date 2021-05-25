# Reproducing Figure 6 of the Paper

Figure 6 shows effect of individual disambiguation checks on the ICMP RFC. In these measurements we change the order of disambiguation check and measure the efficiency of the first applied check.

We show two metrics: 
* average number of LFs filtered by the check per ambiguous sentence, and 
* number of ambiguous sentences affected.

# Executing the Experiment

## Execution details
The experiments is scripted except eyeballing the results at the very end.

Execution of the experiments takes approx. 78 minutes.

## How to execute

1. Execute `./run.sh`  (takes approx. 78 mins)
2. Check the results:
   * _Measured_ results are in pair with _Figure_ results.
   * results might differ due to recent improvements (i.e., additional rules) of SAGE
