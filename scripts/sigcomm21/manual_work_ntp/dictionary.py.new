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

""" This file holds the CCG dictionary """

STRING2PREDICATE = {
    '"s': ['$Possessive'],
    ',': ['$Separator', '$Punctuate'],
    ',_and': ['$And'],
    '/': ['$Separator'],
    '16-bit': ['$Bit'],
    "16-bit_one's_complement": ['$Ones'],
    "16_bit_one's_complement": ['$Ones'],
    'octet': ['$Octet'],
    'octets': ['$Octet'],
    '<': ['$LessThan'],
    '<=': ['$AtMost'],
    '<O>': ['$ArgY'],
    '<S>': ['$ArgX'],
    '=': ['$Equal'],
    '==': ['$Equals'],
    '>': ['$MoreThan'],
    '>=': ['$AtLeast'],
    'Between': ['$Between'],
    'For': ['$For'],
    'If': ['$If0'],
    'OBJ': ['$ArgY'],
    'OBJ-ORGANIZATION': ['$ArgY'],
    'SUBJ': ['$ArgX'],
    'SUBJ-ORGANIZATION': ['$ArgX'],
    'The': ['$The'],
    'There': ['$There'],
    'Type': ['$Type'],
    'X': ['$ArgX'],
    'Y': ['$ArgY'],
    'a': ['$Any'],
    'active':['$Active'],
    "'address' of the 'source'": ['$SourceAddr'],
    'address': ['$Addr'],
    'adding': ['$Add'],
    'address_of_the_source': ['$SourceAddr'],
    'admist': ['$Between'],
    'after': ['$Right'],
    'agencies': ['$OrganizationNER'],
    'agency': ['$OrganizationNER'],
    'all': ['$All'],
    'all capitalized': ['$Upper'],
    'all caps': ['$Upper'],
    'and': ['$And'],
    'another': ['$AtLeastOne'],
    'any': ['$Any'],
    'apart': ['$Apart'],
    'appear': ['$Is'],
    'appears': ['$Is'],
    'are': ['$Is'],
    'are assumed to': ['$ModalVerb'],
    'are coded': ['$Is'],
    'are identified': ['$Is'],
    "are simply reversed": ['$Reverse'],
    "are 'reversed'": ['$Reverse'],
    "are reversed": ['$Reverse'],
    'arg': ['$Arg'],
    'argument': ['$Arg'],
    'arrived at': ['$Arrive'],
    'as': ['$Is'],
    'as follows': ['$ArgY'],
    'as follows:':['$ArgY'],
    'at least': ['$AtLeast'],
    'at most': ['$AtMost'],
    'at which': ['$When'],
    'away': ['$Apart'],
    'be': ['$Is'],
    'be terminated':['$Stop'],
    'because': ['$Because'],
    'be discarded':['$Discard'],
    'before': ['$Before'],
    'Before': ['$Before'],
    #'before': ['$Left'],
    'behind': ['$Right'],
    'being reported': ['$Reported'],
    'between': ['$Between'],
    'be used to':['$Punctuate'],
    'both': ['$All'],
    'but': ['$And'],
    'by': ['$By'],
    'capital': ['$Capital'],
    'capitalized': ['$Capital'],
    'capitals': ['$Capital'],
    'changed to': ['$ChangeTo'],
    'character': ['$Char'],
    'characters': ['$Char'],
    'cease': ['$Stop'],
    'clear':['$Clear'],
    'code': ['$Code'],
    'come': ['$Is'],
    'comes': ['$Is'],
    'companies': ['$OrganizationNER'],
    'company': ['$OrganizationNER'],
    'compute': ['$Compute'],
    'computing': ['$Compute'],
    'connect': ['$Link'],
    'connects': ['$Link'],
    'contain': ['$Contains'],
    'containing': ['$Contains'],
    'contains': ['$Contains'],
    'correct': ['$True'],
    'count': ['$Count'],
    'copies': ['$Copy'],
    'is copied': ['$Copy'],
    'date': ['$DateNER'],
    'dates': ['$DateNER'],
    'departed':['$Depart'],
    'destination': ['$Dest'],
    'different': ['$NotEquals'],
    'different than': ['$NotEquals'],
    'directly': ['$Direct'],
    'each other': ['$EachOther'],
    'eachother': ['$EachOther'],
    'enclosed': ['$Between'],
    'end with': ['$EndsWith'],
    'ending': ['$Last'],
    'ending with': ['$EndsWith'],
    'ends with': ['$EndsWith'],
    'entities': ['$ArgXListAnd'],
    'equal': ['$Equals'],
    'equals': ['$Equal'],
    'exactly': ['$Equals'],
    'exist': ['$Exists'],
    'exists': ['$Exists'],
    'false': ['$False'],
    'field': ['$Field'],
    'final': ['$Last'],
    'followed by': ['$Left'],
    'following': ['$Right'],
    'follows': ['$Right'],
    'for': ['$For'],
    'form': ['$Form'],
    'from': ['$Of'],
    #'greater than': ['$MoreThan'],
    'greater than or equal': ['$AtLeast'],
    'holds': ['$Is'],
    'identical': ['$Equals'],
    'identifies': ['$Is'],
    'identifying': ['$Identify'],
    'if': ['$If', '$If0'],
    'ignored': ['$Ignore'],
    'immediately': ['$Direct'],
    'in': ['$In'],
    'in between': ['$Between'],
    'in front of': ['$Left'],
    'in the middle of': ['$Between'],
    "in the future": ['$AdvComment'],
    #"in the 'future'": ['$AdvComment'],
    'include': ['$Contains'],
    'includes': ['$Contains'],
    'including': ['$Contains'],
    'incorrect': ['$False'],
    'indicating': ['$Indicate'],
    'institution': ['$OrganizationNER'],
    'institutions': ['$OrganizationNER'],
    'is': ['$Is'],
    'is associated':['$Associate'],
    'is called': ['$Call'],
    'is clear':['$Clear'],
    'is found': ['$Is'],
    'is not found': ['$IsNull'],
    'is greater than': ['$GreaterThan'],
    'is identified': ['$Is'],
    'is ignored': ['$Ignore'],
    #'is in': ['$In'],
    'is inserted at': ['$InsertedAt'],
    'is less than': ['$BeLessThan'],
    'is not':['$LogicNot'],
    'is odd': ['$Odd'],
    'is placed': ['$Is'],
    'is referring to': ['$Contains'],
    'is set':['$Set'],
    'is set to': ['$Is'],
    'is stated': ['$Is'],
    'is transmitted by': ['$TransmitBy'],
    'is being transmitted by': ['$TransmitBy'],
    'is Up':['$Up'],
    'is used': ['$Is'],
    'is used for': ['$SuggestUse'],
    'is used by': ['$UsedBy'],
    'is padded with': ['$PadWith'],
    'is zeroed': ['$Zero'],
    'it': ['$Sentence'],
    'larger than': ['$MoreThan'],
    'last': ['$Last'],
    'left': ['$Left'],
    #"'length' of": ['$Length'],
    'less than': ['$LessThan'],
    'less than or equal': ['$AtMost'],
    'letter': ['$Char'],
    'letters': ['$Char'],
    'link': ['$Link'],
    'links': ['$Link'],
    'location': ['$LocationNER'],
    'locations': ['$LocationNER'],
    'lower': ['$Lower'],
    'lower case': ['$Lower'],
    'lowercase': ['$Lower'],
    'match': ['$Match'],
    'matching': ['$Match'],
    'may': ['$ModalVerb'],
    'mentioned': ['$Contains'],
    'mentions': ['$Contains'],
    'message': ['$Message'],
    'minus': ['$Minus'],
    'more than': ['$MoreThan'],
    'n"t': ['$Not'],
    'neither': ['$None'],
    'next': ['$Within'],
    'no': ['$None', '$Int'],
    'no larger than': ['$AtMost'],
    'no less than': ['$AtLeast'],
    'no more than': ['$AtMost'],
    'no smaller than': ['$AtLeast'],
    'none': ['$None'],
    'nor': ['$Or'],
    'not': ['$Not'],
    'not any': ['$None'],
    'number': ['$Count', '$NumberNER'],
    'numbers': ['$NumberNER'],
    'object': ['$ArgY'],
    'occur': ['$Is'],
    'occurs': ['$Is'],
    'of': ['$Of'],
    'one of': ['$Any'],
    "one's_complement_sum": ['$OnesSum'],
    'or': ['$Or'],
    'organization': ['$OrganizationNER'],
    'organizations': ['$OrganizationNER'],
    'pair': ['$Tuple'],
    'people': ['$PersonNER'],
    'person': ['$PersonNER'],
    'phrase': ['$Word'],
    'phrases': ['$Word'],
    'place': ['$LocationNER'],
    'places': ['$LocationNER'],
    'plus': ['$And'],
    'political': ['$NorpNER'],
    'politician': ['$NorpNER'],
    'preceded by': ['$Right'],
    'precedes': ['$Left'],
    'preceding': ['$Left'],
    'reaches':['$Reach'],
    'recomputed': ['$Recompute'],
    'received': ['$Receive'],
    'receiver': ['$Receiver'],
    'Receiver': ['$Receiver'],
    'referred': ['$Contains'],
    'refers': ['$Contains'],
    'religious': ['$NorpNER'],
    'replies': ['$Reply'],
    'reply': ['$Reply'],
    'reverse': ['$Reverse'],
    'reversed': ['$Reverse'],
    'right': ['$Direct', '$Right'],
    'said': ['$Is'],
    'same': ['$Equals'],
    'same as': ['$Equals'],
    'sandwich': ['$SandWich'],
    'sandwiched': ['$Between'],
    'sandwiches': ['$SandWich'],
    'says': ['$Contains'],
    'select':['$Select'],
    'send':['$Send'],
    'sends':['$Send'],
    'sender': ['$Sender'],
    'Sender': ['$Sender'],
    'sent': ['$Sent'],
    'sentence': ['$Sentence'],
    'sequence_number': ['$SequenceNum'],
    'set':['$Set'],
    'should': ['$ModalVerb'],
    'since': ['$Because'],
    'smaller than': ['$LessThan'],
    'source': ['$Src'],
    'start with': ['$StartsWith'],
    'starting with': ['$StartsWith'],
    'starts with': ['$StartsWith'],
    'states': ['$Contains'],
    'string': ['$Word'],
    'subject': ['$ArgX'],
    'sum': ['$Sum'],
    'term': ['$Word'],
    'terms': ['$Word'],
    'text': ['$Sentence'],
    'the': ['$The'],
    'the number of': ['$Numberof'],
    'them': ['$ArgXListAnd', '$ArgXListAnd'],
    'there': ['$There'],
    'they': ['$ArgXListAnd', '$ArgXListAnd'],
    'to': ['$To'],
    'to aid in': ['$Aid'],
    'to help': ['$Help'],
    'to the left of': ['$Left'],
    'to the right of': ['$Right'],
    'to match': ['$Match'],
    'token': ['$Token', '$Word'],
    'tokens': ['$Word'],
    'true': ['$True'],
    'tuple': ['$Tuple'],
    'type': ['$Type'],
    'Up':['$Up'],
    'update':['$Update'],
    'updates':['$Update'],
    'upper': ['$Upper'],
    'upper case': ['$Upper'],
    'uppercase': ['$Upper'],
    'use': ['$SuggestUse'],
    'uses': ['$SuggestUse'],
    'was detected': ['$Detect'],
    'where': ['$Where'],
    'when': ['$When'],
    'in the case of': ['$InCaseOf'],
    "In the 'case' of": ['$InCaseOf'],
    'in case of': ['$InCaseOf'],
    #'with':['$With'],
    'with which':['$Of'],
    'within': ['$AtMost', '$Within'],
    'word': ['$Word'],
    'words': ['$Word'],
    'wrong': ['$False'],
    'x': ['$ArgX'],
    'y': ['$ArgY'],
    'zeroed':['$Zero'],
}

