#!/bin/bash

# Script to run ITGSend tests for different protocols, packet sizes, and IP addresses
# Ensure ITGSend is installed and available in the PATH
# Ensure the LOGFILE directory exists
# This script runs ITGSend tests for both IPv4 and IPv6 addresses with different protocols and packet sizes.
# Usage: chmod +x testscript.sh && ./testscript.sh
# This script runs the test for 10 runs for each combination of protocol, packet size, and IP address.

PACKET_SIZE=( 128 256 384 512 640 768 896 1024 1152 1280 1408 1536)
PROTOCOLS=( "TCP" "UDP" )
IPV4ADDRESS=( "192.168.1.14" )
IPV6ADDRESS=("FD00:ABCD:3::2")
LOGFILE="/home/client-2/Desktop/LOGS/"

for PROTOCOL in "${PROTOCOLS[@]}"; do
    for SIZE in "${PACKET_SIZE[@]}"; do
        for IPV4 in "${IPV4ADDRESS[@]}"; do
            echo "Running test with $PROTOCOL, packet size $SIZE, IPv4 address $IPV4"
            for run in {1..10}; do
                echo "Run Number: $run"
                ITGSend -a $IPV4 -T $PROTOCOL -c $SIZE -t 10000 -C 16498 -x $LOGFILE/IPV4/$PROTOCOL/$SIZE/run-$run.log
                sleep 3
            done
        done

        sleep 5
        for IPV6 in "${IPV6ADDRESS[@]}"; do
            echo "Running test with $PROTOCOL, packet size $SIZE, IPv6 address $IPV6"
            for run in {1..10}; do
                echo "Run Number: $run"
                ITGSend -a $IPV6 -T $PROTOCOL -c $SIZE -t 10000 -C 16498 -x $LOGFILE/IPV6/$PROTOCOL/$SIZE/run-$run.log
                sleep 3
            done
        done
        echo "Running test with $PROTOCOL, packet size $SIZE, both IPv4 and IPv6"
    done
done
