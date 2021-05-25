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

#ifndef HELPER_H_
#define HELPER_H_

#include <arpa/inet.h>
#include <pcap/pcap.h>
#include <sys/types.h>
#include <time.h>

#include <string>

#include "common.h"
#include "icmp_hdr.h"
#include "meta.h"
#include "proto.h"

#define RECV_BUF_SIZE 256

void dump_binary(char* ptr, int len) {
  // Print the content for 'len' size,
  // starting from the position of 'ptr'

  for (int i = 0; i < len; ++i) {
    printf("%02x", ptr[i] & 0xff);
    if (i % 2 == 1) printf(" ");
    if (i % 16 == 15) printf("\n");
  }
  printf("\n");
}

enum fail_code {
  error = 1,
};

enum interfaces {
  // eth3: 10.0.1.1/24
  // eth2: 172.64.3.1/24
  // eth1: 192.168.2.1/24
  interface_1_addr = 0x0101000A,
  interface_1_mask = 0x0001000A,
  gateway_1_addr = 0xFE01000A,
  group_1_addr = 0x000100E0,
  interface_2_mask = 0x0002A8C0,
  gateway_2_addr = 0xFE02A8C0,
  group_2_addr = 0x000200E0,
  interface_3_mask = 0x000340AC,
  gateway_3_addr = 0xFE0340AC,
  group_3_addr = 0x000300E0,
};

bool match_if(uint32_t addr) {
  // return true if argument 'addr' is in one of
  // the known subnet. Otherwise, return false

  uint32_t subnet = addr & 0x00FFFFFF;
  bool match;
  switch (subnet) {
    case interface_1_mask:
      match = true;
      break;
    case interface_2_mask:
      match = true;
      break;
    case interface_3_mask:
      match = true;
      break;
    default:
      match = false;
  }
  return match;
}

uint32_t find_gateway(uint8_t* ip_ptr) {
  // Return the redirect gateway addr for the dest
  // address from ip header pointed by argument
  // 'ip_ptr'

  ip_hdr_t* ip_hdr = (ip_hdr_t*)ip_ptr;
  uint32_t addr = ip_hdr->ip_dst;
  uint32_t subnet = addr & 0x00FFFFFF;
  uint32_t match_addr;

  switch (subnet) {
    case interface_1_mask:
      match_addr = gateway_1_addr;
      break;
    case interface_2_mask:
      match_addr = gateway_2_addr;
      break;
    case interface_3_mask:
      match_addr = gateway_3_addr;
  }
  return match_addr;
}

uint32_t find_group_addr(uint8_t* ip_ptr) {
  // Return the registered group address for the dest
  // address from ip header pointed by argument 'ip_ptr'

  ip_hdr_t* ip_hdr = (ip_hdr_t*)ip_ptr;
  uint32_t addr = ip_hdr->ip_dst;
  uint32_t subnet = addr & 0x00FFFFFF;
  uint32_t match_addr;

  switch (subnet) {
    case interface_1_mask:
      match_addr = group_1_addr;
      break;
    case interface_2_mask:
      match_addr = group_2_addr;
      break;
    case interface_3_mask:
      match_addr = group_3_addr;
      break;
  }
  return match_addr;
}

bool same_subnet(uint32_t addr, uint32_t if_addr) {
  // return true if argument 'addr' and argument
  // 'if_addr' are in the same subnet, but 'addr'
  // is not 'if_addr'. Otherwise, return false

  uint32_t mask = 0x00FFFFFF;
  if ((addr & mask) == (if_addr & mask)) {
    if (addr != if_addr) {
      return true;
    } else {
      return false;
    }
  } else {
    return false;
  }
}

void reverse_ip(ip_hdr_t* ip_hdr) {
  // Reverse src and dst ips from pointer 'hdr'

  uint32_t tmp = ip_hdr->ip_dst;
  ip_hdr->ip_dst = ip_hdr->ip_src;
  ip_hdr->ip_src = tmp;
}

void update_ip_checksum(ip_hdr_t* hdr) {
  // Compute IP header checksum by using 16-bit
  // one's complement of one's complement sum

  hdr->ip_sum = 0;
  uint16_t result = u16bit_ones_complement(
      ones_complement_sum((const void*)hdr, sizeof(struct ip_hdr)));
  hdr->ip_sum = result;
}

void fill_ether(ether_hdr_t* hdr) {
  // Fill in Ethernet header content:
  // destination MAC address, source
  // MAC addressm and next protocol type

  hdr->ether_dhost[0] = 0x9a;
  hdr->ether_dhost[1] = 0x30;
  hdr->ether_dhost[2] = 0x40;
  hdr->ether_dhost[3] = 0xbc;
  hdr->ether_dhost[4] = 0x61;
  hdr->ether_dhost[5] = 0x6d;
  hdr->ether_shost[0] = 0xc6;
  hdr->ether_shost[1] = 0x7c;
  hdr->ether_shost[2] = 0x52;
  hdr->ether_shost[3] = 0x27;
  hdr->ether_shost[4] = 0x41;
  hdr->ether_shost[5] = 0xcc;
  hdr->ether_type = htons(ethertype_ip);
}

