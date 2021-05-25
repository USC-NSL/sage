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

#ifndef HEADERGEN_H_
#define HEADERGEN_H_

#include <stdlib.h>

#include <algorithm>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "./headerImpl.h"

std::string space2underscore(std::string target_str) {
  for (size_t pos = 0; pos < target_str.size(); pos++) {
    switch (target_str[pos]) {
      case ' ':
        target_str[pos] = '_';
        break;
      case '+':
        target_str[pos] = 'w';
        break;
    }
  }
  return target_str;
}

void clean_obsolete(std::string path_name, std::string rfc_name) {
  const std::string file_name = path_name + "/" + rfc_name + "_hdr.h";
  std::ofstream fp(file_name, std::ofstream::out | std::ofstream::trunc);
  fp.close();
}

void add_head_include_guard(std::string file_name, std::string header_line) {
  std::transform(header_line.begin(), header_line.end(), header_line.begin(),
                 ::toupper);
  std::ofstream fp(file_name, std::ofstream::out);
  fp << "#ifndef " + header_line + "\n";
  fp << "#define " + header_line + "\n\n";
  fp.close();
}

void add_tail_include_guard(std::string file_name, std::string header_line) {
  std::transform(header_line.begin(), header_line.end(), header_line.begin(),
                 ::toupper);
  std::ofstream fp(file_name, std::ofstream::app);
  fp << "#endif  // " + header_line + "\n";
  fp.close();
}

void sanitize_name(std::string& name) {
  // remove illegal characters from name
  const std::string illegal_chars = "\\/:?\"'@#%/^!~<>|{}()[]";
  std::string::iterator it;
  for (it = name.begin(); it < name.end(); ++it) {
    if (illegal_chars.find(*it) != std::string::npos) {
      name.erase(it);
    }
  }
  // remove numbers from first position
  while (!name.empty() && isdigit(name[0])) {
    name.erase(0, 1);
  }
}

void hdr_gen(std::string path_name, std::string rfc_name, Paragraph para) {
  const std::string file_name = path_name + "/" + rfc_name + "_hdr.h";
  const std::string field_fname = path_name + "/" + rfc_name + "_fields.txt";
  const std::string indent = "  ";  // as of the Google C++ Style Guide
  std::ofstream fp(file_name, std::ofstream::app);
  std::ofstream fp2(field_fname, std::ofstream::app);
  std::string hdr_name = para.get_topic();
  sanitize_name(hdr_name);
  hdr_name = space2underscore(hdr_name);
  std::vector<pkt_field> fields = parse_ascii(para.get_content());
  if (!fields.empty()) {
    fp << "struct " + hdr_name + "_hdr {\n";
    for (auto& field : fields) {
      std::string size_desc = "";
      std::string field_name = space2underscore(field.field_name);
      sanitize_name(field_name);
      std::string field_type;
      switch (field.field_bit) {
        case 8:
          field_type = "uint8_t ";
          break;
        case 16:
          field_type = "uint16_t ";
          break;
        case 32:
          field_type = "uint32_t ";
          break;
        case 64:
          field_type = "uint64_t ";
          break;
        default:
          // 2 options here:
          //  1st: add as comment if size is not known or field too large
          //  to fit
          field_type = "// char * ";
          if (field.field_bit > 0) {
            size_desc = ": " + std::to_string(field.field_bit);
            // 2nd: create a bitfield
            if (field.field_bit <= 64) {
              field_type = "uint64_t ";
            }
          }
          break;
      }
      fp << indent + field_type + field_name + size_desc + ";\n";
      fp2 << field_name << "\n";
    }
    fp << "};\n\n";
  }
  fp.close();
}

#endif  // HEADERGEN_H_
