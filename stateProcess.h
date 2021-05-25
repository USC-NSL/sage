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

#ifndef STATEPROCESS_H_
#define STATEPROCESS_H_

#include <regex>
#include <string>
#include <vector>

std::vector<std::string> state_process(std::string text,
                                       std::string path_name) {
  std::vector<std::string> IR;

  bool last_return = false;
  size_t cnt, pos;
  std::vector<std::string> sentences;
  std::vector<std::string> pre_sentences;
  std::string cmd;

  for (cnt = 0; cnt < text.size(); cnt++) {
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

  std::regex rgx("([\n])");
  std::sregex_token_iterator iter(text.begin(), text.end(), rgx, -1);
  std::sregex_token_iterator end;

  for (; iter != end; ++iter) {
    if (!(iter->str().empty())) {
      pre_sentences.push_back(*iter);
    }
  }

  for (cnt = 0; cnt < pre_sentences.size(); cnt++) {
    std::string copy = pre_sentences[cnt];
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

  for (cnt = 0; cnt < sentences.size(); cnt++) {
    // Display the parsed sentences
    // std::cout<<"\t"<<sentences[cnt]<<std::endl;
    cmd = "cd utils/phraser; python3 corenlp.py -s \"" + sentences[cnt] +
          "\" >nul 2>nul";
    exec_command(cmd);

    std::string output_filepath =
        path_name + "/utils/phraser/models/DBLP/output.txt";
    std::ifstream fp_in(output_filepath);
    std::string line;
    while (getline(fp_in, line)) {
    }
    // std::cout<<"Output: "<<line<<std::endl;

    std::string ccg_result_path = path_name + "/utils/ccg_tool/CCGresult.txt";
    std::string ir_result;
    std::ifstream fp_read;

    cmd = "python3 utils/ccg_tool/parse_rfc.py -c -s \"" + line +
          "\"; >nul 2>nul";
    exec_command(cmd);

    fp_read.open(ccg_result_path);
    while (std::getline(fp_read, ir_result)) {
      size_t pos = ir_result.find("~");
      std::string ir = ir_result.substr(0, pos);
      std::cout << ir << std::endl;
      IR.push_back(ir);
    }
    fp_read.close();
    std::remove(ccg_result_path.c_str());
  }

  return IR;
}

void gen_state_management_code(std::vector<std::string> IR,
                               std::string outfile) {
  std::string cmd;
  size_t cnt;
  std::cout << "IR aggregate results:" << std::endl;
  for (cnt = 0; cnt < IR.size(); cnt++) {
    std::cout << IR[cnt] << std::endl;
    cmd = "python3 utils/code_generator/sim_code_gen.py \"" + IR[cnt] +
          "\" -o \"" + outfile + "\";";
    exec_command(cmd);
  }
}

void concate_dynamic_term(std::string varfile, std::string fieldfile,
                          std::string path_name) {
  std::string outfile = path_name + "/utils/code_generator/dyn_term.py";
  std::ifstream f_var_ptr(varfile);
  std::ifstream f_field_ptr(fieldfile);
  std::ofstream fp(outfile, std::ofstream::app);
  std::string line;

  if (f_var_ptr.is_open()) {
    fp << "VARS = [\n";
    while (getline(f_var_ptr, line)) {
      fp << "\t\"" << line << "\",\n";
    }
    f_var_ptr.close();
  }
  fp << "]\n";
  if (f_field_ptr.is_open()) {
    fp << "FIELDS = [\n";
    while (getline(f_field_ptr, line)) {
      fp << "\t\"" << line << "\",\n";
    }
    f_field_ptr.close();
  }
  fp << "]\n";
  fp.close();
  return;
}

#endif  // STATEPROCESS_H_
