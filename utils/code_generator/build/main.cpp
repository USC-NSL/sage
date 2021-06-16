// Copyright (c) 2021, The University of Southern California.
// All rights reserved.

// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:

// 1. Redistributions of source code must retain the above copyright notice,
// this list of conditions and the following disclaimer.

// 2. Redistributions in binary form must reproduce the above copyright notice,
// this list of conditions and the following disclaimer in the documentation
// and/or other materials provided with the distribution.

// 3. Neither the name of the copyright holder nor the names of its contributors
// may be used to endorse or promote products derived from this software without
// specific prior written permission.

// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.

#include <getopt.h>
#include <signal.h>

#include <iostream>
#include <string>

#include "./common.h"
#include "./gen.h"
#include "./helper.h"
#include "./icmp_hdr.h"
#include "./igmp_hdr.h"
#include "./netfilter_q.h"
#include "./receiver.h"
#include "./sender.h"

const char PROG_NAME[] = "echo";

void print_usage(const std::string prog_name = PROG_NAME) {
  //  The program can take three different flags
  //  flag 's' represents sender
  //  flag 'r' represents receiver
  //  flag 'a' representes sender+receiver
  std::cout << "Usage: " << prog_name << " [options]" << std::endl
            << "Options:" << std::endl
            << "  -h:   print usage" << std::endl
            << "  -v:   verbose" << std::endl
            << "  -m:   mode selector: choices: [pcap,net]" << std::endl
            << "  -s:   sender PCAP action" << std::endl
            << "  -r:   receiver PCAP action" << std::endl
            << "  -a:   sender and receiver PCAP actions" << std::endl;
}

int exec_command(std::string const& cmd) {
  int status = system(cmd.c_str());
  if (status != 0) {
    std::printf("Failed to execute cmd: \n%s\n! Exit code: %d\n", cmd.c_str(),
                status);
  }
  return status;
}

void int_handler(int sig) {
  int exit_val;
  exit_val = exec_command(
      "iptables -I INPUT -p icmp --icmp-type echo-request -j ACCEPT");
  if (exit_val != 0) {
    fprintf(stderr, "error while resetting iptables rules\n");
    exit(130);
  }
  printf("\n");
  exit(0);
}

int main(int argc, char* argv[]) {
  int retval = 0;
  std::string mode("pcap");
  std::string actions("");
  char* pkt = NULL;
  int pkt_len = 0;
  bool opts_eol = false;
  bool verbose = false;
  // parse CLI args
  while (opts_eol == false) {
    switch (getopt(argc, argv, "m:srahv")) {
      case 'h':
        print_usage();
        return 0;
      case 'm':
        mode.assign(optarg);
        break;
      case 's':
        // register a sender action
        actions += 's';
        break;
      case 'r':
        // register a receiver action
        actions += 'r';
        break;
      case 'a':
        // register a sender and a receiver actions
        actions += "sr";
        break;
      case 'v':
        verbose = true;
        break;
      case -1:
        opts_eol = true;
        break;
    }
  }
  if (mode.compare("pcap") == 0) {
    // execute actions
    if (actions.find('s') != std::string::npos) {
      // sender
      if (verbose) std::cout << "Executing sender PCAP action.." << std::endl;
      sender_code_template();
    }
    if (actions.find('r') != std::string::npos) {
      // receiver
      if (verbose) std::cout << "Executing receiver PCAP action.." << std::endl;
      pkt_len = read_pkt(&pkt);
      receiver_code_template(pkt, pkt_len);
    }
  } else if (mode.compare("net") == 0) {
    // setup signal handler
    signal(SIGINT, int_handler);
    // or start listening on a net/netfilter queue
    if (verbose) std::cout << "Starting ICMP Echo replying.." << std::endl;
    // setup iptables
    retval = exec_command(
        "iptables -I INPUT -p icmp --icmp-type echo-request -j NFQUEUE "
        "--queue-num 0");
    if (retval != 0) {
      fprintf(stderr, "error while setting iptables rules\n");
      return retval;
    }
    // read packets from netfilter queue
    retval = proces_pkts_from_netfilterq(verbose);
    // reset iptables
    retval = exec_command(
        "iptables -I INPUT -p icmp --icmp-type echo-request -j ACCEPT");
    if (retval != 0) {
      fprintf(stderr, "error while resetting iptables rules\n");
      return retval;
    }
  } else {
    std::cout << "Invalid mode. Try one of these: [pcap,net]" << std::endl;
    return 64;
  }
  return retval;
}
