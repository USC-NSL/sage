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

#ifndef NETFILTERQ_H_
#define NETFILTERQ_H_

#include <libnetfilter_queue/libnetfilter_queue.h>
#include <linux/netfilter.h>
#include <stdio.h>

#include "./helper.h"
#include "./receiver.h"

// inspired by
// https://github.com/irontec/netfilter-nfqueue-samples/blob/master/sample-helloworld.c

void construct_icmp_reply(int type, proto_len_t *lens, proto_ptr_t *ptrs);

static int cb(struct nfq_q_handle *qh, struct nfgenmsg *nfmsg,
              struct nfq_data *nfa, void *data) {
  u_int32_t id;
  int len;
  unsigned char *nf_packet;
  struct nfqnl_msg_packet_hdr *ph;
  ph = nfq_get_msg_packet_hdr(nfa);
  id = ntohl(ph->packet_id);
  len = nfq_get_payload(nfa, &nf_packet);
  if ((len <= 0)) {
    fprintf(stderr, "Error, no pkt to receive\n");
    return -1;
  }
  valid_proto_t flags = {true, true, false, false};
  proto_len_t lens = {len + 14, len, 0, 0};
  proto_ptr_t ptrs = {nf_packet, nf_packet, nullptr, nullptr};
  // no need to handle ethernet, it is done by the kernel
  /* if (flags.eth) { }*/
  if (flags.ip) {
    bool ip_process = verify_ip_hdr(ptrs.ip_ptr, lens.ip_len, &lens, &ptrs);
    if (ip_process) {
      printf("Pass verifying ip hdr...\n");
      ip_action(&flags, &lens, &ptrs);
    } else {
      drop();
      return -1;
    }
  }
  if (flags.icmp) {
    bool icmp_process = verify_icmp_hdr(ptrs.icmp_ptr, lens.icmp_len);
    if (icmp_process) {
      printf("Pass verifying icmp hdr...\n");
      // icmp action
      Echo_or_Echo_Reply_Message_hdr *icmp_hdr =
          (Echo_or_Echo_Reply_Message_hdr *) ptrs.icmp_ptr;
      switch (icmp_hdr->type) {
        case 8:
          printf("recv pkt is echo msg\n");
          construct_icmp_reply(0, &lens, &ptrs);
          break;
        case 15:
          printf("recv pkt is information request\n");
          construct_icmp_reply(16, &lens, &ptrs);
          break;
        case 0:
          dummy_action();
          break;
        default:
          printf("Packet Forwarded\n");
      }
    }
  } else {
    drop();
    return -1;
  }

  return nfq_set_verdict(qh, id, NF_ACCEPT, 0, NULL);
}

