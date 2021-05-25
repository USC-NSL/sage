#ifndef ICMP_HDR_H_
#define ICMP_HDR_H_

struct Destination_Unreachable_Message_hdr {
  uint8_t type;
  uint8_t code;
  uint16_t checksum;
  uint32_t unused;
};

struct Time_Exceeded_Message_hdr {
  uint8_t type;
  uint8_t code;
  uint16_t checksum;
  uint32_t unused;
};

struct Parameter_Problem_Message_hdr {
  uint8_t type;
  uint8_t code;
  uint16_t checksum;
  uint8_t pointer;
  uint64_t unused: 24;
};

struct Source_Quench_Message_hdr {
  uint8_t type;
  uint8_t code;
  uint16_t checksum;
  uint32_t unused;
};

struct Redirect_Message_hdr {
  uint8_t type;
  uint8_t code;
  uint16_t checksum;
  uint32_t gateway_internet_address;
};

struct Echo_or_Echo_Reply_Message_hdr {
  uint8_t type;
  uint8_t code;
  uint16_t checksum;
  uint16_t identifier;
  uint16_t sequence_number;
};

struct Timestamp_or_Timestamp_Reply_Message_hdr {
  uint8_t type;
  uint8_t code;
  uint16_t checksum;
  uint16_t identifier;
  uint16_t sequence_number;
  uint32_t originate_timestamp;
  uint32_t receive_timestamp;
  uint32_t transmit_timestamp;
};

struct Information_Request_or_Information_Reply_Message_hdr {
  uint8_t type;
  uint8_t code;
  uint16_t checksum;
  uint16_t identifier;
  uint16_t sequence_number;
};

#endif  /* ICMP_HDR_H_ */
