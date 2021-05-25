#ifndef GEN_H_
#define GEN_H_
#include "helper.h"
#include "icmp_hdr.h"
#include "meta.h"
#include "proto.h"


void fill_icmp_dest_unreachable_receiver(
    struct Destination_Unreachable_Message_hdr *hdr, uint16_t length,
    int code_value, proto_ptr_t *ptrs) {
  char *payload = (char *) (hdr + 1);
  copy(&payload, (char *) ptrs->ip_ptr, 28);

  hdr->type = 3;

  hdr->code = code_value;

  /* host use this_data */
  hdr->checksum = 0;

  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *) &hdr->type, length));
}

void fill_icmp_echo_receiver(struct Echo_or_Echo_Reply_Message_hdr *hdr,
                             uint16_t length, int type_value) {
  char *data = (char *) (hdr + 1);
  hdr->code = 0;

  hdr->type = type_value;

  hdr->checksum = 0;

  if (isodd(length)) {
    pad(&data, sizeof(*data), 0, 1);
    length += 1;
  }

  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *) &hdr->type, length));
}

void fill_icmp_echo_sender(struct Echo_or_Echo_Reply_Message_hdr *hdr,
                           uint16_t length, int type_value) {
  char *data = (char *) (hdr + 1);
  hdr->type = type_value;

  hdr->code = 0;

  if (hdr->code == 0) {
    hdr->identifier = 0;
  }

  if (hdr->code == 0) {
    hdr->sequence_number = 0;
  }

  hdr->checksum = 0;

  if (isodd(length)) {
    pad(&data, sizeof(*data), 0, 1);
    length += 1;
  }

  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *) &hdr->type, length));
}

void fill_icmp_info_receiver(
    struct Information_Request_or_Information_Reply_Message_hdr *hdr,
    uint16_t length, int type_value) {
  hdr->type = type_value;

  hdr->code = 0;

  if (hdr->code == 0) {
    hdr->identifier = 0;
  }

  if (hdr->code == 0) {
    hdr->sequence_number = 0;
  }

  hdr->checksum = 0;

  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *) &hdr->type, length));
}

void fill_icmp_para_prob_receiver(struct Parameter_Problem_Message_hdr *hdr,
                                  uint16_t length, proto_ptr_t *ptrs) {
  char *payload = (char *) (hdr + 1);
  copy(&payload, (char *) ptrs->ip_ptr, 28);

  hdr->type = 12;

  hdr->code = 0;

  /* host use this_data */
  hdr->checksum = 0;

  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *) &hdr->type, length));
}

void fill_icmp_redir_receiver(struct Redirect_Message_hdr *hdr, uint16_t length,
                              int code_value, proto_ptr_t *ptrs) {
  char *payload = (char *) (hdr + 1);
  copy(&payload, (char *) ptrs->ip_ptr, 28);

  hdr->type = 5;

  hdr->code = code_value;

  /* host use this_data */
  hdr->checksum = 0;

  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *) &hdr->type, length));
}

void fill_icmp_source_quench_receiver(struct Source_Quench_Message_hdr *hdr,
                                      uint16_t length, proto_ptr_t *ptrs) {
  char *payload = (char *) (hdr + 1);
  copy(&payload, (char *) ptrs->ip_ptr, 28);

  hdr->type = 4;

  hdr->code = 0;

  /* host use this_data */
  hdr->checksum = 0;

  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *) &hdr->type, length));
}

void fill_icmp_time_exceed_receiver(struct Time_Exceeded_Message_hdr *hdr,
                                    uint16_t length, int code_value,
                                    proto_ptr_t *ptrs) {
  char *payload = (char *) (hdr + 1);
  copy(&payload, (char *) ptrs->ip_ptr, 28);

  hdr->type = 11;

  hdr->code = code_value;

  /* host use this_data */
  hdr->checksum = 0;

  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *) &hdr->type, length));
}

void fill_icmp_timestamp_receiver(
    struct Timestamp_or_Timestamp_Reply_Message_hdr *hdr, uint16_t length,
    int type_value) {
  hdr->code = 0;

  hdr->type = type_value;

  hdr->checksum = 0;

  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *) &hdr->type, length));
}

void fill_icmp_timestamp_sender(
    struct Timestamp_or_Timestamp_Reply_Message_hdr *hdr, uint16_t length,
    int type_value) {
  hdr->type = type_value;

  hdr->code = 0;

  if (hdr->code == 0) {
    hdr->identifier = 0;
  }

  if (hdr->code == 0) {
    hdr->sequence_number = 0;
  }

  hdr->checksum = 0;

  hdr->checksum = u16bit_ones_complement(
      ones_complement_sum((const void *) &hdr->type, length));
}

#endif  /* GEN_H_ */
