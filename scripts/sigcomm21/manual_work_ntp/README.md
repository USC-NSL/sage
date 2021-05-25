# Manual Work on NTP

This experiment presents the manual work required for supporting new protocoll descriptions. For this purpose, we are taking the [NTP-UDP description text](ntp-udp.txt). In the paper we claim that only a minimal number of new rules (CCG lexicon entries and inconsistency check rules) are required to extend SAGE to a new protocol header description. In this semi-manual test we show how to extend SAGE to cover additional protocol header descriptions.

The experiments work on the [NTP-UDP description text](ntp-udp.txt) on an embedded version SAGE missing the important rules to process the text. During the experiment we extend SAGE with the required rules to process the protocol description.

# Executing the Experiment

## Execution details
The experiments is semi-manual: many steps are automated, but interactions are required.

Execution of the experiments takes approx. 20 minutes.

## How to execute

1. Bootstrap (or reset) the environment: `./run.sh init`
2. Let SAGE parse the text:
   * automatically: use the runner script `./run.sh run`
   * manually: run SAGE by hand as `cd sage; ./sage -i ../ntp-udp.txt -p NTP > ../output.txt`
3. Note that the results differ from the [expected output](expected_output.txt).
   * take a look at the generated SAGE output `output.txt` and observe that many sentences result no logical forms
4. Extend SAGE to support these sentences as well.

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

   * Alternatively, you can use the runner script to add these rules: `./run.sh autoapply`

2. Re-run again and check the results: `./run.sh run`
   * Results are expected to conform the [expected results](expected_output.txt).