void construct_icmp_reply(int type, proto_len_t *lens, proto_ptr_t *ptrs) {
  // Construct an echo reply packet from the sender packet,
  // where each header pointers are kept in 'ptrs' and length
  // of header to packet tail is kept in argument struct 'lens'

  printf("Construct Reply Packet ... \n");
  char *buffer = (char *) malloc(lens->eth_len);
  memcpy(buffer, ptrs->eth_ptr, lens->eth_len);

  // update ip header
  ip_hdr_t *ip_hdr = (ip_hdr_t *) (buffer + (int) sizeof(ether_hdr_t));

  // update icmp header
  switch (type) {
    case 0:
      reverse_ip(ip_hdr);
      update_ip_checksum(ip_hdr);
      fake_fill_icmp((Echo_or_Echo_Reply_Message_hdr *) (ip_hdr + 1), 0,
                     lens->icmp_len, lens, ptrs);
      break;

    case 3:
      ip_hdr->ip_dst = ip_hdr->ip_src;
      ip_hdr->ip_src = interface_1_addr;
      update_ip_checksum(ip_hdr);
      fill_icmp_dest_unreachable_receiver(
          (Destination_Unreachable_Message_hdr *) (ip_hdr + 1),
          lens->ip_len - (int) sizeof(ip_hdr_t), 0, ptrs);
      break;

    case 4:
      ip_hdr->ip_dst = ip_hdr->ip_src;
      ip_hdr->ip_src = interface_1_addr;
      update_ip_checksum(ip_hdr);
      fill_icmp_source_quench_receiver(
          (Source_Quench_Message_hdr *) (ip_hdr + 1),
          lens->ip_len - (int) sizeof(ip_hdr_t), ptrs);
      break;

    case 5:
      ip_hdr->ip_dst = ip_hdr->ip_src;
      ip_hdr->ip_src = interface_1_addr;
      update_ip_checksum(ip_hdr);
      fill_icmp_redir_receiver((Redirect_Message_hdr *) (ip_hdr + 1),
                               lens->ip_len - (int) sizeof(ip_hdr_t), 0, ptrs);
      break;

    case 11:
      ip_hdr->ip_dst = ip_hdr->ip_src;
      ip_hdr->ip_src = interface_1_addr;
      update_ip_checksum(ip_hdr);
      fill_icmp_time_exceed_receiver((Time_Exceeded_Message_hdr *) (ip_hdr + 1),
                                     lens->ip_len - (int) sizeof(ip_hdr_t), 0,
                                     ptrs);
      break;

    case 12:
      ip_hdr->ip_dst = ip_hdr->ip_src;
      ip_hdr->ip_src = interface_1_addr;
      ip_hdr->ip_tos = 0;
      update_ip_checksum(ip_hdr);
      fill_icmp_para_prob_receiver(
          (Parameter_Problem_Message_hdr *) (ip_hdr + 1),
          lens->ip_len - (int) sizeof(ip_hdr_t), ptrs);
      break;

    case 16:
      reverse_ip(ip_hdr);
      update_ip_checksum(ip_hdr);
      fill_icmp_info_receiver(
          (Information_Request_or_Information_Reply_Message_hdr *) (ip_hdr + 1),
          lens->icmp_len, 16);

    case igmp_construct_reply:
      reverse_ip(ip_hdr);
      update_ip_checksum(ip_hdr);
      fill_igmp_igmp_receiver(
          (INTERNET_GROUP_MANAGEMENT_PROTOCOL_hdr *) (ip_hdr + 1),
          lens->ip_len - (int) sizeof(ip_hdr_t), igmp_report, ptrs);
  }
  free(buffer);
  // no need to explicitly send the packet, it is in the kernel
  // processing chain already
}

int proces_pkts_from_netfilterq(bool verbose = false) {
  struct nfq_handle *h;
  struct nfq_q_handle *qh;
  int fd;
  int rv;
  char buf[4096] __attribute__((aligned));

  if (verbose) printf("opening library handle\n");
  h = nfq_open();
  if (!h) {
    fprintf(stderr, "error during nfq_open()\n");
    return 1;
  }

  if (verbose)
    printf("unbinding existing nf_queue handler for AF_INET (if any)\n");
  if (nfq_unbind_pf(h, AF_INET) < 0) {
    fprintf(stderr, "error during nfq_unbind_pf()\n");
    return 1;
  }

  if (verbose)
    printf("binding nfnetlink_queue as nf_queue handler for AF_INET\n");
  if (nfq_bind_pf(h, AF_INET) < 0) {
    fprintf(stderr, "error during nfq_bind_pf()\n");
    return 1;
  }

  if (verbose) printf("binding this socket to queue '0'\n");
  qh = nfq_create_queue(h, 0, &cb, NULL);
  if (!qh) {
    fprintf(stderr, "error during nfq_create_queue()\n");
    return 1;
  }

  if (verbose) printf("setting copy_packet mode\n");
  if (nfq_set_mode(qh, NFQNL_COPY_PACKET, 0xffff) < 0) {
    fprintf(stderr, "can't set packet_copy mode\n");
    return 1;
  }

  fd = nfq_fd(h);
  while ((rv = recv(fd, buf, sizeof(buf), 0))) {
    if (verbose) printf("pkt received\n");
    nfq_handle_packet(h, buf, rv);
  }
  nfq_destroy_queue(qh);
  nfq_close(h);

  return 0;
}

#endif  // NETFILTERQ_H_
