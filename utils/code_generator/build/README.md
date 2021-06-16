# SAGE Static Framework

This is the implementation of the static framework used in SAGE.

This codebase also serves as a demo application processing ICMP Echo Request/Reply messages on GNU/Linux systems.

## Using the static framework

The static framework consists of helper functions and data structures. Depending on the use-case it requires some adjustments to fit into the executing environment (e.g., OS APIs, I/O libraries).

The key components:

* [common.h](common.h)
* [gen.h](gen.h)
* [helper.h](helper.h)
* [meta.h](meta.h)
* [proto.h](proto.h)
* [receiver.h](receiver.h)
* [sender.h](sender.h)

## Tailored versions of the static framework

A tailored version is used in the [SIGCOMM21 ICMP interoperability experiment](/scripts/sigcomm21/interoperability) in a Mininet environment.

This folder contains a version implementing ICMP Echo Request/Reply processing on a real GNU/Linux system using the SAGE-generated protocol implementation.

This  version is interoperable with `ping` and `traceroute -I`. To try it, install `libnetfilter-queue-dev`, run `make`, start it with `sudo ./echo -m net -v`, and start pinging the system.
