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

#ifndef PARAGRAPH_H_
#define PARAGRAPH_H_

#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include "./utils.h"

const std::vector<std::string> bad_info{"[Page", "Sep", "RFC", "---"};

bool keep_info(std::string str) {
  for (const auto& bad_elem : bad_info) {
    if (str.find(bad_elem) != std::string::npos) {
      return false;
    }
  }
  return true;
}

class Paragraph {
 public:
  std::vector<std::string> ir_;

  Paragraph(std::string topic_line, std::string line) {
    topic_ = topic_line;
    //    std::string::iterator new_end = std::unique(line.begin(), line.end(),
    //    BothAreReturns); line.erase(new_end, line.end());
    content_ = line;
  }

  void print() {
    std::cout << topic_ << std::endl;
    std::cout << content_ << std::endl;
  }

  void print_ir() {
    std::cout << "Print IR: " << std::endl;
    for (const auto& ir : ir_) {
      std::cout << "\t" << ir << std::endl;
    }
  }

  void writeout(std::string filename) {
    std::ofstream outfile(filename);
    outfile << topic_ << std::endl;
    outfile << content_ << std::endl;
  }

  void trim_ascii() {
    const std::string pattern =
        "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+";
    int start_line = -1;
    std::vector<std::string> str_split;
    std::stringstream ss(content_);
    std::string single_line;
    while (getline(ss, single_line, '\n')) {
      str_split.push_back(single_line);
    }

    for (size_t i = 0; i < str_split.size(); i++) {
      if (str_split[i].find(pattern) != std::string::npos) {
        start_line = i;
      }
    }

    if (start_line != -1) {
      std::string trimmed_content;
      for (size_t j = start_line + 1; j < str_split.size(); j++) {
        trimmed_content.append(str_split[j]);
        trimmed_content.append("\n");
      }
      content_ = trimmed_content;
    }
  }

  std::string get_topic() { return topic_; }
  std::string get_content() { return content_; }

 private:
  std::string topic_;
  std::string content_;
};

std::vector<Paragraph> new_sliceParagraph(std::string raw_text) {
  const std::string delimiter = "\n";
  std::string per_line;
  std::vector<Paragraph> sub_paragraph_bank;
  std::string per_topic;
  std::string per_content;
  bool push_new = false;
  size_t pos = 0;
  size_t space_cnt, last_indent;
  bool first_indent = true, allow = false;
  size_t space_std = 0;

  while ((pos = raw_text.find(delimiter)) != std::string::npos) {
    per_line = raw_text.substr(0, pos);
    // std::cout<<"per_line: "<<per_line<<std::endl;
    raw_text.erase(0, pos + delimiter.length());

    // check if line is not empty
    if ((space_cnt = per_line.find_first_not_of(" \t")) != std::string::npos) {
      if (first_indent) {
        // store indentation info
        space_std = space_cnt;
        last_indent = space_cnt;
        per_topic = per_line;
        first_indent = false;
      }

      if (space_cnt == space_std) {
        // new field
        if (space_cnt != last_indent) {
          push_new = true;
        } else {
          per_topic = per_line;
        }
      } else {
        // descriptions
        if (space_cnt < space_std) {
          std::cout << "Wrong structure alignment for field parsing"
                    << std::endl;
          break;
        }
        allow = true;  // permit empty line before register the whole chunk
        per_content.append(per_line);
        per_content.append("\n");
      }

      last_indent = space_cnt;

      // empty line
    } else if (allow) {
      per_content.append("\n");
    }

    if (push_new && !per_content.empty()) {
      per_content = per_content.substr(0, per_content.size() - 1);
      Paragraph para(per_topic, per_content);
      sub_paragraph_bank.push_back(para);
      per_content.clear();
      per_topic.clear();
      allow = false;
      push_new = false;
      per_topic = per_line;
    }
  }

  if (!per_content.empty()) {
    Paragraph para(convert_to_lower(per_topic), per_content);
    sub_paragraph_bank.push_back(para);
  }

  // for (auto& sub_paragraph: sub_paragraph_bank) {
  //   sub_paragraph.print();
  // }

  return sub_paragraph_bank;
}

#endif  // PARAGRAPH_H_
