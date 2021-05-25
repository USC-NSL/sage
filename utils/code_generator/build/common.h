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

#ifndef COMMON_H_
#define COMMON_H_

#include <arpa/inet.h>
#include <pcap/pcap.h>
#include <stdlib.h>
#include <string.h>

#include "icmp_hdr.h"

bool isodd(uint32_t x) {
  // Returns true if the argument 'x' is an odd number

  return (x % 2 == 1);
}

void pad(char **data, int shift_byte, int data_len, int pad_len,
         char pad_char) {
  // Pad 'data_len' size of 'data' with 'pad_len' size of 'pad_char'

  *data = (char *)realloc(*data, data_len + pad_len);
  char *pad_start = *data + shift_byte + data_len;
  memset((void *)pad_start, pad_char, pad_len);
}

void copy(char **buffer, char *data, int len) {
  // Copy 'len' bytes of argument 'data' to 'buffer'

  memcpy((void *)(*buffer), data, len);
}

uint16_t u16bit_ones_complement(uint32_t x) {
  // Return 16-bit one's complement of the argument 'number'

  while (x > 0xffff) {
    x = (x >> 16) + (x & 0xffff);
  }
  x = htons(~x);
  if (x != 0) {
    return x;
  }
  return 0xffff;
}

uint32_t ones_complement_sum(const void *data, int len) {
  // Return one's complement sum of the argument 'data' for 'len' size

  const uint8_t *ptr = (uint8_t *)data;
  uint32_t sum;
  for (sum = 0; len >= 2; ptr += 2, len -= 2) {
    sum += ptr[0] << 8 | ptr[1];
  }
  if (len > 0) {
    sum += ptr[0] << 8;
  }
  return sum;
}

#endif  // COMMON_H_