WORD_NUMBERS = ['zero', 'one', 'two', 'three', 'four', 'five',
                'six', 'seven', 'eight', 'nine', 'ten', 'eleven']
WORD2NUMBER = {elem: str(i) for i, elem in enumerate(WORD_NUMBERS)}

LEXICON_HEAD = ''':- S,NP,N,PP
        VP :: S\\NP
        Det :: NP/N
        Adj :: N/N'''

RAW_LEXICON = ''':- S,NP,N,PP
        VP :: S\\NP
        Det :: NP/N
        Adj :: N/N
        arg => NP {None}
        #$True => (S\\VP)/PP {None}
        #$False => (S\\VP)/PP {None}
        $And => var\\.,var/.,var {\\x y.'@And'(x,y)}
        $Or => var\\.,var/.,var {\\x y.'@Or'(x,y)}
        $Not => (S\\NP)\\(S\\NP) {None}
        $Not => (S\\NP)/(S\\NP) {None}
        $All => NP/N {None}
        $All => NP {None}
        $All => NP/NP {None}
        $Any => NP/N {None}
        $None => N {None}
        #$Is => (S\\NP)/NP {\\y x.'@Is'(x,y)}
        #$Is => (S\\NP)/(S\\NP) {\\y x.'@Is'(x,y)}
        $Is => (S\\NP)/PP {\\y x.'@Is'(x,y)}   # word 'a' occurs between <S> and <O>
        $Is => (S\\NP)\\PP {\\y x.'@Is'(x,y)}  # between <S> and <O> occurs word 'a'
        $Is => (S\\PP)\\NP {\\x y.'@Is'(x,y)}  # between <S> and <O> word 'a' occurs
        $Is => (S\\NP)/NP {\\y x.'@Is'(x, y)}   # Customize rule
        $IsNull => (S\\NP) {\\x. '@Is'(x, 'null')}
        #$Or => var\\.,var/.,var {\\x y. '@XOR'(x,y)}
        $LogicNot => (S\\NP)/NP {\\y x. '@LogicNot'(x,y)}
        $Ignore => S\\NP {\\x. '@Ignore'(x)}
        $Select => (S\\NP)/NP {\\y x. '@Select'(x,y)}
        $Send => (S\\NP)/NP {\\y x. '@Send'(x,y)}
        $Set => (S\\NP) {\\x. '@LogicNot0'(x,'0')}
        $Set => (NP\\NP) {\\x. '@LogicNot0'(x,'0')}
        $Clear => (S\\NP) {\\x. '@Is'(x,'0')}
        $Clear => (NP\\NP){\\x. '@Is'(x,'0')}
        $If0 => (S/S)/S {\\x y. '@Condition'(x,y) }
        $If => (S\\NP)/NP {\\x y. '@Condition'(x,y)}
        $Indicate =>(NP\\NP)/NP {\\y x. '@Indicate'(x,y)}
        $InsertedAt => (S\\NP)/NP {\\y x. '@InsertedAt'(x,y)}
        $Identify => (NP\\NP)/NP {\\y x. '@Identify'(x,y)}
        $BeLessThan => (S\\NP)/NP {\\y x. '@LessThan'(x,y)}
        $Bit => NP {Bit} #customized rule
        $Bit => NP/NP {\\x. '@16Bit'(x)}  #customized rule
        $Octet => NP {Octet}
        $Ones => NP {Ones}  #customized rule
        $OnesSum => NP {OnesSum}
        $InCaseOf => (S/S)/NP {\\x y.'@Condition'(x,y)}
        $For => (S/S)/NP {\\x y.'@AdvBefore'(x,y)}
        $AdvComment => S\S {\\x. '@AdvComment'(x)}
        $Active => NP {'active'}
        $Associate =>(NP\\NP) {\\x.x}
        $Up => NP {'up'}
        $Up => S\\NP {\\x. '@Is'(x, 'up')}
        $Before => (S/S/NP) {\\x y. '@AdvBefore'(x,y)}
        $Before => (S\S)/NP {\\x y. '@AdvBefore'(x,y)}
        $For => (NP\\NP)/NP {\\y x. '@Associate'(x,y)}
        $Of => (NP\\NP)/NP {\\y x. '@Of'(x,y)}
        $TransmitBy => (S\\NP)/NP {\\x y. '@Transmit'(x,y)}
        $To => (S\\S)/NP {\\ y x. '@OperateTo'(x,y)}
        $To => (S\\S)/(S\\NP) {\\x y. '@Purpose'(x,y)}
        $To => (S/S)/(S\\NP) {\\x y. '@Purpose'(x,y)}
        #$To => (S/S)/NP {\\x y. '@Purpose'(x,y)}
        $To => (S/S)/(S\\NP) {\\x y. '@Purpose'(x,y)}
        $To => (S\\NP)/(S\\NP)/(S\\NP) {\\y z x. '@Purpose0'(x,y,z)}
        $In => (NP\\NP)/NP {\\y x. '@In'(x,y)}
        #$In => (S\\S)/NP {\\x y. '@Condition'(x,y)}
        $Any => NP/NP {\\x. x}
        $Aid => (NP\\NP)/NP {\\x. '@Action'('aid',x)}
        $Aid => (S\\S)/NP {\\x y. '@Action'('aid',x,y)}
        $Arrive => (S\\NP)/NP {\\y x. '@Arrive'(x,y)}
        $Match => NP/NP {\\x. '@Action'('match', x)}
        $Form => (S\\NP)/NP {\\x. '@Action'('form', x)}
        #$Form => NP/NP {\\x. '@Action'('form', x)}
        $ChangeTo => (S\\NP)/NP {\\y x. '@ChangeTo'(x, y)}
        $Discard => (S\\NP) {\\x. '@Action'('discard',x)}
        $Reach => (S\\NP)/NP {\\y x. '@Reach'(x,y)}
        $Recompute => (S\\NP) {\\x. '@Action'('recompute',x)}
        $Reverse => (S\\NP){\\x. '@Action'('reverse',x)}
        $Reported => NP\\NP {\\x. '@Compound'('reported',x)}
        $Stop => (S\\NP) {\\x. '@Action'('stop', x)}
        $Stop => (S\\NP)/NP {\\y x. '@Action'('stop',y)}
        $Call => S\\NP {\\x. '@Call'('passive', x)}
        $Compute => NP/N {\\x. '@Action'('compute', x)}
        $Compute => NP/NP {\\x. '@Action'('compute', x)}
        $Compute => (S\\NP)/NP {\\x. '@Action'('compute',x)}
        $Compute => (S\\NP)/NP {\\y x. '@Action0'('compute',x,y)}
        $Copy => (S\\NP)/NP {\\y x. '@Copy'(x,y)}
        $Detect => S\\NP {\\x. x}
        $Depart => (S\\NP)/NP {\\y x. '@Depart'(x,y)}
        $Help => (S\\S)/NP {\\x y. '@Action'('help',x,y)}
        $Equal => (S\\NP)/NP {\\y x.'@Is'(x,y)}
        $GreaterThan =>(S\\NP)/NP {\\y x.'@GreaterThan'(x,y)}
        #$Message => NP\\NP {\\x. '@Compound'(x,'message')}
        $Message => NP {'message'}
        $Type => NP\\NP {\\x. '@Compound'(x,'Type')}
        $SequenceNum => NP {'SequenceNum'}
        $Addr => NP {'Address'}
        $Add => (NP\\NP)/NP {\\y x. '@Add'(x,y)}
        $Src => NP {'Source'}
        $Dest => NP {'Destination'}
        $Code => NP {'Code'}
        $Reply => NP {'Reply'}
        #$Reply => NP\\NP{\\x. '@Reply'(x)}
        $Field => NP\\NP {\\x.x}
        $Field => NP {'Field'}
        $UsedBy => (S\\NP)/NP {\\x y. '@Use'(x,y)}
        $Use => (S\\NP)/NP {\\y x. '@Use'(x,y)}
        $Term => NP {\\x. '@Word'(x)}
        $Term => NP/NP {\\x.x}
        $Term => NP\\NP {\\x.x}
        $Odd => S\\NP {\\x. '@Odd'(x)}
        $PadWith => (S\\NP)/NP {\\y x. '@Pad'(x,y)}
        $Receive => NP {'receive'}
        $Receive => NP/NP {\\x.x}
        $Receiver => NP {Receiver}
        $Sender => NP {Sender}
        $Sent => NP {'send'}
        $SourceAddr => NP{Source_Address}
        $SuggestUse => (S\\NP)/NP {\\y x. '@SuggestUse'(x,y)}
        #$Length => NP {Length}
        $Length => NP/NP {\\x. '@Of'('length', x)}
        #$Length => (NP\\NP)/NP {\\x y. '@Length'(x,y)}
        #$Length => (S\\NP)/NP {\\y x.'@Length'(x,y)}
        $Sum => NP {Sum}
        $Sum => N/N {\\x.x}
        $Sum => (NP\\NP)/NP {\\x y. '@Sum'(x,y)}
        $Sum => (S\\NP)/NP {\\x y.'@Sum'(x,y)}
        $Update => S\\NP {\\x. '@Action'('update',x)}
        $Update => (S\\NP)/NP {\\y x. '@Action'('update',y)}
        $Minus => (S\\NP)/NP {\\x y. '@Minus'(x,y)}
        $StartsWith => S\\S/NP {\\y x.'@StartsWith'(x,y)}
        $ModalVerb => (S\\NP)/(S\\NP) {\\x. x}
        #$ModalVerb => (S\\NP)/(S\\NP) {\\y x. '@Should'(x,y)}
        #$ModalVerb => (S\\NP)/(S\\NP) {\\x y. '@Sum'(x,y)}
        $With => (S\\S)/NP {\\y x. '@With'(x,y)}
        $Where => (NP\\NP)/S {\\x y. '@PositionAt'(x, y)}
        $When => (S\\S)/NP {\\x y. '@When'(x, y)}
        $When => (S\\S)/S {\\x y. '@When'(x, y)}
        $Zero => S\\NP {\\x. '@Zeros'(x)}
        $Exists => S\\NP/PP {\\y x.'@Is'(x,y)}
        #$Exists => S\\NP {None}
        $Int => Adj {None} #There are no words between <S> and <O>
        $AtLeastOne => NP/N {None}
        #$Equals => (S\\NP)/NP {None}
        #$NotEquals => (S\\NP)/NP {None}
        $LessThan => PP/PP/N {\\x y.'@LessThan'(y,x)} #There are less than 3 words between <S> and <O>
        $AtMost => PP/PP/N {\\x y.'@AtMost'(y,x)} #There are at most 3 words between <S> and <O>
        $AtLeast => PP/PP/N {\\x y.'@AtLeast'(y,x)} #same as above
        $MoreThan => PP/PP/N {\\x y.'@MoreThan'(y,x)} #same as above
        #$LessThan => PP/N {\\x.'@LessThan1'(y,x)} #number of words between X and Y is less than 7.
        $AtMost => PP/N {\\x.'@AtMost1'(y,x)}
        $AtLeast => PP/N {\\x.'@AtLeast1'(y,x)}   #same as above
        $MoreThan => PP/N {\\x.'@MoreThan1'(y,x)} #same as above
        #$In => S\\NP/NP {None} # There are 2 words in the sentence  ， reverse version?
        $In => PP/NP {\\x.'@In0'(x)}
        $Contains => S\\NP/NP {None} #The sentence contains two words
        $Separator => var\\.,var/.,var {\\x y.'@And'(x,y)} #connection between two words
        #$Processive => NP/N\\N {None}
        #$Count => N {None}
        #$Tuple => N {None}
        #$ArgXListAnd => NP {None}
        $EachOther => N {None}
        $Token => N {\\x.'@Word'(x)}
        $Word => NP/N {\\x.'@Word'(x)}
        $Word => NP/NP {\\x.'@Word'(x)}
        $Word => N {'tokens'} #There are no more than 3 words between <S> and <O>
        $Word => NP {'tokens'} #There are no more than 3 words between <S> and <O>
        $Char => N {None} #same as above
        #$Lower => Adj {None}
        #$Capital => Adj {None}
        $StartsWith => S\\NP/NP {\\y x.'@StartsWith'(x,y)}
        $EndsWith => S\\NP/NP {\\y x.'@EndsWith'(x,y)}
        $Left => PP/NP {\\x.'@Left0'(x)} # the word 'a' is before <S>
        $Left => (S\\NP)/NP {\\y x.'@Left'(y,x)}  #Precedes
        $Right => PP/NP {\\x.'@Right0'(x)}# the word 'a' ia after <S>
        $Right => (S\\NP)/NP {\\y x.'@Right'(y,x)}
        #$Within => ((S\\NP)\\(S\\NP))/NP {None} # the word 'a' is within 2 words after <S>
        #$Within => (NP\\NP)/NP {None}
        $Within => PP/PP/N {\\x y.'@AtMost'(y,x)} #Does Within has other meaning.
        $Sentence => NP {'Sentence'}
        $Between => (S/S)/NP {\\x y.'@Between'(x,y)}
        $Between => S/NP {\\x.'@Between'(x)}
        $Between => PP/NP {\\x.'@Between'(x)}
        $Between => (NP\\NP)/NP {\\x y.'@Between'(x,y)}

        $PersonNER => NP {'@PER'}
        $LocationNER => NP {'@LOC'}
        $DateNER => NP {'@Date'}
        $NumberNER => NP {'@Num'}
        $OrganizationNER => NP {'@Org'}
        $NorpNER => NP {'@Norp'}
        $ArgX => NP {'ArgX'}
        $ArgY => NP {'ArgY'}
        #$will => S\\NP/VP {None}
        #$might => S\\NP/VP {None}
        $that => NP/N {None}
        #$that => (N\\N)/(S/NP) {None} #same as which
        $Apart => (S/PP)\\NP {None}
        $Direct => PP/PP {\\x.'@Direct'(x)} # the word 'a' is right before <S>
        $Direct => (S\\NP)/PP {\\y x.'@Is'(x,'@Direct'(y))}
        $Last => Adj {None}
        $There => NP {'There'}
        $By => S\\NP\\PP/NP {\\z f x.'@By'(x,f,z)} #precedes sth by 10 chatacters
        $By => (S\\NP)\\PP/(PP/PP) {\\F x y.'@Is'(y,F(x))} #precedes sth by no more than10 chatacters
        $By => PP\\PP/(PP/PP) {\\F x. F(x)} #occurs before by no...
        $Numberof => NP/PP/NP {\\x F.'@NumberOf'(x,F)}
        #$Of => PP/NP {\\x.'@Range0'(x)} # the word 'x' is at most 3 words of Y
        #$Of => NP/NP {\\x.x} #these two are designed to solve problems like $Is $Left $Of and $Is $Left
        #$Of => N/N {\\x.x}
        $Char => NP/N {None}
        $ArgX => N {'ArgX'}
        $ArgY => N {'ArgY'}
        $Link => (S\\NP)/NP {\\x y.'@Is'(y,'@between'(x))}
        $SandWich => (S\\NP)/NP {\\x y.'@Is'(x,'@between'(y))}
        $The => N/N {\\x.x}
        $The =>NP/NP {\\x.x}
        $Punctuate => S/S {\\x. x}
        $Punctuate => S\\S {\\x. x}
        '''
