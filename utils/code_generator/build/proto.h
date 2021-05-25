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

#ifndef PROTO_H_
#define PROTO_H_

#ifdef _LINUX_
#include <stdint.h>
#endif

#ifndef __LITTLE_ENDIAN
#define __LITTLE_ENDIAN 1
#endif

#ifndef __BIG_ENDIAN
#define __BIG_ENDIAN 2
#endif

#ifndef __BYTE_ORDER
#ifndef _LINUX_
#define __BYTE_ORDER __LITTLE_ENDIAN
#endif
#endif

struct ethernet_hdr {
#ifndef ETHER_ADDR_LEN
#define ETHER_ADDR_LEN 6
#endif
  uint8_t ether_dhost[ETHER_ADDR_LEN]; /* destination ethernet address */
  uint8_t ether_shost[ETHER_ADDR_LEN]; /* source ethernet address */
  uint16_t ether_type;                 /* packet type ID */
} __attribute__((packed));
typedef struct ethernet_hdr ether_hdr_t;

struct ip_hdr {
#if __BYTE_ORDER == __LITTLE_ENDIAN
  unsigned int ip_hl : 4; /* header length */
  unsigned int ip_v : 4;  /* version */
#elif __BYTE_ORDER == __BIG_ENDIAN
  unsigned int ip_v : 4;  /* version */
  unsigned int ip_hl : 4; /* header length */
#else
#error "Byte ordering not specified "
#endif
  uint8_t ip_tos;          /* type of service */
  uint16_t ip_len;         /* total length */
  uint16_t ip_id;          /* identification */
  uint16_t ip_off;         /* fragment offset field */
#define IP_RF 0x8000       /* reserved fragment flag */
#define IP_DF 0x4000       /* dont fragment flag */
#define IP_MF 0x2000       /* more fragments flag */
#define IP_OFFMASK 0x1fff  /* mask for fragmenting bits */
  uint8_t ip_ttl;          /* time to live */
  uint8_t ip_p;            /* protocol */
  uint16_t ip_sum;         /* checksum */
  uint32_t ip_src, ip_dst; /* source and dest address */
} __attribute__((packed));
typedef struct ip_hdr ip_hdr_t;

struct tcp_hdr {
  uint16_t src_port;
  uint16_t dst_port;
  uint32_t seq_num;
  uint32_t ack_num;
#if __BYTE_ORDER == __LITTLE_ENDIAN
  uint8_t reserved : 4;  // Unused reserved bits.
  uint8_t offset : 4;    // Data offset.
#elif __BYTE_ORDER == __BIG_ENDIAN
  uint8_t offset : 4;     // Data offset.
  uint8_t reserved : 4;   // Unused reserved bits.
#else
#error __BYTE_ORDER must be defined.
#endif
  uint8_t flags;  // Flags.
  uint16_t window;
  uint16_t checksum;
  uint16_t urgent_ptr;
};

enum ethertype {
  ethertype_ip = 0x0800,
};

enum ip_protocol {
  ip_protocol_icmp = 0x0001,
  ip_protocol_igmp = 0x0002,
};

enum igmp_type {
  igmp_construct_reply = -1,
  igmp_query = 0x1,
  igmp_report = 0x2,
};

enum tcp_flag {
  tcp_Fin = 0x01,
  tcp_Syn = 0x02,
  tcp_Rst = 0x04,
  tcp_Psh = 0x08,
  tcp_Ack = 0x10,
  tcp_Urg = 0x20,
};

#endif
