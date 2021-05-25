# SAGE

[Overview](#overview) | [Installation](#installation) | [Usage](#usage) | [Caveats and Limitations](#caveats-and-limitations) | [License](#license)

## Overview

This tool is used to disambiguate protocol descriptions in IETF RFC documents, then to convert disambiguated protocol descriptions into executable protocol implementation.

_SAGE introduces semi-automated protocol processing across multiple protocol specifications. SAGE includes domain-specific extensions to semantic parsing and automated discovery of ambiguities and enables disambiguation; SAGE can convert these specs to code._

For more information, please refer to the ACM SIGCOMM21 paper ([preprint](https://arxiv.org/pdf/2010.04801.pdf)).


## Installation
There are 2 ways to use SAGE. First is using our [Vagrantfile](/Vagrantfile), second is shown below. If you use the Vagrant file, you may skip to [Usage](#Usage) below. For more information about Vagrant, please visit [official website](https://www.vagrantup.com/intro).

### 1. Install Dependencies
- Debian/Ubuntu packages
``` sh
sudo apt install build-essential python3-pip clang-format libsqlite3-dev libpcap-dev git
```
For Ubuntu, enable the universe distribution component ([howto](https://askubuntu.com/questions/1254309/not-installing-pip-on-ubuntu-20-04)).

- Python3 packages
``` sh
pip3 install tabulate tqdm torch stanfordcorenlp termcolor networkx matplotlib pydot nltk "spacy >=2.2,<3"
```

- Download SpaCy model
``` sh
python3 -m spacy download en
```

- Install NeuralCoref
```sh
git clone --depth 1 https://github.com/huggingface/neuralcoref.git
cd neuralcoref
pip install -r requirements.txt
pip install -e .
```

#### 2. Patch NLTK
Edit `~/.local/lib/python3.*/site-packages/nltk/parse/chart.py` or the NLTK source you are using:

```diff
     def parses(self, root, tree_class=Tree):
         """
         Return an iterator of the complete tree structures that span
         the entire chart, and whose root node is ``root``.
         """
-        for edge in self.select(start=0, end=self._num_leaves, lhs=root):
+        for edge in self.select(start=0, end=self._num_leaves):
             for tree in self.trees(edge, tree_class=tree_class, complete=True):
                 yield tree
```

### 3. Clone the Repository

```sh
git clone https://github.com/USC-NSL/sage.git
```

### 4. Build Sage
```sh
cd sage
make build
```

## Usage

### Run Sage
To start Sage, execute the following command:
```sh
./sage -i <rfc.txt> -p <PROTOCOL>
```
During execution Sage provides detailed logs about the process: currently processed sentence, number of logical forms, ..., and lastly, the generated code.

### Add support for additional protocols / Configure Sage
Sage currently stores configuration files in a distributed fashion. To add support for new protocols, extend the configuration.

**Phraser** relies on terms defined in [utils/phraser/data/EN/custom.txt](utils/phraser/data/EN/custom.txt).

**CCG Tool** uses a lexicon which is stored in [utils/ccg_tool/dictionary.py](utils/ccg_tool/dictionary.py).

**Logical Form Checker** uses [utils/logic_form_checker/check_predicates.py](utils/logic_form_checker/check_predicates.py).

**Code Generator** configuration is stored in [utils/code_generator/settings.py](utils/code_generator/settings.py).


### Run our experiments and tests
To easily recreate some of our results, we packed our SIGCOMM experiments with ready-to-run shell scripts. For details, see [scripts/sigcomm21](scripts/sigcomm21).

Additional ready-to-run test scripts are available in [scripts/tests](scripts/tests).


## Caveats and Limitations

Sage is an experimental software under heavy development with limitations:

* Small number of protocols/RFCs are supported
* No single config file
* Slow execution due to limited scalability (mostly single-core execution)

## License

Sage is a free software and licensed under the [3-Clause BSD license](/LICENSE).
