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

#ifndef GEN_H_
#define GEN_H_

#include "helper.h"
#include "icmp_hdr.h"
#include "igmp_hdr.h"
#include "meta.h"
#include "proto.h"

void fill_icmp_dest_unreachable_receiver(
    Destination_Unreachable_Message_hdr *hdr, uint16_t length, int code_value,
    proto_ptr_t *ptrs) {
  char *payload = (char *)(hdr + 1);
  // The source network and address from the original datagram's data
  copy(&payload, (char *)ptrs->ip_ptr, 28);
  // Set type to 3
  hdr->type = 3;
  // 0 = net unreachable;
  // 1 = host unreachable;
  // 2 = protocol unreachable;
  // 3 = port unreachable;
  // 4 = fragmentation needed and DF set;
  // 5 = source route failed
  hdr->code = code_value;
  // For computing the checksum , the checksum field should be zero
  hdr->checksum = 0;
  // The checksum is the 16-bit one's complement of the one's complement sum of
  // the ICMP message starting with the ICMP Type
  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *)&hdr->type, length));
}

void fill_icmp_echo_receiver(Echo_or_Echo_Reply_Message_hdr *hdr,
                             uint16_t length, int type_value, proto_len_t *lens,
                             proto_ptr_t *ptrs) {
  char *data = (char *)(hdr + 1);
  // 0 for echo reply message
  hdr->type = type_value;
  // Set code to 0
  hdr->code = 0;
  // If code equals 0, an identifier may be zero to help match echos and replies
  if (hdr->code == 0) {
    hdr->identifier = 0;
  }
  // If code equals 0, a sequence number may be zero to help match echos and
  // replies
  if (hdr->code == 0) {
    hdr->sequence_number = 0;
  }
  // For computing the checksum , the checksum field should be zero
  hdr->checksum = 0;
  // For computing the checksum, if the total length is odd, the received data
  // is padded with one octet of zeros
  if (isodd(length)) {
    pad((char **)&ptrs->eth_ptr, lens->eth_len, sizeof(*data), '0', 1);
    length += 1;
  }
  // The checksum is the 16-bit one's complement of the one's complement sum of
  // the ICMP message starting with the ICMP Type
  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *)&hdr->type, length));
}

void fill_icmp_echo_sender(Echo_or_Echo_Reply_Message_hdr *hdr, uint16_t length,
                           int type_value, proto_len_t *lens,
                           proto_ptr_t *ptrs) {
  char *data = (char *)(hdr + 1);
  // 8 for echo message;
  // 0 for echo reply message
  hdr->type = type_value;
  // Set code to 0
  hdr->code = 0;
  // If code equals 0, an identifier may be zero to help match echos and replies
  if (hdr->code == 0) {
    hdr->identifier = 0;
  }
  // If code equals 0, a sequence number may be zero to help match echos and
  // replies
  if (hdr->code == 0) {
    hdr->sequence_number = 0;
  }
  // For computing the checksum , the checksum field should be zero
  hdr->checksum = 0;
  // For computing the checksum, if the total length is odd, the received data
  // is padded with one octet of zeros
  if (isodd(length)) {
    pad((char **)&ptrs->eth_ptr, lens->eth_len, sizeof(*data), '0', 1);
    length += 1;
  }
  // The checksum is the 16-bit one's complement of the one's complement sum of
  // the ICMP message starting with the ICMP Type
  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *)&hdr->type, length));
}

void fill_icmp_info_receiver(
    Information_Request_or_Information_Reply_Message_hdr *hdr, uint16_t length,
    int type_value) {
  // 15 for information request message;
  // 16 for information reply message
  hdr->type = type_value;
  // Set code to 0
  hdr->code = 0;
  // If code equals 0, an identifier may be zero to help match request and
  // replies
  if (hdr->code == 0) {
    hdr->identifier = 0;
  }
  // If code equals 0, a sequence number may be zero to help match request and
  // replies
  if (hdr->code == 0) {
    hdr->sequence_number = 0;
  }
  // For computing the checksum , the checksum field should be zero
  hdr->checksum = 0;
  // The checksum is the 16-bit one's complement of the one's complement sum of
  // the ICMP message starting with the ICMP Type
  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *)&hdr->type, length));
}

void fill_icmp_para_prob_receiver(Parameter_Problem_Message_hdr *hdr,
                                  uint16_t length, proto_ptr_t *ptrs) {
  char *payload = (char *)(hdr + 1);
  // The source network and address from the original datagram's data
  copy(&payload, (char *)ptrs->ip_ptr, 28);
  // Set type to 12
  hdr->type = 12;
  // 0 = pointer indicates the error
  hdr->code = 0;
  // For computing the checksum , the checksum field should be zero
  hdr->checksum = 0;
  // The checksum is the 16-bit one's complement of the one's complement sum of
  // the ICMP message starting with the ICMP Type
  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *)&hdr->type, length));
}

void fill_icmp_redir_receiver(Redirect_Message_hdr *hdr, uint16_t length,
                              int code_value, proto_ptr_t *ptrs) {
  char *payload = (char *)(hdr + 1);
  // The source network and address of the original datagram's data
  copy(&payload, (char *)ptrs->ip_ptr, 28);
  // Set type to 5
  hdr->type = 5;
  // 0 = Redirect datagrams for the Network
  // 1 = Redirect datagrams for the Host
  // 2 = Redirect datagrams for the Type of Service and Network
  // 3 = Redirect datagrams for the Type of Service and Host
  hdr->code = code_value;
  // Gateway Internet Adrress is the address of the gateway of the internet
  // destination address of the original datagram's
  hdr->gateway_internet_address = find_gateway(ptrs->ip_ptr);
  // For computing the checksum , the checksum field should be zero
  hdr->checksum = 0;
  // The checksum is the 16-bit one's complement of the one's complement sum of
  // the ICMP message starting with the ICMP Type
  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *)&hdr->type, length));
}

