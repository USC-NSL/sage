# SAGE Tests

## Available Tests

| Name      | Test Dir  | Checks<br />LF | Checks<br />Header | Checks<br />Code | Execution Time |
|:----------|:----------|:--------------:|:------------------:|:----------------:|---------------:|
| ICMP Echo | echo      | x              | x                  | x                |    3 min       |
| ICMP      | icmp      | x              | x                  | x                |   19 min       |
| IGMP      | igmp      | x              | x                  |                  |    2 min       |
| NTP       | ntp       | x              | x                  | x                |    6 min       |
| NTP UDP   | ntp-udp   | x              | x                  |                  |    3 min       |
| BFD       | bfd       | x              | x                  |                  |    6 min       |

## Executing a Test

Navigate to a test folder and execute `run.sh`.
Tests print either `OK` or `FAIL` depending on the test result.

Example:
```sh
cd echo
./run.sh
```

## Adding New Tests

Testing options are very simple. Each test case is built around a single `run.sh` execution script with expected results (e.g., expected_output.txt or expected_code.txt). Currently there is no framework for the comparing output to expected results. Do not forget to print either OK or FAIL depending on the test result.

Test scripts have 4 main parts. These, with examples taken from [echo](echo), are the following:

1. Common variables
``` sh
NAME="ICMP Echo"
INPUT=echo.txt
PROTOCOL_NAME=ICMP

CUR_DIR=`realpath $(dirname $BASH_SOURCE)`
SAGE_DIR="${CUR_DIR}/../../../"
SAGE_BIN=parseicmp
```

2. SAGE and test case reset
```sh
echo "[$NAME] Resetting.."
rm -f ${CUR_DIR}/output.txt
rm -f ${CUR_DIR}/icmp_*.h
pushd $SAGE_DIR
make clean build > /dev/null || make clean build
popd
```

3. Run SAGE
```sh
echo "[$NAME] Executing.."
pushd ${SAGE_DIR}
cmd="./${SAGE_BIN} -i ${INPUT} -p ${PROTOCOL_NAME} > ${CUR_DIR}/output.txt"
eval $cmd
mv icmp_hdr.h ${CUR_DIR}/icmp_hdr.h
mv icmp_gen.h ${CUR_DIR}/icmp_gen.h
popd
rm -f ${CUR_DIR}/nul
```

4. Analyze results
```sh
# 1. check logical forms
echo "[$NAME] Checking results.."
results=`diff -q <(grep "LF check summary:" ${CUR_DIR}/output.txt) ${CUR_DIR}/expected_output.txt`
if [ "$results" ]; then
    echo "[$NAME] Check: LFs Diff Output:"
    diff <(grep "LF check summary:" ${CUR_DIR}/output.txt) ${CUR_DIR}/expected_output.txt
    echo "[$NAME] FAIL"
    exit 1
fi
echo "[$NAME] Check: Logical Forms OK"
# 2. check generated header
results=`diff -q ${CUR_DIR}/icmp_hdr.h ${CUR_DIR}/expected_header.txt`
if [ "$results" ]; then
    echo "[$NAME] Check: Header Diff Output:"
    diff ${CUR_DIR}/icmp_hdr.h ${CUR_DIR}/expected_header.txt
    echo "[$NAME] FAIL"
    exit 1
fi
echo "[$NAME] Check: Headers OK"
# 3. check generated code
results=`diff -q ${CUR_DIR}/icmp_gen.h ${CUR_DIR}/expected_code.txt`
if [ "$results" ]; then
    echo "[$NAME] Check: Code Diff Output:"
    diff ${CUR_DIR}/icmp_gen.h ${CUR_DIR}/expected_code.txt
    echo "[$NAME] FAIL"
    exit 1
fi
echo "[$NAME] Check: Code OK"

echo "[$NAME] OK"
exit 0
```
