# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-20.04"

  config.vm.hostname = "SageVM"

  config.vm.synced_folder ".", "/sage"

  config.vm.provider "virtualbox" do |vb|
    vb.name = "SageVM"
    vb.gui = false
    vb.memory = "4096"
    vb.cpus = "2"
  end

  config.vm.provision "deps", type: "shell", privileged: false, inline: <<-SHELL
    sudo apt-get update
    sudo apt-get install -y \
         build-essential \
         python3-pip \
         clang-format \
         libsqlite3-dev \
         libpcap-dev \
         git
  SHELL

  config.vm.provision "pydeps", type: "shell", privileged: false, inline: <<-SHELL
    pip3 install --no-cache-dir \
         tabulate \
         tqdm \
         torch \
         termcolor \
         networkx \
         matplotlib \
         pydot \
         nltk \
         stanfordcorenlp \
         "spacy >=2.2,<3"
  SHELL

  config.vm.provision "spacy", type: "shell", privileged: false, inline: <<-SHELL
    python3 -m spacy download en
  SHELL

  config.vm.provision "neuralcoref", type: "shell", privileged: false, inline: <<-SHELL
    git clone --depth 1 https://github.com/huggingface/neuralcoref.git
    cd neuralcoref
    pip3 install -r requirements.txt
    pip3 install -e .

  SHELL

  config.vm.provision "nltk", type: "shell", privileged: false, inline: <<-SHELL
    sed -i \
    "s/for edge in self.select(start=0, end=self._num_leaves, lhs=root):/for edge in self.select(start=0, end=self._num_leaves):/" \
    ~/.local/lib/python3.*/site-packages/nltk/parse/chart.py
  SHELL

  config.vm.provision "clean", type: "shell", privileged: false, inline: <<-SHELL
    sudo apt-get clean
  SHELL

  config.vm.provision "link", type: "shell", privileged: false, inline: <<-SHELL
    ln -s /sage ~/sage
  SHELL

end
