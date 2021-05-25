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

#include <ctype.h>
#include <getopt.h>

#include <cctype>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "./extTool.h"
#include "./headerGen.h"
#include "./headerImpl.h"
#include "./paragraph.h"
#include "./register_meta.h"
#include "./stateProcess.h"

const char PROG_NAME[] = "sage";

void print_usage(const std::string prog_name = PROG_NAME) {
  std::cout << "Usage: " << prog_name << " [-i/--infile str] [-p/--proto str]"
            << std::endl;
}

int main(int argc, char* argv[]) {
  // std::vector<std::string> bad_info{"[Page", "Sep", "RFC", "---"};
  std::string proto_name = "icmp";
  std::string line;
  bool section_focus = false;
  bool state_machine = false;
  bool graph_only = false;
  bool lf_only = false;
  bool sp_output = false;
  std::string path_name = get_current_dir();
  std::string file_name("");
  std::string section_name("Echo");
  std::string write_file;
  std::string var_file;
  std::string lf_checks;  // LF checks to execute
  std::vector<Paragraph> paragraph_bank;

  // Parse CLI args
  static struct option long_options[] = {{"infile", required_argument, 0, 'i'},
                                         {"proto", required_argument, 0, 'p'},
                                         {"section", required_argument, 0, 's'},
                                         {"wsec", required_argument, 0, 'w'},
                                         {"varfile", required_argument, 0, 'v'},
                                         {"checks", required_argument, 0, 'c'},
                                         {"extra", no_argument, 0, 'e'},
                                         {"graph", no_argument, 0, 'g'},
                                         {"lfonly", no_argument, 0, 'l'},
                                         {"spoutput", no_argument, 0, 'o'},
                                         {0, 0, 0, 0}};
  int opt = 0;
  int long_index = 0;
  while ((opt = getopt_long(argc, argv, "d:i:p:s:w:v:c:eglo", long_options,
                            &long_index)) != -1) {
    switch (opt) {
      case 'i':
        file_name.assign(optarg);
        break;
      case 'p':
        proto_name.assign(optarg);
        break;
      case 's':
        section_focus = true;
        section_name.assign(optarg);
        break;
      case 'w':
        write_file.assign(optarg);
        break;
      case 'v':
        var_file.assign(optarg);
        break;
      case 'e':
        state_machine = true;
        break;
      case 'g':
        graph_only = true;
        break;
      case 'l':
        lf_only = true;
        break;
      case 'o':
        sp_output = true;
        break;
      case 'c':
        lf_checks.assign(optarg);
        break;
      default:
        print_usage(argv[0]);
        exit(EXIT_FAILURE);
    }
  }
  // std::cout << "path name " << path_name << std::endl;
  if (file_name.empty()) {
    print_usage(argv[0]);
    exit(EXIT_FAILURE);
  }

  std::ifstream f_ptr(file_name);

  // Open file and parse content into paragraphs
  if (f_ptr.is_open()) {
    bool push_new = false;
    std::string topic_line;
    std::string long_str;
    bool last_line_empty = false;

    while (getline(f_ptr, line)) {
      size_t indexer = 0;
      size_t space_count = 0;
      bool find_char = false;
      if (line.empty() && !last_line_empty) {
        long_str.append("\n");
        last_line_empty = true;
      } else if (line.empty()) {
        last_line_empty = true;
      } else {
        last_line_empty = false;
      }
      while ((!find_char) && indexer < line.size()) {
        char ch = line[indexer];
        if (isspace(ch)) {
          space_count++;
        } else {
          find_char = true;

          if (space_count == 0 && keep_info(line)) {
            push_new = true;
          } else {
            if (keep_info(line)) {
              long_str.append(line);
              long_str.append("\n");
            }
          }

          if (push_new && !line.empty()) {
            Paragraph para(topic_line, long_str);
            paragraph_bank.push_back(para);
            long_str.clear();
            topic_line.clear();
            if (keep_info(line)) {
              topic_line = line;
            }
            push_new = false;
          }
          break;
        }
        indexer++;
      }
    }
    if (!long_str.empty()) {
      Paragraph para(topic_line, long_str);
      paragraph_bank.push_back(para);
    }
    f_ptr.close();
  } else {
    std::cout << "Unable to open file" << std::endl;
  }
  size_t cnt;

  if (state_machine) {
    for (int cnt = paragraph_bank.size() - 1; cnt >= 0; cnt--) {
      if (paragraph_bank[cnt].get_topic().find_first_not_of(" \t\n\r") ==
          std::string::npos) {
        paragraph_bank.erase(paragraph_bank.begin() + cnt);
      }
    }
    std::cout << "enable state machine description parsing" << std::endl;
    const std::string outfile = path_name + "/" + proto_name + "_gen.h";
    const std::string fieldfile = path_name + "/" + proto_name + "_fields.txt";
    add_head_include_guard(outfile, proto_name + "_GEN_H_");
    for (cnt = 0; cnt < paragraph_bank.size(); cnt++) {
      // fill in the necessary arguments
      paragraph_bank[cnt].ir_ =
          state_process(paragraph_bank[cnt].get_content(), path_name);
      if (!var_file.empty()) {
        concate_dynamic_term(var_file, fieldfile, path_name);
      }
      gen_state_management_code(paragraph_bank[cnt].ir_, outfile);
    }
    add_tail_include_guard(outfile, proto_name + "_GEN_H_");
    return 0;
  }

  /*
  // Display parsed paragraph
  std::cout<<"How many paragraph object? "<<paragraph_bank.size()<<std::endl;
  for(cnt = 0; cnt<paragraph_bank.size(); cnt++){
    std::cout<<paragraph_bank[cnt].get_topic()<<std::endl;
    std::cout<<"===================================================="<<std::endl;
  }
  */

  // Trim information before Introduction and after Reference
  int intro_index = -1, refer_index = -1, sec_index = -1;
  size_t para_size = paragraph_bank.size();
  for (cnt = 0; cnt < para_size; cnt++) {
    std::string str_copy = paragraph_bank[cnt].get_topic();
    if (!section_focus) {
      if (str_copy.find("Intro") != std::string::npos) {
        intro_index = cnt;
      } else if (str_copy.find("Overview") != std::string::npos) {
        intro_index = cnt;
      }
      if (str_copy.find("Refer") != std::string::npos) {
        refer_index = cnt;
      }
    } else {
      if (convert_to_lower(str_copy).find(convert_to_lower(section_name)) !=
          std::string::npos) {
        sec_index = cnt;
      }
    }
  }
  if (sec_index != -1) {
    paragraph_bank.erase(paragraph_bank.begin() + sec_index + 1,
                         paragraph_bank.end());
    paragraph_bank.erase(paragraph_bank.begin(),
                         paragraph_bank.begin() + sec_index);
  } else {
    if (refer_index != -1) {
      paragraph_bank.erase(paragraph_bank.end() - (para_size - 1 - refer_index),
                           paragraph_bank.end());
    }
    if (intro_index != -1) {
      paragraph_bank.erase(paragraph_bank.begin(),
                           paragraph_bank.begin() + intro_index);
    }
  }
  // Display parsed paragraph
  std::cout << "****************************************************"
            << std::endl;
  std::cout << "How many paragraph object? " << paragraph_bank.size()
            << std::endl;
  for (cnt = 0; cnt < paragraph_bank.size(); cnt++) {
    // Writeout file
    if (!write_file.empty()) {
      paragraph_bank[cnt].writeout(write_file);
    }

    // paragraph_bank[cnt].print();
    // std::cout<<paragraph_bank[cnt].get_content()<<std::endl;
    // clean_mds();
    std::vector<pkt_field> fields =
        parse_ascii(paragraph_bank[cnt].get_content());
    register_meta_fields(proto_name, paragraph_bank[cnt].get_topic(), fields);
    if (cnt == 0) {
      clean_obsolete(path_name, proto_name);
      add_head_include_guard(path_name + "/" + proto_name + "_hdr.h",
                             proto_name + "_HDR_H_");
    }
    hdr_gen(path_name, proto_name, paragraph_bank[cnt]);

    if (!fields.empty()) {
      std::cout << "+++++ PARSE ASCII +++++" << std::endl;
      paragraph_bank[cnt].trim_ascii();  // Trim ASCII art part
      // std::cout<< "Before slice:
      // "<<paragraph_bank[cnt].get_content()<<std::endl;
      if (graph_only) {
        continue;
      }
      std::vector<Paragraph> field_descriptions =
          new_sliceParagraph(paragraph_bank[cnt].get_content());

      std::cout << "<<<<Field Parse>>>>\n";
      for (size_t desc_cnt = 0; desc_cnt < field_descriptions.size();
           desc_cnt++) {
        std::cout << "FIELD: " << field_descriptions[desc_cnt].get_topic()
                  << std::endl;
        if (field_descriptions[desc_cnt].get_topic().find("descript") !=
            std::string::npos) {
          std::cout << "description field: skip nlp process" << std::endl;
        } else {
          // std::cout<<field_descriptions[desc_cnt].get_content()<<std::endl;

          std::string field_name(
              convert_to_lower(field_descriptions[desc_cnt].get_topic()));
          field_name.erase(0, field_name.find_first_not_of(' '));
          paragraph_bank[cnt].ir_ =
              execTool(proto_name, paragraph_bank[cnt].get_topic(), field_name,
                       field_descriptions[desc_cnt].get_content(), path_name,
                       lf_only, lf_checks);
          paragraph_bank[cnt].print_ir();
        }
      }
      std::cout << "<<<<End of Field Parse>>>>\n";
    }
    // std::cout<<"===================================================="<<std::endl;
  }
  add_tail_include_guard(path_name + "/" + proto_name + "_hdr.h",
                         proto_name + "_HDR_H_");
  if (graph_only || lf_only) {
    return 0;
  }

  // Generate Code
  const std::set<std::string> msg_types = get_msg_types(proto_name);
  if (msg_types.empty()) {
    std::cout << "No message type to generate code for." << std::endl;
    return 1;
  }
  const std::string outfile = path_name + "/" + proto_name + "_gen.h";
  add_head_include_guard(outfile, proto_name + "_GEN_H_");

  for (const auto& msg_type : msg_types) {
    std::set<std::string> roles = get_roles_of_msg(msg_type);
    if (roles.empty()) {
      // FIXME: use a proper config file and read config from there.
      // for example, libjsoncpp might do the job
      if (msg_type == "NTP Data Format") {
        roles.insert("timeout");
      } else {
        roles.insert("receiver");
      }
    }
    generate_code(msg_type, roles, outfile, sp_output);
  }

  add_tail_include_guard(outfile, proto_name + "_GEN_H_");

  std::cout << "Done." << std::endl;

  return 0;
}
