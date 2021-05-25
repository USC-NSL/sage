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

#ifndef EXTTOOL_H_
#define EXTTOOL_H_

#include <stdio.h>
#include <stdlib.h>

#include <algorithm>
#include <cstring>
#include <regex>
#include <set>
#include <string>
#include <vector>

#include "./register_meta.h"
#include "./utils.h"

bool match_equal(std::regex e, std::string target) {
  if (std::regex_match(target, e)) {
    return true;
  }
  return false;
}

std::vector<std::string> execTool(std::string protocol, std::string topic,
                                  std::string field, std::string text,
                                  std::string path_name, bool lf_only,
                                  std::string lf_checks) {
  const std::string file_path = path_name + "/utils/phraser/data/EN";
  const std::string file_name = file_path + "/input.txt";

  size_t pos = 0;
  std::vector<std::string> IR;
  std::vector<std::string> SENT;
  std::vector<std::string> SENT_ID;

  bool last_return = false;
  bool ccg_parse = true;

  for (size_t cnt = 0; cnt < text.size(); cnt++) {
    if (text[cnt] == '\n' || text[cnt] == '\r') {
      if (last_return) {
        text[cnt] = ' ';
        text[cnt - 1] = '\n';
      } else {
        text[cnt] = ' ';
        last_return = true;
      }
    } else {
      last_return = false;
      if (text[cnt] == '\t') text[cnt] = ' ';
    }

    if (cnt == text.size() - 1 && text[cnt] == ' ') {
      text[cnt] = '\n';
    }
  }

  std::vector<std::string> count_num;
  std::string::iterator new_end =
      std::unique(text.begin(), text.end(), BothAreSpaces);
  text.erase(new_end, text.end());
  pos = text.find_last_not_of(" \t\n\r");
  text = text.substr(0, pos + 1);
  pos = text.find_first_not_of(" \t\n\r");
  text = text.substr(pos);

  // Handle one word assignment case
  std::string text_copy = text;
  std::size_t found = text_copy.find_first_not_of(" \t\r");
  text_copy = text_copy.substr(found);

  std::string cut_text;
  std::string cmd;

  const std::string env_str = "{\"protocol\":\"" + protocol +
                              "\",\"message\":\"" + topic + "\",\"field\":\"" +
                              field + "\"}";

  while ((pos = text_copy.find(" ")) != std::string::npos) {
    cut_text = text_copy.substr(0, pos);
    count_num.push_back(cut_text);
    if ((pos + 1) <= text_copy.size()) {
      text_copy = text_copy.substr(pos + 1);
    } else {
      break;
    }
  }
  if (!text_copy.empty()) {
    count_num.push_back(text_copy);
  }
  if (count_num.size() == 1) {
    std::string assign_value =
        "\'@Is\'(\'" + field + "\',\'" + count_num[0] + "\')";
    std::string sent_to_db = "Set " + field + " to " + count_num[0];

    register_meta_sentence(protocol, topic, field, sent_to_db, 0);
    register_mapping_lf(topic, field, sent_to_db, std::to_string(0),
                        assign_value, env_str);
    // std::cout<<cmd<<std::endl;
    SENT.push_back(sent_to_db);
    SENT_ID.push_back("0");
    IR.push_back(assign_value);
    ccg_parse = false;
    //    return IR;
  }
  // End of one word assignment case

  std::vector<std::string> sentences;
  std::vector<std::string> pre_sentences;

  std::regex rgx("([\n])");
  std::sregex_token_iterator iter(text.begin(), text.end(), rgx, -1);
  std::sregex_token_iterator end;

  for (; iter != end; ++iter) {
    if (!(iter->str().empty())) {
      pre_sentences.push_back(*iter);
    }
  }

  for (size_t chunk_cnt = 0; chunk_cnt < pre_sentences.size(); chunk_cnt++) {
    std::string copy = pre_sentences[chunk_cnt];
    pos = copy.find(". ");
    while (pos != std::string::npos) {
      sentences.push_back(copy.substr(0, pos));
      copy = copy.substr(pos + 1);
      pos = copy.find(". ");
    }
    if (!copy.empty()) {
      sentences.push_back(copy);
    }
  }

  // Match sentences with equal mark inside
  std::regex e(".*=.*");
  std::regex arrow(".*<-.*");
  std::vector<std::string> reserved_relations;
  std::string lhstr, rhstr;
  for (size_t idx = 0; idx < sentences.size(); idx++) {
    pos = sentences[idx].find_last_not_of(" \t\n\r");
    sentences[idx] = sentences[idx].substr(0, pos + 1);
    pos = sentences[idx].find_first_not_of(" \t\n\r");
    sentences[idx] = sentences[idx].substr(pos);
    if (match_equal(arrow, sentences[idx])) {
      std::string toReplace("<-");
      pos = sentences[idx].find(toReplace);
      // sentences[idx] = sentences[idx].replace(pos,toReplace.length()," = ");
      lhstr = sentences[idx].substr(0, pos);
      rhstr = sentences[idx].substr(pos + toReplace.length());
      register_meta_sentence(protocol, topic, field, sentences[idx], idx);
      std::string pseudo_code =
          "\'@Pseudo\'(\'" + lhstr + "\',\'" + rhstr + "\')";
      register_mapping_lf(topic, field, sentences[idx], std::to_string(idx),
                          pseudo_code, env_str);
      SENT.push_back(sentences[idx]);
      SENT_ID.push_back(std::to_string(idx));
      IR.push_back(pseudo_code);
      continue;
    }

    if (match_equal(e, sentences[idx])) {
      pos = sentences[idx].find("=");
      lhstr = sentences[idx].substr(0, pos);
      rhstr = sentences[idx].substr(pos + 1);
      if (find_multi_word(lhstr) && find_multi_word(rhstr)) {
        sentences[idx] =
            std::regex_replace(sentences[idx], std::regex("= "), "equals ");
        reserved_relations.push_back(sentences[idx]);
      } else {
        register_meta_sentence(protocol, topic, field, sentences[idx], idx);
        pos = lhstr.find_first_not_of(" \t");
        lhstr = lhstr.substr(pos);
        pos = lhstr.find_last_not_of(" .,;");
        lhstr = lhstr.substr(0, pos + 1);

        pos = rhstr.find_first_not_of(" \t");
        rhstr = rhstr.substr(pos);
        pos = rhstr.find_last_not_of(" .,;");
        rhstr = rhstr.substr(0, pos + 1);
        std::string temp;
        if (sentences.size() > 1) {
          temp = "\'@Associate\'(\'" + lhstr + "\',\'" + rhstr + "\')";
        } else {
          temp = "\'@Is\'(\'" + lhstr + "\',\'" + rhstr + "\')";
        }

        register_mapping_lf(topic, field, sentences[idx], std::to_string(idx),
                            temp, env_str);
        SENT.push_back(sentences[idx]);
        SENT_ID.push_back(std::to_string(idx));
        IR.push_back(temp);
      }
    } else {
      reserved_relations.push_back(sentences[idx]);
    }
  }

  // Checkpoint if there requires more conversion to logical forms
  if (reserved_relations.empty()) {
    ccg_parse = false;
  }
  if (ccg_parse) {
    for (size_t idx = 0; idx < reserved_relations.size(); idx++) {
      text = reserved_relations[idx];
      // Register sentence to metadata system
      register_meta_sentence(protocol, topic, field, text, idx);

      cmd = "cd utils/phraser; python3 corenlp.py -s \"" + text + "\" " +
            "-i " + std::to_string(idx) + " >nul 2>nul";
      exec_command(cmd);

      // Read in annotation from AutoPhrase
      std::string output_filepath =
          path_name + "/utils/phraser/models/DBLP/output.txt";
      std::ifstream fp_in(output_filepath);
      std::string domain_result;
      std::string line;
      while (getline(fp_in, line)) {
        domain_result = domain_result + line;
      }

      // Debug code
      std::cout << "Sentence from Phraser output: " << domain_result
                << std::endl;

      // Start to replace labels with single quote
      std::vector<std::string> domain_words;
      std::string start_delim = "<phrase>";
      std::string end_delim = "</phrase>";

      std::size_t start_pos, end_of_first_delim, end_pos = 0;
      start_pos = domain_result.find(start_delim);
      end_pos = domain_result.find(end_delim);
      std::string label_word;
      while (start_pos != std::string::npos) {
        end_of_first_delim = start_pos + start_delim.length();
        label_word = domain_result.substr(end_of_first_delim,
                                          end_pos - end_of_first_delim);
        if (std::find(domain_words.begin(), domain_words.end(), label_word) ==
            domain_words.end()) {
          domain_words.push_back(label_word);
        }
        domain_result.replace(end_pos, end_delim.size(), "'");
        domain_result.replace(start_pos, start_delim.size(), "'");
        start_pos = domain_result.find(start_delim);
        end_pos = domain_result.find(end_delim);
      }
      // End of replacement of lebels to single quote

      // Debug Code
      std::cout << "Sentence to CCG: " << domain_result << std::endl;
      update_mapping_label(topic, field, text, std::to_string(idx),
                           domain_result);

      // Run CCG and Logic Form Checker
      std::ifstream fp_read;
      std::string ccg_result_path = path_name + "/utils/ccg_tool/CCGresult.txt";
      std::remove(ccg_result_path.c_str());  // Clean up stale result
      std::string ir_result;

      // call CCG
      cmd = "python3 utils/ccg_tool/parse_rfc.py -c -s \"" + domain_result +
            "\" -m \"" + topic + "\" -n \"" + field + "\" --env \'" + env_str +
            "\'";
      if (!lf_checks.empty()) {
        cmd += " -C " + lf_checks;
      }
      exec_command(cmd);

      fp_read.open(ccg_result_path);

      while (std::getline(fp_read, ir_result)) {
        // std::cout<<"IR result: "<<ir_result<<std::endl;
        size_t pos = ir_result.find("~");
        std::string ir = ir_result.substr(0, pos);
        IR.push_back(ir);

        ir_result = ir_result.substr(pos + 1);
        std::string sent = ir_result.substr(0, pos = ir_result.find("~"));
        SENT.push_back(sent);

        ir_result = ir_result.substr(pos + 1);
        std::string recv = ir_result.substr(0, ir_result.find("~"));
        SENT_ID.push_back(recv);
      }
      fp_read.close();
      std::remove(ccg_result_path.c_str());
    }
    // Run Logic Form Code Generator
  }

  if (lf_only) {
    return IR;
  }

  std::cout << "Logic Form Code Generator Output: " << std::endl;
  const std::string codegen_dir = "utils/code_generator";
  const std::string codegen_outfile = codegen_dir + "/code_out.txt";

  std::vector<std::string>::iterator ir_it =
      std::find_if(IR.begin(), IR.end(), [](const std::string& sub_str) {
        return sub_str.find("@Pseudo") != std::string::npos;
      });
  std::string ir, sent, sent_id;
  if (ir_it != IR.end()) {
    // If pseudo code is found, replace all other IR as comments
    std::size_t pseudo_idx = ir_it - IR.begin();
    for (size_t counter = 0; counter < IR.size(); counter++) {
      ir = IR[counter];
      sent = SENT[counter];
      sent_id = SENT_ID[counter];
      if (counter != pseudo_idx) {
        std::string sent_copy = sent;
        std::replace(sent_copy.begin(), sent_copy.end(), '(', '[');
        std::replace(sent_copy.begin(), sent_copy.end(), ')', ']');
        ir = "\'@Comment\'(\'" + sent_copy + "\','')";
        register_mapping_lf(topic, field, sent, sent_id, ir, env_str);
      }
      const std::string command_codegen =
          "python3 " + codegen_dir + "/code_gen.py" +
          " --use_metadata_system " + " --outfile \"" + codegen_outfile +
          "\" --sentence \"" + sent + "\" --sentence_id " + sent_id +
          " --env \'" + env_str + "\' \"" + ir + "\";";
      exec_command(command_codegen);
    }

  } else {
    for (size_t i = 0; i < IR.size(); i++) {
      ir = IR[i];
      sent = SENT[i];
      sent_id = SENT_ID[i];
      const std::string command_codegen =
          "python3 " + codegen_dir + "/code_gen.py" +
          " --use_metadata_system " + " --outfile \"" + codegen_outfile +
          "\" --sentence \"" + sent + "\" --sentence_id " + sent_id +
          " --env \'" + env_str + "\' \"" + ir + "\";";
      exec_command(command_codegen);
    }
  }

  return IR;
}

void generate_code(const std::string message, const std::set<std::string> roles,
                   const std::string outfile, bool sp_output) {
  const std::string codegen_dir = "utils/code_generator";
  for (const auto& role : roles) {
    std::string app_str = "";
    if (sp_output) {
      app_str = " --special_purpose";
    }
    const std::string command_funcgen =
        "python3 " + codegen_dir + "/func_gen.py" + app_str +
        " --comments --message \"" + message + "\" --role \"" + role + "\"" +
        " --outfile \"" + outfile + "\" --outfile_mode \"a\";";
    exec_command(command_funcgen);

    std::ofstream fp(outfile, std::ofstream::app);
    fp << '\n';
    fp.close();
  }
}

#endif  // EXTTOOL_H_