void fill_icmp_source_quench_receiver(Source_Quench_Message_hdr *hdr,
                                      uint16_t length, proto_ptr_t *ptrs) {
  char *payload = (char *)(hdr + 1);
  // The source network and address of the original datagram's data
  copy(&payload, (char *)ptrs->ip_ptr, 28);
  // Set type to 4
  hdr->type = 4;
  // Set code to 0
  hdr->code = 0;
  // For computing the checksum , the checksum field should be zero
  hdr->checksum = 0;
  // The checksum is the 16-bit one's complement of the one's complement sum of
  // the ICMP message starting with the ICMP Type
  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *)&hdr->type, length));
}

void fill_icmp_time_exceed_receiver(Time_Exceeded_Message_hdr *hdr,
                                    uint16_t length, int code_value,
                                    proto_ptr_t *ptrs) {
  char *payload = (char *)(hdr + 1);
  // The source network and address from the original datagram's data
  copy(&payload, (char *)ptrs->ip_ptr, 28);
  // Set type to 11
  hdr->type = 11;
  // 0 = time to live exceeded in transit;
  // 1 = fragment reassembly time exceeded
  hdr->code = code_value;
  // For computing the checksum , the checksum field should be zero
  hdr->checksum = 0;
  // The checksum is the 16-bit one's complement of the one's complement sum of
  // the ICMP message starting with the ICMP Type
  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *)&hdr->type, length));
}

void fill_icmp_timestamp_receiver(Timestamp_or_Timestamp_Reply_Message_hdr *hdr,
                                  uint16_t length, int type_value) {
  // 14 for timestamp reply message
  hdr->type = type_value;
  // Set code to 0
  hdr->code = 0;
  // If code equals 0, an identifier may be zero to help match timestamp and
  // replies
  if (hdr->code == 0) {
    hdr->identifier = 0;
  }
  // If code equals 0, a sequence number may be zero to help match timestamp and
  // replies
  if (hdr->code == 0) {
    hdr->sequence_number = 0;
  }
  // For computing the checksum , the checksum field should be zero
  hdr->checksum = 0;
  // The checksum is the 16-bit one's complement of the one's complement sum of
  // the ICMP message starting with the ICMP Type
  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *)&hdr->type, length));
}

void fill_icmp_timestamp_sender(Timestamp_or_Timestamp_Reply_Message_hdr *hdr,
                                uint16_t length, int type_value) {
  // 13 for timestamp message;
  // 14 for timestamp reply message
  hdr->type = type_value;
  // Set code to 0
  hdr->code = 0;
  // If code equals 0, an identifier may be zero to help match timestamp and
  // replies
  if (hdr->code == 0) {
    hdr->identifier = 0;
  }
  // If code equals 0, a sequence number may be zero to help match timestamp and
  // replies
  if (hdr->code == 0) {
    hdr->sequence_number = 0;
  }
  // For computing the checksum , the checksum field should be zero
  hdr->checksum = 0;
  // The checksum is the 16-bit one's complement of the one's complement sum of
  // the ICMP message starting with the ICMP Type
  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *)&hdr->type, length));
}

void fill_igmp_igmp_sender(INTERNET_GROUP_MANAGEMENT_PROTOCOL_hdr *hdr,
                           uint16_t length, int type_value) {
  // Set version to 1
  hdr->version = 1;

  // 1 = Host Membership Query,
  // 2 = Host Membership Report
  hdr->type = type_value;

  // Unused field is zeroed when sent
  /*send*/
  hdr->unused = 0;

  // Unused field is ignored when received
  // The group address field is ignored when received
  /*receive*/
  dummy_action();

  // For a Host Membership Query message, the group address field is zeroed when
  // sent
  /*send*/
  hdr->group_address = 0;

  // For computing the checksum, the checksum field is zero
  hdr->checksum = 0;

  // The checksum is the 16-bit one's complement of the one's complement sum of
  // the IGMP message
  hdr->checksum =
      u16bit_ones_complement(ones_complement_sum((const void *)hdr, length));
}

void fill_igmp_igmp_receiver(INTERNET_GROUP_MANAGEMENT_PROTOCOL_hdr *hdr,
                             uint16_t length, int type_value,
                             proto_ptr_t *ptrs) {
  // Set version to 1
  hdr->version = 1;

  // 1 = Host Membership Query,
  // 2 = Host Membership Report
  hdr->type = type_value;

  // Unused field is zeroed when sent
  /*send*/
  hdr->unused = 0;

  // Unused field is ignored when received
  // The group address field is ignored when received
  /*receive*/
  dummy_action();

  // For a Host Membership Report message, the group address field holds the IP
  // host group address of the group being reported
  hdr->group_address = find_group_addr(ptrs->ip_ptr);

  // For computing the checksum, the checksum field is zero
  hdr->checksum = 0;

  // The checksum is the 16-bit one's complement of the one's complement sum of
  // the IGMP message
  hdr->checksum =
      u16bit_ones_complement(ones_complement_sum((const void *)hdr, length));
}

#endif  // GEN_H_
