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

#ifndef UTILS_H_
#define UTILS_H_

#include <bits/stdc++.h>
#include <unistd.h>

#include <algorithm>
#include <string>

bool BothAreSpaces(char lhs, char rhs) { return (lhs == rhs) && (lhs == ' '); }
bool BothAreReturns(char lhs, char rhs) {
  return (lhs == rhs) && (lhs == '\n');
}

bool find_multi_word(std::string target_str) {
  std::string whitespaces(" \t\f\v\n\r");
  size_t found = target_str.find_first_not_of(whitespaces);
  if (found != std::string::npos) {
    target_str = target_str.substr(found);
  }
  size_t found_last = target_str.find_last_not_of(whitespaces);
  if (found_last != std::string::npos) {
    target_str.erase(found_last + 1);
  }

  if (target_str.find(" ") != std::string::npos) {
    return true;
  }
  return false;
}

std::string first_word(std::string text) {
  std::string firstWord = text.substr(0, text.find(" "));
  return firstWord;
}

std::string convert_to_lower(std::string target_str) {
  std::transform(target_str.begin(), target_str.end(), target_str.begin(),
                 ::tolower);
  return target_str;
}

std::string get_current_dir() {
  char* tmp = get_current_dir_name();
  std::string current_dir(tmp);
  free(tmp);
  return current_dir;
}

void exec_command(std::string const& cmd) {
  int status = system(cmd.c_str());
  if (status != 0) {
    std::printf("Failed to execute cmd: \n%s\n! Exit code: %d\n", cmd.c_str(),
                status);
  }
}

#endif  // UTILS_H_
