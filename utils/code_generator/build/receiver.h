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

#ifndef RECEIVER_H_
#define RECEIVER_H_

#include <string>

#include "./helper.h"

void construct_reply(int, proto_len_t*, proto_ptr_t*);

bool verify_eth_hdr(uint8_t* hdr_ptr, int len) {
  // Return true if the argument 'len' is large
  // enough to hold an ethernet header struct

  if (len < (int) sizeof(ether_hdr_t)) {
    drop();
    return false;
  }
  return true;
}

bool verify_ip_hdr(uint8_t* hdr_ptr, int len, proto_len_t* lens,
                   proto_ptr_t* ptrs) {
  // Return true if the argument 'len' is large
  // enough to hold an ip header struct, and if
  // the ip checksum is computed correctly.

  if (len < (int) sizeof(ip_hdr_t)) {
    drop();
    return false;
  }
  ip_hdr_t* ip_hdr = (ip_hdr_t*) hdr_ptr;
  ip_hdr_t* cpy_buf = (ip_hdr_t*) malloc((int) sizeof(ip_hdr_t));
  memcpy(cpy_buf, ip_hdr, (int) sizeof(ip_hdr_t));
  cpy_buf->ip_sum = 0;
  uint16_t cksum = u16bit_ones_complement(
      ones_complement_sum((const void*) cpy_buf, (int) sizeof(struct ip_hdr)));
  if (cksum != ip_hdr->ip_sum) {
    return false;
  }

  // if (!match_if(ip_hdr->ip_dst)) {
  //   printf("Packet is dest unreachable\n");
  //   construct_reply(3, lens, ptrs);
  //   return false;
  // }

  if (same_subnet(ip_hdr->ip_dst, interface_1_addr)) {
    printf("Packet needs to be redirected\n");
    construct_reply(5, lens, ptrs);
    return false;
  }

  if (ip_hdr->ip_ttl == 1) {
    printf("Time exceeds...\n");
    construct_reply(11, lens, ptrs);
    return false;
  }

  if (ip_hdr->ip_tos != 0) {
    printf("Parameter Problem...type of service is wrong\n");
    construct_reply(12, lens, ptrs);
    return false;
  }

  return true;
}

bool verify_icmp_hdr(uint8_t* hdr_ptr, int len) {
  // Return true if the argument 'len' is large enough
  // to hold icmp echo/echo-reply message header and verify if
  // each field value is a valid/correct value

  if (len < (int) sizeof(Echo_or_Echo_Reply_Message_hdr)) {
    drop();
    return false;
  }
  Echo_or_Echo_Reply_Message_hdr* echo_ptr =
      (Echo_or_Echo_Reply_Message_hdr*) hdr_ptr;
  if (!(echo_ptr->code == 0)) return false;
  if (!(echo_ptr->type == 8 || echo_ptr->type == 0)) return false;
  Echo_or_Echo_Reply_Message_hdr* cpy_buf =
      (Echo_or_Echo_Reply_Message_hdr*) malloc(len);
  memcpy(cpy_buf, hdr_ptr, len);
  cpy_buf->checksum = 0;
  uint16_t cksum =
      u16bit_ones_complement(ones_complement_sum((const void*) cpy_buf, len));
  if (cksum == echo_ptr->checksum)
    return true;
  else
    return false;
}

bool verify_igmp_hdr(uint8_t* hdr_ptr, int len) {
  // Return true if the argument 'len' is large enough
  // to hold igmp message header and verify if
  // each field value is a valid/correct value

  if (len < (int) sizeof(INTERNET_GROUP_MANAGEMENT_PROTOCOL_hdr)) {
    drop();
    return false;
  }

  return true;
}

void eth_action(valid_proto_t* flags, proto_len_t* lens, proto_ptr_t* ptrs) {
  // According to ether_type field value of ethernet header, decide actions.
  // If it is ether_type for ip, flag ip header to be true/valid, update
  // length starting from ip header to the tail of packet, update pointer
  // to the beginning address of ip header.

  ether_hdr_t* eth_hdr = (ether_hdr_t*) ptrs->eth_ptr;
  switch (ntohs(eth_hdr->ether_type)) {
    case ethertype_ip:
      flags->ip = true;
      lens->ip_len = lens->eth_len - (int) sizeof(ether_hdr_t);
      ptrs->ip_ptr = ptrs->eth_ptr + (int) sizeof(ether_hdr_t);
      break;
    default:
      drop();
  }
}

