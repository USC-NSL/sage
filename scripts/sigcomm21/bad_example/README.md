# Demonstration on human involvement for bad message

This short experiment presents when human involvement is required on a [poor/ambigous text](bad_echo.txt) describing the ICMP ECHO protocol header. In this experiment, we intentionally include two ambiguous sentences. One is an identical sentence presenting in current RFC 792, and it results in more than 1 LF, shown in Table 6 in the paper. The other is a made-up sentence intentionally added to the text, and it results in 0 LF before disambiguation check. In this short automated test, we run SAGE on the bad sentences and generate alarm/suggestion messages to users.

# Executing the Experiment

## Execution details
The experiments is scripted, but requires manual interaction in fixing the two ambigous sentences.

Execution of the experiments takes approx. 1.5 minutes.

### Troubleshooting

#### No CCG result after adding 'bad' with 'NP' lexicon

Defining a new entry includes 2 steps:

* adding a word to predicate conversion ruleset (STRING2PREDICATE variable in CCG tool config)

* adding a lexicon entry (RAW_LEXICON variable in CCG tool config)

A possible solution:

```diff
STRING2PREDICATE = {
     [...]
     'x': ['$ArgX'],
     'y': ['$ArgY'],
     'zeroed':['$Zero'],
+    'bad': ['$Bad'],
 }

[...]

RAW_LEXICON = ''':- S,NP,N,PP
         Det :: NP/N
         Adj :: N/N
         arg => NP {None}
+        $Bad => NP {'Bad'}
         #$True => (S\\VP)/PP {None}
         #$False => (S\\VP)/PP {None}
         $And => var\\.,var/.,var {\\x y.'@And'(x,y)}
```

#### Not seeing the second sentence

The script shows the second sentence as:
```
[ICMP Echo] More than 1 LF sentence exists. Please rewrite below sentence(s):
    To form an echo reply message, the source and destination addresses are simply reversed, the type code changed to 0, and the checksum recomputed
```

If by any chance this sentence is not shown, please

* check [SAGE config files](/utils/README.md#configuration-files) (`git diff` can work too),
* reset the SAGE instance using `make purge` in the root folder.

Please be careful to run only a single instance of SAGE at a time.


## How to execute

1. Execute `./run.sh`
2. Check the results:
   * expect to see two ambiguous sentences marked in red on the output with suggestions on human actions.
3. Fix issues
4. Check the results:
   * expect to see successful execution.
