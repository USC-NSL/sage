# SAGE

[Overview](#overview) | [Installation](#installation) | [Usage](#usage) | [Caveats and Limitations](#caveats-and-limitations) | [License](#license)

## Overview

This tool is used to disambiguate protocol descriptions in IETF RFC documents, then to convert disambiguated protocol descriptions into executable protocol implementation.

_SAGE introduces semi-automated protocol processing across multiple protocol specifications. SAGE includes domain-specific extensions to semantic parsing and automated discovery of ambiguities and enables disambiguation; SAGE can convert these specs to code._

For more information, please refer to the ACM SIGCOMM21 paper ([preprint](https://arxiv.org/pdf/2010.04801.pdf)).


## Installation
There are 2 ways to use SAGE. 

* Use [Vagrant](https://www.vagrantup.com/intro) with our [Vagrantfile](/Vagrantfile) -  Please refer to the [howto](/installation_vagrant_readme.md)
* Build SAGE in fresh VM - Please refer to the [howto](/install_readme.md)

## Usage

### Run SAGE
To start SAGE, execute the following command:
```sh
./sage -i <rfc.txt> -p <PROTOCOL>
```

* rfc.txt: This is the specification text file you would like SAGE to parse
* PROTOCOL: This is the protocol name you would like to name for the generated header and code files

An example of the command is:
```sh
./sage -i igmp.txt -p igmp
```

This command will parse the input `igmp.txt` text file, and the protocol specified inside the text file is IGMP protocol. The output header and code file will have `IGMP` as the prefix of file names.

During execution SAGE provides detailed logs about the process: currently processed sentence, number of logical forms, ..., and lastly, the generated code.

### Run our experiments and tests
To easily recreate some of our results, we packed our SIGCOMM experiments with ready-to-run shell scripts. For details, see [scripts/sigcomm21](scripts/sigcomm21).

Additional ready-to-run test scripts are available in [scripts/tests](scripts/tests).

### Add support for additional protocols
SAGE is able to parse a number of protocols, and adding support for additional protocols is still in progress. For more details, we provide another [README](/utils) for introuductions of configurations and an illustration example.

## Caveats and Limitations

SAGE is an experimental software under heavy development with limitations:

* Small number of protocols/RFCs are supported
* No single config file
* Slow execution due to limited scalability (mostly single-core execution)

## Developers

* Jane Yen - [email](mailto:yeny@usc.edu)
* Tamás Lévai - [email](mailto:levait@tmit.bme.hu)

## License

SAGE is a free software and licensed under the [3-Clause BSD license](/LICENSE).
