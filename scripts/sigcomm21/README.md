# Reproducing ACM SIGCOMM 2021 Paper Results

We provide experiments with runner scripts to reproduce our results claimed in our ACM SIGCOMM2021 paper.

## Requirements
Experiments were tested in a test VM instantiated by the [Vagrantfile](/Vagrantfile) in the repo root. For the interoperability an additional VM is required ([details](interoperability/README.md)). 

### Required Software:
* [vagrant](https://www.vagrantup.com/)
* [VirtualBox](https://www.virtualbox.org/)

##  Vagrant Usage:
Please refer to the [howto](/installation_vagrant_readme.md)

### Executing Experiments

#### List of Experiments
We present the following experiments to demonstrate SAGE capabilities and to reproduce main results of the paper:

| Name                                                              | Scripted/Manual | Execution Time     |
|:------------------------------------------------------------------|:---------------:|-------------------:|
| [Validation of checks on IGMP](validation_of_checks_igmp)         | Scripted        |             2 min  |
| [Interoperation with existing tools ICMP](interoperability)       | Manual          | depends (>15 mins) |
| [Demonstration on human involvement for bad message](bad_example) | Scripted        |             2 min  |
| [Show the manual work on NTP](manual_work_ntp)                    | Mixed           | depends (>10 mins) |
| [Reproduce Figure 5](fig5)                                        | Mixed           |         27-30 min  |
| [Reproduce Figure 6](fig6)                                        | Mixed           |            78 min  |

Additonal experiments (e.g., BFD processing) are available at [SAGE tests](/scripts/tests).

### Execute an Experiment

Navigate to a experiment folder. Test steps are described in the README. Please, consult with the experiment README first.

Experiments rely on a runner script `run.sh` that prints either `OK` or `FAIL` depending on the experiment outcome.

An example of experiment execution:
```sh
$ cd validation_of_checks_igmp
$ ./run.sh
[IGMP] Resetting..
[IGMP] Executing..
[IGMP] Checking results..
[IGMP] Check: Logical Forms OK
[IGMP] Check: Headers OK
[IGMP] OK
```
