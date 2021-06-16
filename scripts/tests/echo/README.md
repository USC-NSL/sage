# SAGE ping/traceroute Interoperability Test

This test demonstrates the interoperation of SAGE generated ICMP code with ping and traceroute on a realistic networks.

The experiment uses 2 interconnected VMs:
```
+-----------+    +-----------+
|    SUT    |    |   Tester  |
| 10.0.0.10 |====| 10.0.0.11 |
+-----------+    +-----------+
```

# Executing the Experiment

0. Start both VMs with `vagrant up` from the current directory, and login to both VMs at once: `vagrant ssh sut` and `vagrant ssh tester`

1. On the SUT (System Under Test), run SAGE-generated ICMP Echo Request/Reply handler code:

```sh
cd /sage/utils/code_generator/build
make
sudo ./echo -m net -v
```

2. On Tester, execute `ping 10.0.0.10` or `traceroute -I 10.0.0.10`

We expect to see responses on the Tester, and output indicating correct behavior on the SUT.

Example SUT output:

```
Starting ICMP Echo replying..
opening library handle
unbinding existing nf_queue handler for AF_INET (if any)
binding nfnetlink_queue as nf_queue handler for AF_INET
binding this socket to queue '0'
setting copy_packet mode
pkt received
Pass verifying ip hdr...
Pass verifying icmp hdr...
recv pkt is echo msg
Construct Reply Packet ...
```
