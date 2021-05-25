# Copyright (c) 2021, The University of Southern California.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Logic forms having denylisted terms are skipped in code generation
DENYLIST = [
    "'future'",
    "'concern'",
    "Octet",
]

# Role Conversion Table: get role from logic form chunks
ROLE_KEYWORDS = {
    'echo_message': 'sender',
    'echo_reply_message': 'receiver',
    'timestamp_message': 'sender',
    'timestamp_reply_message': 'receiver',
    'information_reply_message': 'receiver',
    'destination_unreachable_message': 'receiver',
    'time_exceed_message': 'receiver',
    'parameter_problem_message': 'receiver',
    'source_quench_message': 'receiver',
    'redirect_message': 'receiver',
    'host_membership_query_message': 'query',
    'host_membership_report_message': 'report',
}

# Message Abbrevation Table: short form of message types to use in function declaration
MSG_ABBREVS = {
    'Destination Unreachable Message': 'dest_unreachable',
    'Echo or Echo Reply Message': 'echo',
    'Information Request or Information Reply Message': 'info',
    'Parameter Problem Message': 'para_prob',
    'Redirect Message': 'redir',
    'Time Exceeded Message': 'time_exceed',
    'Timestamp or Timestamp Reply Message': 'timestamp',
    'INTERNET GROUP MANAGEMENT PROTOCOL': 'igmp',
    'UDP Header Format': 'udp',
}

# LF Conversion Table: replace parts oflogic forms in preprocessing
LF_CONVERSIONS = {
    "'@Is'('@In'(Source_Address,'echo_message'),'@Of'('Destination','echo_reply_message'))":
    "",
    "'@Is'('length','@Add'('@Of'('length','@Of'('ntp_message','udp_header')),'length'))":
    "'@Is'('length','@Add'('@Of'('length','ntp_message'),'@Of'('length','udp_header')))",
    "'@Is'('@In'(Source_Address,'timestamp_message'),'@Of'('Destination','timestamp_reply_message'))":
    "",
    "'@Is'('@In'(Source_Address,'information_request_message'),'@Of'('Destination','information_reply_message'))":
    "",
    "'@Is'('destination_address','@Of'('source_address','original_datagram's_data'))":
    "",
    "'@SuggestUse'('gateway_internet_address','future_traffic')":
    "",
    "'@Action'('recompute','checksum')":
    "",
    "'@ChangeTo'('type_code','0')":
    "",
    "'@ChangeTo'('type_field','0')":
    "",
    "'@ChangeTo'('type_code','14')":
    "",
    "'@ChangeTo'('type_code','16')":
    "",
    "'@Of'('@And'('first_64_bits','internet_header'),'original_datagram's_data')":
    "",
    "'@And'('@Of'('first_64_bits','original_datagram's_data'),'internet_header')":
    "",
    "'@OperateTo'('@Action'('help','@Action'('match','message'),'@Use'('host','this_data')),'process')":
    "",
    "'@Condition'('@SuggestUse'('higher_level_protocol','port_numbers'),'@Is'('port_numbers','@In0'('@Of'('first_64_data_bits','original_datagram's_data'))))":
    "",
    "'@Condition'('@Is'('identifier','0'),'@Is'('Code','0'))":
    "'@Condition'('@Is'('Code','0'),'@Is'('identifier','0'))",
    "'@Condition'('@Is'('SequenceNum','0'),'@Is'('Code','0'))":
    "'@Condition'('@Is'('Code','0'),'@Is'('SequenceNum','0'))",
    "'@Condition'('@Is'('port_numbers','@In0'('@Of'('first_64_data_bits','original_datagram's_data'))),'@SuggestUse'('higher_level_protocol','port_numbers'))":
    "",
    "'@Condition'('@Is'('Code','0'),'@Is'('pointer','@PositionAt'('error','octet')))":
    "",
    "'@Purpose'('@Action'('form','echo_reply_message'),'@Action'('reverse','@And'('destination_addresses','Source')))":
    "",
    "'@Purpose'('@Action'('form','timestamp_reply_message'),'@Action'('reverse','@And'('destination_addresses','Source')))":
    "",
    "'@Purpose'('@Action'('form','information_reply_message'),'@Action'('reverse','@And'('destination_addresses','Source')))":
    "",
    "'@Purpose'('@Action'('form','echo_reply_message'),'@Action'('reverse','source_and_destination_addresses'))":
    "",
    "'@Purpose'('@Action'('form','timestamp_reply_message'),'@Action'('reverse','source_and_destination_addresses'))":
    "",
    "'@Purpose'('@Action'('form','information_reply_message'),'@Action'('reverse','source_and_destination_addresses'))":
    "",
    "'@StartsWith'('@Is'('checksum','@Of'(Ones,'@Of'(OnesSum,'icmp_message'))),'icmp_type')":
    "'@StartsWith'('@Is'('checksum','@Of'('@Of'(Ones,OnesSum),'icmp_message')),'icmp_type')",
    "'@Is'('checksum','@Of'('@Of'(Ones,OnesSum),'igmp_message'))":
    "'@Is'('checksum','@Of'(Ones,'@Of'(OnesSum,'igmp_message')))",
    "'@Compound'('reported','group')":
    "'reported_group'",
    "'@Is'('ntp_service_port_number','123')":
    "",
    "'@When'('@Reach'('peer_timer','value'),'@Condition'('@Of'('@And'('symmetric_mode','client_mode'),'timer_threshold_variable'),'@Call'('passive','timeout_procedure')))":
    "'@When'('@Reach'('peer_timer','@Of'('value','timer_threshold_variable')),'@Condition'('@And'('symmetric_mode','client_mode'),'@Call'('passive','timeout_procedure')))",
    "'@Condition'(@Action('discard','packet'),'@And'('@LogicNot'('bfd[dot]authtype','0'),'@Is'('bit','0')))":
    "'@Condition'('@And'('@LogicNot'('bfd[dot]authtype','0'),'@Is'('bit','0')),@Action('discard','packet'))",
}

