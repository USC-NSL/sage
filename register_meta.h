#ifndef REGISTER_META_H_
#define REGISTER_META_H_

#include <sqlite3.h>

#include <regex>
#include <set>
#include <sstream>
#include <string>
#include <vector>

#include "./headerImpl.h"
#include "./paragraph.h"
#include "./utils.h"

void register_meta_fields(std::string protocol, std::string message_name,
                          std::vector<pkt_field> fields) {
  if (fields.empty()) {
    return;
  }
  for (const auto &field : fields) {
    const std::string command =
        "cd utils/metadata_system; python3 run_sqlite.py -c -m \"" +
        message_name + "\" -p \"" + protocol + "\" -n \"" +
        convert_to_lower(field.field_name) + "\" -b " +
        std::to_string(field.field_bit);
    exec_command(command);
  }
}

void register_meta_sentence(std::string protocol, std::string topic,
                            std::string field_name, std::string sentence,
                            int sentence_id) {
  std::string sent(sentence);
  sent.erase(0, sent.find_first_not_of(' '));
  std::string command =
      "cd utils/metadata_system; python3 run_sqlite.py -p \"" + protocol +
      "\" -m \"" + topic + "\" -n \"" + field_name + "\" -s \"" + sent +
      "\" -i " + std::to_string(sentence_id);
  exec_command(command);
}

void update_meta(std::string message_type,
                 std::vector<Paragraph> field_descriptions) {
  for (auto &field_desc : field_descriptions) {
    const std::string command =
        "cd utils/metadata_system; python3 run_sqlite.py -ud -desc \"" +
        field_desc.get_content() + "\" -m \"" + message_type + "\" -n \"" +
        field_desc.get_topic() + "\"";
    exec_command(command);
  }
}

void update_mapping_label(std::string msg_type, std::string field,
                          std::string sentence, std::string sentence_id,
                          std::string label) {
  const std::string command =
      "cd utils/metadata_system; python3 run_sqlite.py -ul -m \"" + msg_type +
      "\" -n \"" + field + "\" -s \"" + sentence + "\" -i " + sentence_id +
      " -l \"" + label + "\";";
  exec_command(command);
}

void register_mapping_lf(std::string msg_type, std::string field,
                         std::string sentence, std::string sentence_id,
                         std::string lf, std::string env) {
  const std::string command =
      "cd utils/metadata_system; python3 run_sqlite.py -ulf -m \"" + msg_type +
      "\" -n \"" + field + "\" -s \"" + sentence + "\" -i " + sentence_id +
      " -lf \"" + lf + "\" -env \'" + env + "\';";
  exec_command(command);
}

void clean_invalid_sentence_entry(std::string msg_type, std::string sentence,
                                  std::string sentence_id) {
  const std::string command =
      "cd utils/metadata_system; python3 run_sqlite.py -ci -m \"" + msg_type +
      "\" -s \"" + sentence + "\" -i " + sentence_id + ";";
  exec_command(command);
}

void clean_mds() {
  const std::string command =
      "cd utils/metadata_system; python3 run_sqlite.py -r ;";
  exec_command(command);
}

std::set<std::string> get_msg_types(std::string protocol) {
  sqlite3 *db;
  sqlite3_stmt *stmt;
  std::set<std::string> msg_types;

  if (sqlite3_open("utils/metadata_system/message.db", &db) != SQLITE_OK) {
    std::cout << "Failed to open db: " << sqlite3_errmsg(db) << std::endl;
    return {};
  }
  int rc = sqlite3_prepare_v2(
      db, "SELECT msg_type from meta WHERE protocol = ?;", -1, &stmt, NULL);
  sqlite3_bind_text(stmt, 1, protocol.c_str(), protocol.length(),
                    SQLITE_TRANSIENT);
  if (rc != SQLITE_OK) {
    std::cout << "error: " << sqlite3_errmsg(db) << std::endl;
    return {};
  }
  while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
    msg_types.insert(std::string((char *) sqlite3_column_text(stmt, 0)));
  }
  if (rc != SQLITE_DONE) {
    std::cout << "error: " << sqlite3_errmsg(db) << std::endl;
  }

  sqlite3_finalize(stmt);
  sqlite3_close(db);

  return msg_types;
}

std::set<std::string> get_roles_of_msg(std::string msg_type) {
  sqlite3 *db;
  sqlite3_stmt *stmt;
  std::set<std::string> roles;

  if (sqlite3_open("utils/metadata_system/sent_to_lf.db", &db) != SQLITE_OK) {
    std::cout << "Failed to open db: " << sqlite3_errmsg(db) << std::endl;
    return {};
  }
  int rc = sqlite3_prepare_v2(db, "SELECT env from mapping WHERE msg_type = ?;",
                              -1, &stmt, NULL);
  sqlite3_bind_text(stmt, 1, msg_type.c_str(), msg_type.length(),
                    SQLITE_TRANSIENT);
  if (rc != SQLITE_OK) {
    std::cout << "error: " << sqlite3_errmsg(db) << std::endl;
    return {};
  }
  while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
    std::string env_str = std::string((char *) sqlite3_column_text(stmt, 0));
    std::regex role_regex("\"role\": \"([,\\w]*)\"");
    std::cmatch re_match;
    std::regex_search(env_str.c_str(), re_match, role_regex);
    std::string roles_env = re_match[1];
    if (!roles_env.empty()) {
      std::stringstream ss(roles_env);
      std::string role;
      while (std::getline(ss, role, ',')) {
        roles.insert(role);
      }
    }
  }
  if (rc != SQLITE_DONE) {
    std::cout << "error: " << sqlite3_errmsg(db) << std::endl;
  }

  sqlite3_finalize(stmt);
  sqlite3_close(db);

  return roles;
}

#endif  // REGISTER_META_H_
