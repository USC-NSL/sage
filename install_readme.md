# Installation from fresh VM
Below are the instructions to install SAGE on fresh VM.

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

### 4. Build SAGE
```sh
cd sage
make build
```

