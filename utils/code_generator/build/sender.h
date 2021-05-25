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

#ifndef SENDER_H_
#define SENDER_H_

#include <string>

enum emulate_cases {
  base_case = 1,
  info_request = 2,
  igmp_request = 3,
};

void sender_code_template() {
  // Construct an echo message with hard-coded payload for comparison purpose.
  // The contructed echo message packet is stored in PCAP format.

  const unsigned char payload[56] = {
      0xe0, 0x70, 0x89, 0x5e, 0x00, 0x00, 0x00, 0x00, 0x53, 0xb9, 0x0b, 0x00,
      0x00, 0x00, 0x00, 0x00, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
      0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x20, 0x21, 0x22, 0x23,
      0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f,
      0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37,
  };
  uint16_t len = sizeof(ether_hdr_t) + sizeof(ip_hdr_t) +
                 sizeof(Echo_or_Echo_Reply_Message_hdr) + sizeof(payload);
  char* buffer = (char*)malloc(len);
  ether_hdr_t* eth_hdr = (ether_hdr_t*)buffer;
  ip_hdr_t* ip_hdr = (ip_hdr_t*)(buffer + sizeof(ether_hdr_t));
  Echo_or_Echo_Reply_Message_hdr* icmp_hdr =
      (Echo_or_Echo_Reply_Message_hdr*)(buffer + sizeof(ether_hdr_t) +
                                        sizeof(ip_hdr_t));
  char* pkt_payload = buffer + sizeof(ether_hdr_t) + sizeof(ip_hdr_t) +
                      sizeof(Echo_or_Echo_Reply_Message_hdr);
  memcpy(pkt_payload, payload, sizeof(payload));

  proto_len_t lens = {len, len - (int)sizeof(ether_hdr_t),
                      len - (int)sizeof(ether_hdr_t) - (int)sizeof(ip_hdr_t)};
  proto_ptr_t ptrs = {(uint8_t*)buffer, (uint8_t*)ip_hdr, (uint8_t*)icmp_hdr};

  fill_ether(eth_hdr);

  // tos value = 1 to emulate parameter problem
  uint8_t tos = 0;
  fill_ip(ip_hdr,
          sizeof(ip_hdr_t) + sizeof(Echo_or_Echo_Reply_Message_hdr) +
              sizeof(payload),
          tos);

  char* buf = (char*)malloc(len);
  Information_Request_or_Information_Reply_Message_hdr* info_ptr;
  INTERNET_GROUP_MANAGEMENT_PROTOCOL_hdr* igmp_ptr;
  // change scenario value to emulate info request, igmp_request, base_case
  uint8_t scenario = 1;
  switch (scenario) {
    case info_request:
      info_ptr =
          (Information_Request_or_Information_Reply_Message_hdr*)(buffer +
                                                                  sizeof(
                                                                      ether_hdr_t) +
                                                                  sizeof(
                                                                      ip_hdr_t));
      fill_icmp_info_receiver(
          info_ptr,
          sizeof(Information_Request_or_Information_Reply_Message_hdr) +
              sizeof(payload),
          15);
      break;

    case igmp_request:
      ip_hdr->ip_p = ip_protocol_igmp;
      len = sizeof(ether_hdr_t) + sizeof(ip_hdr_t);
      ip_hdr->ip_len = htons(sizeof(ip_hdr_t) +
                             sizeof(INTERNET_GROUP_MANAGEMENT_PROTOCOL_hdr));
      update_ip_checksum(ip_hdr);
      memcpy(buf, buffer, len);
      len = len + sizeof(INTERNET_GROUP_MANAGEMENT_PROTOCOL_hdr);
      buffer = (char*)realloc(buffer, len);
      memcpy(buffer, buf, sizeof(ether_hdr_t) + sizeof(ip_hdr_t));
      free(buf);
      igmp_ptr = (INTERNET_GROUP_MANAGEMENT_PROTOCOL_hdr*)(buffer +
                                                           sizeof(ether_hdr_t) +
                                                           sizeof(ip_hdr_t));
      fill_igmp_igmp_sender(igmp_ptr, len, 1);
      break;

    default:
      fake_fill_icmp(icmp_hdr, 8,
                     sizeof(Echo_or_Echo_Reply_Message_hdr) + sizeof(payload),
                     &lens, &ptrs);
  }

  std::string out_file = "send_pkt.pcap";

  int errval = writeout_pcap(out_file.c_str(), buffer, len);
  if (errval) {
    std::cout << "Error occured in writing message to \"" << out_file;
    std::cout << "\"." << std::endl;
  }
}

#endif