# Term Conversion Table: replace terms in preprocessing
TERM_CONVERSIONS = {
    "'Destination'": "Destination_Address",
    "'destination_addresses'": "Destination_Address",
    "'echos'": "'Echo_or_Echo_Reply_Message_hdr'",
    "'echo_message'": "'Echo_or_Echo_Reply_Message_hdr'",
    "'echo_reply_message'": "'Echo_or_Echo_Reply_Message_hdr'",
    "'timestamps'": "'Timestamp_or_Timestamp_Reply_Message_hdr'",
    "'timestamp_message'": "'Timestamp_or_Timestamp_Reply_Message_hdr'",
    "'timestamp_reply_message'": "'Timestamp_or_Timestamp_Reply_Message_hdr'",
    "'information_request_message'": "'Information_Request_or_Information_Reply_Message_hdr'",
    "'information_reply_message'": "'Information_Request_or_Information_Reply_Message_hdr'",
    "'destination_unreachable_message'": "'Destination_Unreachable_Message_hdr'",
    "'time_exceed_message'": "Time_Exceeded_Message_hdr",
    "'parameter_problem_message'": "'Parameter_Problem_Message_hdr'",
    "'source_quench_message'": "'Source_Quench_Message_hdr'",
    "'redirect_message'": "Redirect_Message_hdr",
    "'icmp_message'": "{ENV_message}_hdr",
    "'icmp_type'": "{ENV_message}_hdr.type",
    "'type_code'": "{ENV_message}_hdr.type",
    "'total_length'": "Length",
    "'group_address_field'": "{ENV_message}_hdr.group_address",
    "'data'": "{ENV_message}_hdr.data",
    "'Code'": "{ENV_message}_hdr.code",
    "'Sequence Number'": "{ENV_message}_hdr.sequence_number",
    "'SequenceNum'": "{ENV_message}_hdr.sequence_number",
    "'gateway_internet_address'": "{ENV_message}_hdr.gateway_internet_address",
    "'checksum_field'": "{ENV_message}_hdr.checksum",
    "'identifier'": "{ENV_message}_hdr.identifier",
    "{ENV_message}_hdr": "{ENV_message}_hdr",
}

