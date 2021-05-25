# Add support for additional protocols
To extend SAGE for additional protocols, we make incremental changes to the existing configurations. As stated in our paper, extending elements to other protocols will require marginal extensions at each step. We first introduce the components in SAGE, and then list out the four configuration files that these tools are dependent on. To add support for additional protocols, you may edit these configuration files.

## Modular tools/components

**Phraser** is a tool to label noun phrases identified in a sentence. This tool relies on both SpaCy and domain-specific dictionary. Users may decide to add more domain-specific terms when needed.

**CCG Tool** is a tool to turn a labelled sentence into logical form(s). Users may need to add lexicon(s) if a word inside a sentence is not yet defined with its lexicon.

**Logical Form Checker** is a tool used to disambiguate LFs. When new predicates are used in the input LF, corresponding disambiguation rules are required to be added/extended.

**Code Generator** is a tool to generate code from the unique LF. If new predicates are introduced, corresponding predicate function handlers shall be added. In addition, to adapt to the static framework, SAGE might have to postprocess some variable naming to match with the universe naming in static framework. 

## Configuration files

**Phraser** relies on domain-specific terms defined in [phraser/data/EN/custom.txt](phraser/data/EN/custom.txt). Currently, SAGE directly imports the terms from index pages in a textbook.

**CCG Tool** uses lexicons which are stored in [ccg_tool/dictionary.py](ccg_tool/dictionary.py).

**Logical Form Checker** uses disambiguation checks defined in [logic_form_checker/check_predicates.py](logic_form_checker/check_predicates.py).

**Code Generator** uses predicate function handlers that are stored in [code_generator/ops.py](code_generator/ops.py). The postprocessing naming mapping is stored in [code_generator/settings.py](code_generator/settings.py).

## Example of incremental changes in configuration files
Here, we use the same NTP-UDP example as we provide in [sage/scripts/sigcomm21/manual_work_ntp](../scripts/sigcomm21/manual_work_ntp). Below shows a summary of manual effort required to edit corresponding configuration files

   * CCG lexicon entries to add:
   ```diff
   STRING2PREDICATE = {
   [...]
   +     'octet': ['$Octet'],
   +     'octets': ['$Octet'],
   +     'adding': ['$Add'],
   +     'is called': ['$Call'],
   +     'reaches':['$Reach'],
   ```
   and
   ```diff
   RAW_LEXICON = ''':- S,NP,N,PP
             [...]
   +         $Octet => NP {Octet}
   +         $Reach => (S\\NP)/NP {\\y x. '@Reach'(x,y)}
   +         $Call => S\\NP {\\x. '@Call'('passive', x)}
   +         $Add => (NP\\NP)/NP {\\y x. '@Add'(x,y)}
   ```
   * Predicate rules to add to `sage/utils/logic_form_checker/check_predicates.py`:
   ```diff
   predicate_rules = {
         [...]
   +     '@Add':[
   +         ('const_str', 'const_str'),
   +     ],
   +     '@Reach':[
   +         ('const_str', 'const_str'),
   +         ('const_str', 'variable'),
   +         ('const_str', 'variable'),
   +         ('variable', 'variable'),
   +     ],
   +     '@Call':[
   +         ('const_str', 'const_str'),
   +         ('const_str', 'variable'),
   +     ],
   ```
   * Predicate order rule to add to `sage/utils/logic_form_checker/check_predicates.py`:
   ```diff
   predicate_order_denylist = {
         [...]
   +     '@Add':[
   +         '@Of',
   +     ],
   ```


