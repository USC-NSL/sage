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

#ifndef HEADERIMPL_H_
#define HEADERIMPL_H_

#include <cstdio>
#include <iostream>
#include <regex>
#include <sstream>
#include <string>
#include <vector>

#include "./utils.h"

struct pkt_field {
  std::string field_name;
  size_t field_bit;
};

class Usage {
 public:
 private:
  std::vector<pkt_field> field_vector_;
};

void trim(std::string& s) {
  size_t p = s.find_first_not_of(" \t");
  s.erase(0, p);

  p = s.find_last_not_of(" \t");
  if (std::string::npos != p) {
    s.erase(p + 1);
  }
}

size_t get_field_size(std::string field_name, size_t position) {
  if (!std::any_of(field_name.begin(), field_name.end(), ::isdigit)) {
    // no need for further processing, field name contains no number
    return (position + 1) / 2;
  }
  // but some field names specify their own size
  std::regex bit_regex("(\\d+) bits");
  std::cmatch re_match;
  std::regex_search(field_name.c_str(), re_match, bit_regex);
  size_t bit_length = std::stoi(re_match[0]);
  if (field_name.find("internet header") != std::string::npos) {
    bit_length += 160;  // add IPv4 header length
  }
  return bit_length;
}

std::vector<pkt_field> parse_field(std::string target_str) {
  std::vector<pkt_field> field_vector;
  const std::string delimiter = "|";
  size_t pos = 0;
  while ((pos = target_str.find(delimiter)) != std::string::npos) {
    pkt_field field_obj;
    if (pos > 0) {
      field_obj.field_name = convert_to_lower(target_str.substr(0, pos));
      field_obj.field_bit = get_field_size(field_obj.field_name, pos);
    } else {
      const size_t dot_pos = target_str.find("...");
      if (dot_pos != std::string::npos) {
        const size_t start_pos = target_str[0] == '|' ? 1 : 0;
        field_obj.field_name =
            convert_to_lower(target_str.substr(start_pos, dot_pos - 1));
        field_obj.field_bit = 0;
      }
    }
    trim(field_obj.field_name);
    if (!field_obj.field_name.empty()) {
      field_vector.push_back(field_obj);
    }

    target_str.erase(0, pos + delimiter.length());
  }

  return field_vector;
}

void print_pkt_format(std::vector<pkt_field>& all_pkt_format) {
  for (const auto& field : all_pkt_format) {
    printf("\tfield_name: %s, field_bit: %zd\n", field.field_name.c_str(),
           field.field_bit);
  }
}

// Parse ASCII ART
std::vector<pkt_field> parse_ascii(std::string input_str) {
  const std::string pattern =
      "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+";
  bool find_pattern = false;
  std::vector<pkt_field> tmp_field_vector;
  std::vector<std::string> str_split;
  std::stringstream ss(input_str);
  std::string single_line;
  while (getline(ss, single_line, '\n')) {
    str_split.push_back(single_line);
  }

  for (const auto& str_split_el : str_split) {
    std::string line(str_split_el);
    trim(line);

    if (find_pattern) {
      // std::cout<<"Find Pattern"<<std::endl;
      if (line.find(pattern) == std::string::npos && line[0] == '|') {
        std::vector<pkt_field> field_vector_read_from_line = parse_field(line);
        tmp_field_vector.insert(tmp_field_vector.end(),
                                field_vector_read_from_line.begin(),
                                field_vector_read_from_line.end());
      }
      if (line.empty()) {
        find_pattern = false;
        // tmp_field_vector.clear();
        // printf( find_pattern ? "true\n":"false\n");
      }
    } else if (line.find(pattern) != std::string::npos) {
      tmp_field_vector.clear();
      find_pattern = true;
    }
  }

  return tmp_field_vector;
}

#endif  // HEADERIMPL_H_