void ip_action(valid_proto_t* flags, proto_len_t* lens, proto_ptr_t* ptrs) {
  // According to ip_p field value of ip header, decide actions.
  // If it is ip_p for icmp, flag icmp header to be true/valid, update
  // length starting from icmp header to the tail of packet, update pointer
  // to the beginning address of icmp header.

  ip_hdr_t* ip_hdr = (ip_hdr_t*) ptrs->ip_ptr;
  // if (ip_hdr->ip_dst != interface_1_addr) {
  //   return;
  // }
  switch (ip_hdr->ip_p) {
    case ip_protocol_icmp:
      flags->icmp = true;
      lens->icmp_len = lens->ip_len - (int) sizeof(ip_hdr_t);
      ptrs->icmp_ptr = ptrs->ip_ptr + (int) sizeof(ip_hdr_t);
      break;
    case ip_protocol_igmp:
      flags->igmp = true;
      lens->igmp_len = lens->ip_len - (int) sizeof(ip_hdr_t);
      ptrs->igmp_ptr = ptrs->ip_ptr + (int) sizeof(ip_hdr_t);
      break;
    default:
      drop();
  }
}

void construct_reply(int type, proto_len_t* lens, proto_ptr_t* ptrs) {
  // Construct an echo reply packet from the sender packet,
  // where each header pointers are kept in 'ptrs' and length
  // of header to packet tail is kept in argument struct 'lens'

  printf("Construct Reply Packet ... \n");
  char* buffer = (char*) malloc(lens->eth_len);
  memcpy(buffer, ptrs->eth_ptr, lens->eth_len);
  // update ethernet header

  // update ip header
  ip_hdr_t* ip_hdr = (ip_hdr_t*) (buffer + (int) sizeof(ether_hdr_t));

  // update icmp header
  switch (type) {
    case 0:
      reverse_ip(ip_hdr);
      update_ip_checksum(ip_hdr);
      fake_fill_icmp((Echo_or_Echo_Reply_Message_hdr*) (ip_hdr + 1), 0,
                     lens->icmp_len, lens, ptrs);
      break;

    case 3:
      ip_hdr->ip_dst = ip_hdr->ip_src;
      ip_hdr->ip_src = interface_1_addr;
      update_ip_checksum(ip_hdr);
      fill_icmp_dest_unreachable_receiver(
          (Destination_Unreachable_Message_hdr*) (ip_hdr + 1),
          lens->ip_len - (int) sizeof(ip_hdr_t), 0, ptrs);
      break;

    case 4:
      ip_hdr->ip_dst = ip_hdr->ip_src;
      ip_hdr->ip_src = interface_1_addr;
      update_ip_checksum(ip_hdr);
      fill_icmp_source_quench_receiver(
          (Source_Quench_Message_hdr*) (ip_hdr + 1),
          lens->ip_len - (int) sizeof(ip_hdr_t), ptrs);
      break;

    case 5:
      ip_hdr->ip_dst = ip_hdr->ip_src;
      ip_hdr->ip_src = interface_1_addr;
      update_ip_checksum(ip_hdr);
      fill_icmp_redir_receiver((Redirect_Message_hdr*) (ip_hdr + 1),
                               lens->ip_len - (int) sizeof(ip_hdr_t), 0, ptrs);
      break;

    case 11:
      ip_hdr->ip_dst = ip_hdr->ip_src;
      ip_hdr->ip_src = interface_1_addr;
      update_ip_checksum(ip_hdr);
      fill_icmp_time_exceed_receiver((Time_Exceeded_Message_hdr*) (ip_hdr + 1),
                                     lens->ip_len - (int) sizeof(ip_hdr_t), 0,
                                     ptrs);
      break;

    case 12:
      ip_hdr->ip_dst = ip_hdr->ip_src;
      ip_hdr->ip_src = interface_1_addr;
      ip_hdr->ip_tos = 0;
      update_ip_checksum(ip_hdr);
      fill_icmp_para_prob_receiver(
          (Parameter_Problem_Message_hdr*) (ip_hdr + 1),
          lens->ip_len - (int) sizeof(ip_hdr_t), ptrs);
      break;

    case 16:
      reverse_ip(ip_hdr);
      update_ip_checksum(ip_hdr);
      fill_icmp_info_receiver(
          (Information_Request_or_Information_Reply_Message_hdr*) (ip_hdr + 1),
          lens->icmp_len, 16);

    case igmp_construct_reply:
      reverse_ip(ip_hdr);
      update_ip_checksum(ip_hdr);
      fill_igmp_igmp_receiver(
          (INTERNET_GROUP_MANAGEMENT_PROTOCOL_hdr*) (ip_hdr + 1),
          lens->ip_len - (int) sizeof(ip_hdr_t), igmp_report, ptrs);
  }

  std::string out_file = "recv_pkt.pcap";
  int errval = writeout_pcap(out_file.c_str(), buffer, lens->eth_len);
  if (errval) {
    std::cout << "Error occured in writing message to \"" << out_file;
    std::cout << "\"." << std::endl;
  }
}