void fill_ip(ip_hdr_t* hdr, uint16_t length, uint8_t tos) {
  // Fill in IP header content: ip_hl, ip_v,
  // ip_tos, ip_id, ip_off, ip_ttl, ip_p,
  // ip_sum, ip_src and ip_dst

  // da uses 10.0.1.1, emulates echo/echo reply
  // da uses 204.57.7.9, emulates dest unreach
  // da uses 10.0.1.10, emulates redirect
  // ip_ttl uses 1, da uses 192.168.2.2, emulates time_exceed

  struct sockaddr_in sa, da;
  inet_pton(AF_INET, "10.0.1.100", &(sa.sin_addr));
  inet_pton(AF_INET, "204.57.7.9", &(da.sin_addr));

  hdr->ip_hl = 5;
  hdr->ip_v = 4;
  hdr->ip_tos = tos;
  hdr->ip_len = htons(84);
  hdr->ip_id = htons(0x653b);
  hdr->ip_off = htons(IP_DF);
  hdr->ip_ttl = 64;
  hdr->ip_p = ip_protocol_icmp;
  hdr->ip_src = sa.sin_addr.s_addr;
  hdr->ip_dst = da.sin_addr.s_addr;
  hdr->ip_sum = 0;
  update_ip_checksum(hdr);
}

void fake_fill_icmp(Echo_or_Echo_Reply_Message_hdr* hdr, uint8_t type,
                    uint16_t length, proto_len_t* lens, proto_ptr_t* ptrs) {
  hdr->code = 0;
  hdr->checksum = 0;
  hdr->identifier = htons(4570);
  hdr->type = type;
  hdr->sequence_number = htons(1);

  if (isodd(length)) {
    char* data = (char*)(hdr + 1);
    pad((char**)&ptrs->eth_ptr, lens->eth_len, sizeof(*data), '0', 1);
    char* new_head = (char*)malloc(length + 1);
    hdr->checksum = u16bit_ones_complement(
        ones_complement_sum((const void*)hdr, length + 1));
  } else {
    uint16_t result =
        u16bit_ones_complement(ones_complement_sum((const void*)hdr, length));
    hdr->checksum = result;
  }
}

int writeout_pcap(const char* out_file, char* hdr, uint16_t len) {
  // Write out packet content, which positions at 'hdr' and lasts
  // for 'len' bytes, to 'out_file' in pcap file format. Return 0
  // if writing file successfuly. Otherwise, return 1.

  struct pcap_file_header pfheader;
  pfheader.magic = 0xa1b2c3d4;
  pfheader.version_major = 2;
  pfheader.version_minor = 4;
  pfheader.thiszone = 0;
  pfheader.sigfigs = 0;
  pfheader.snaplen = 65535;
  pfheader.linktype = DLT_EN10MB;

  struct pcap_pkthdr pktheader;
  pktheader.ts = (struct timeval){time(0), 0};
  unsigned long pkt_size = len;
  pktheader.caplen = pkt_size;
  pktheader.len = pkt_size;

  FILE* pFile = NULL;
  pFile = fopen(out_file, "wb");
  if (!pFile) {
    return 1;
  }

  // overcome large struct timeval issue by writing out
  // pcap_pkthdr members one-by-one
  fwrite(&pfheader, 1, sizeof(pfheader), pFile);
  fwrite(&pktheader.ts, 1, 8, pFile);
  fwrite(&pktheader.caplen, 1, sizeof(pktheader.caplen), pFile);
  fwrite(&pktheader.len, 1, sizeof(pktheader.len), pFile);
  fwrite(hdr, 1, len, pFile);
  fclose(pFile);

  return 0;
}

int read_pcap_to_buf(char* buffer) {
  // Read the sender packet from pcap file format and store
  // the read content to argument 'buffer'. If read the content
  // successfully, return 0. Otherwise, return 1.

  std::string in_file = "send_pkt.pcap";

  FILE* pFile = NULL;
  pFile = fopen(in_file.c_str(), "rb");
  int readbyte = 0;

  if (pFile == NULL) {
    perror("Error opening file");
  } else {
    if ((readbyte = fread(buffer, 1, 256, pFile)) > 0) {
      printf("read in %d bytes\n", readbyte);
    }
  }
  return readbyte;
}

int read_pkt(char** pkt) {
  // Read out packet content by calling read_pcap_to_buf function
  // and trim away pcap header to keep packet content only at the
  // argument 'pkt'. Return the read in packet size.

  char* buffer = (char*)malloc(RECV_BUF_SIZE);
  int len = read_pcap_to_buf(buffer);
  int pkt_len = len - 40;
  *pkt = (char*)malloc(pkt_len);
  memcpy(*pkt, buffer + 40, pkt_len);

  printf("pkt size %d\n", pkt_len);

  return pkt_len;
}

void drop() {
  // Print 'drop packet' string when calling the function

  printf("drop recv packet\n");
}

void dummy_action() {
  // Print 'dummy action' string when calling the function

  printf("dummy action\n");
}

#endif
