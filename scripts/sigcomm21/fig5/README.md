# Reproducing Figure 5 of the Paper

Figure 5 shows the number of LFs after inconsistency checks on ICMP, IGMP, and BFD.  For each ambiguous sentence, sequentially executing checks on LFs (Base) reduces inconsistencies; after the last Associativity check, the final output is a single LF.

# Executing the Experiment

## Execution details
The experiments is scripted except eyeballing the results at the very end.

Execution of the experiments takes approx. 30 minutes.

## How to execute

1. Execute `./run.sh`  (takes approx. 30 mins)
2. Check the results:
   * all Associativity results must yield min/avg/max 1.
   * results of inconsistency checks might differ due to recent improvements of SAGE and its dependencies.
