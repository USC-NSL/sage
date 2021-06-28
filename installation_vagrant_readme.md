# Vagrant how-to
Below are the instructions to run SAGE with Vagrant file

## Using Vagrant
Step 1: Clone the [repo](https://github.com/USC-NSL/sage) and change directory to the root of the cloned SAGE repo.

Step 2: To create/start the SAGE VM with the [Vagrantfile](/Vagrantfile):
```sh
vagrant up
```

The [vagrant up](https://www.vagrantup.com/docs/cli/up) command first creates a VM. After the second run, the command just starts it.

* The VM creation requires an Internet connection and takes approx. 50 minutes (depends on your internet connection).

* Starting the VM later is instantaneous.

Step 3: Login to the VM: 
```sh
vagrant ssh
```

To connect to the running VM, use the [vagrant ssh](https://www.vagrantup.com/docs/cli/ssh) command.

Step 4: Build SAGE:

The SAGE directory on the host is available at `/sage/` in the VM. Please go to SAGE dir before running any experiment:
```sh
cd sage
make build
```
Step 5: Execute SAGE to parse input text:

Please refer to the commands in [Usage](/README.md#usage).

Step 6 (Optional): Shutdown the VM: 
`vagrant halt`

To halt the running VM, use the [vagrant halt](https://www.vagrantup.com/docs/cli/halt) command

To remove the VM, use [vagrant destroy](https://www.vagrantup.com/docs/cli/destroy).