void icmp_action(valid_proto_t* flags, proto_len_t* lens, proto_ptr_t* ptrs) {
  // According to type field value of icmp header, decide actions.
  // If it is type for echo message, perform contruct_reply function.
  // If it is type for echo reply message, perform dummy_action function.
  // Otherwise, perform drop function.

  // outbound_buffer_full set true to emulate source quench case
  bool outbound_buffer_full = false;

  if (outbound_buffer_full) {
    printf("Not enough outbound buffer\n");
    construct_reply(4, lens, ptrs);
    drop();
    return;
  }

  Echo_or_Echo_Reply_Message_hdr* icmp_hdr =
      (Echo_or_Echo_Reply_Message_hdr*) ptrs->icmp_ptr;
  switch (icmp_hdr->type) {
    case 8:
      printf("recv pkt is echo msg\n");
      construct_reply(0, lens, ptrs);
      break;

    case 15:
      printf("recv pkt is information request\n");
      construct_reply(16, lens, ptrs);
      break;

    case 0:
      dummy_action();
      break;
    default:
      printf("Packet Forwarded\n");
  }
}

void igmp_action(valid_proto_t* flags, proto_len_t* lens, proto_ptr_t* ptrs) {
  INTERNET_GROUP_MANAGEMENT_PROTOCOL_hdr* hdr =
      (INTERNET_GROUP_MANAGEMENT_PROTOCOL_hdr*) (ptrs->igmp_ptr);

  switch (hdr->type) {
    case igmp_query:
      printf("Get IGMP query packet...\n");
      construct_reply(igmp_construct_reply, lens, ptrs);
      break;
    case igmp_report:
      printf("Got igmp report packet\n");
      break;
    default:
      drop();
  }
}

void receiver_code_template(char* recv_pkt, int len) {
  // Parse received packet 'recv_pkt' for 'len' bytes.
  // Flag valid headers, update length info and update
  // pointers to each head of the header.

  // initialize metadata
  valid_proto_t flags = {true, false, false, false};
  proto_len_t lens = {len, 0, 0, 0};
  proto_ptr_t ptrs = {(uint8_t*) recv_pkt, nullptr, nullptr, nullptr};

  if (flags.eth) {
    ptrs.eth_ptr = (uint8_t*) recv_pkt;
    bool eth_process = verify_eth_hdr(ptrs.eth_ptr, lens.eth_len);
    if (eth_process) {
      printf("Pass verifying ethernet hdr...\n");
      eth_action(&flags, &lens, &ptrs);
    } else {
      drop();
      return;
    }
  }

  if (flags.ip) {
    bool ip_process = verify_ip_hdr(ptrs.ip_ptr, lens.ip_len, &lens, &ptrs);
    if (ip_process) {
      printf("Pass verifying ip hdr...\n");
      ip_action(&flags, &lens, &ptrs);
    } else {
      drop();
      return;
    }
  }

  if (flags.icmp) {
    bool icmp_process = verify_icmp_hdr(ptrs.icmp_ptr, lens.icmp_len);
    if (icmp_process) {
      printf("Pass verifying icmp hdr...\n");
      icmp_action(&flags, &lens, &ptrs);
    } else {
      drop();
      return;
    }
  }

  if (flags.igmp) {
    bool igmp_process = verify_igmp_hdr(ptrs.igmp_ptr, lens.igmp_len);
    if (igmp_process) {
      printf("Pass verifying igmp hdr...\n");
      igmp_action(&flags, &lens, &ptrs);
    } else {
      drop();
      return;
    }
  }

  if (!flags.icmp && !flags.igmp) {
    printf("Packet Forwarded\n");
  }

  // (Optional) Take actions regarding to the packet content
}

#endif