# Code Conversion Table: replace code snippets in postprocessing
CODE_CONVERSIONS = {
    "'{ENV_message}_hdr'.Addresses": "ip_hdr->ip_src",
    "'{ENV_message}_hdr'.Destination_Address": "ip_hdr->ip_dst",
    "'{ENV_message}_hdr'.Source_Address": "ip_hdr->ip_src",
    "Code": "code",
    "Type": "type",
    "Checksum": "checksum",
    "Length": "length",
    "hdr.": "hdr->",
    "hdr->hdr": "hdr",
    "Echo_or_Echo_Reply_Message_hdr": "hdr",
    "Timestamp_or_Timestamp_Reply_Message_hdr": "hdr",
    "Information_Request_or_Information_Reply_Message_hdr": "hdr",
    "Destination_Unreachable_Message_hdr": "hdr",
    "Time_Exceeded_Message_hdr": "hdr",
    "Parameter_Problem_Message_hdr": "hdr",
    "Source_Quench_Message_hdr": "hdr",
    "Redirect_Message_hdr": "hdr",
    "INTERNET_GROUP_MANAGEMENT_PROTOCOL_hdr": "hdr",
    "UDP_Header_Format_hdr": "hdr",
    "igmp_message": "hdr",
    "sizeof(hdr->data)": "sizeof(*data)",
    "hdr->data": "&data",
    "'original_datagram\'s_data'.'Address'; 'source_network'":
    "copy(&payload, (char *) ptrs->ip_ptr, 28);",
    "'original_datagram\'s'.'internet_destination_address'.'address_of_the_gateway'":
    "find_gateway(ptrs->ip_ptr)",
    "original_datagram's_data": "ptrs->ip_ptr",
    "internet_header_+_64_bits_of_data_datagram": "payload",
    "internet_header_w_64_bits_of_original_data_datagram": "payload",
    "original_datagrams_internet_destination_address": "((ip_hdr_t*)(ptrs->ip_ptr))->ip_dst",
    "original_datagram's_internet_destination_address": "ptrs->ip_ptr",
    "reported_group": "ptrs->ip_ptr",
    "compute_checksum()":
    "hdr->checksum = u16bit_ones_complement(ones_complement_sum((const void *) hdr, length))",
    "compute_checksum(hdr->type)":
    "hdr->checksum = u16bit_ones_complement(ones_complement_sum((const void *) &hdr->type, length))",
    "ntp_service_port_number": "123",
    "udp_header": "struct UDP_Header_Format_hdr",
    "ntp_message": "struct NTP_Data_Format_hdr",
    "pkt.leap": "hdr->li",
    "pkt.version": "hdr->vn",
    "pkt.stratum": "hdr->stratum",
    "pkt.poll": "hdr->poll",
    "pkt.precision": "hdr->precision",
    "pkt.distance": "hdr->synchronizing_distance",
    "pkt.drift": "hdr->estimated_drift_rate",
    "pkt.refid": "hdr->reference_clock_identifier",
    "pkt.reftime": "hdr->reference_timestamp_64_bits",
    "pkt.org": "hdr->originate_timestamp_64_bits",
    "pkt.rec": "hdr->receive_timestamp_64_bits",
    "pkt.xmt": "hdr->transmit_timestamp_64_bits",
    "this_bfd_packet.session":"session",
    ">= =": ">=",
    "'timer_threshold_variable'.'value'": "peer.threshold",
    "peer_timer": "peer.timer",
    "'": "",
    ";;": ";",
    ";}": ";\n}",
    "\n;\n": "",
}

# Set message field ranks: the values are field name, index
# pairs. Index 0 means to process field first, -1 means to process it
# last. If there are multiple values with the same index, the order of
# definition breaks the tie. For example setting (('A',0), ('B',0),...)
# indicates the order of A,B,...
RANK_FIELDS = {
    "Echo or Echo Reply Message": [('checksum', -1)],
    "Timestamp or Timestamp Reply Message": [('checksum', -1)],
    "Information Request or Information Reply Message": [('checksum', -1)],
    "Destination Unreachable Message": [('checksum', -1)],
    "Time Exceeded Message": [('checksum', -1)],
    "Parameter Problem Message": [('checksum', -1)],
    "Source Quench Message": [('checksum', -1)],
    "Redirect Message": [('checksum', -1)],
    "INTERNET GROUP MANAGEMENT PROTOCOL": [('checksum', -1)],
    "UDP Header Format": [('checksum', -1)],
    "NTP Data Format": [],
}
