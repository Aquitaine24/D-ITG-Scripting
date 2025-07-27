#!/bin/bash

# Script to run ITGSend tests for different protocols, packet sizes, and IP addresses
# Ensure ITGSend is installed and available in the PATH
# Ensure the LOGROOT directory exists
# This script runs ITGSend tests for both IPv4 and IPv6 addresses with different protocols and packet sizes.
# Usage: chmod +x testscript.sh && ./testscript.sh
# This script runs the test for 10 runs simultaneously for each combination of protocol, packet size, and IP address.

PACKET_SIZE=(128 256 384 512 640 768 896 1024 1152 1280 1408 1536)
PROTOCOLS=("TCP" "UDP")
IPV4ADDRESS=("192.168.1.14")
IPV6ADDRESS=("FD00:ABCD:3::2")
BASE_PORT=10000
PORT=$BASE_PORT
LOGROOT="/home/client-2/Desktop/LOGS/"

# Map packet size to -C value
declare -A C_VALUES=(
    [128]=20300
    [256]=20200
    [384]=20000
    [512]=20000
    [640]=20000
    [768]=19900
    [896]=19600
    [1024]=19500
    [1252]=19300
    [1280]=19200
    [1408]=19200
    [1536]=16200
)

echo "Running ITGSend tests separately for IPv4 and IPv6..."

# ==============================
# IPv4 Tests
# ==============================
for PROTOCOL in "${PROTOCOLS[@]}"; do
    for SIZE in "${PACKET_SIZE[@]}"; do
        SCRIPT_FILE="/tmp/itg_ipv4_${PROTOCOL}_${SIZE}"
        RECV_LOG="$LOGROOT/IPV4/${PROTOCOL}/${SIZE}/recv.log"
        rm -f "$SCRIPT_FILE"

        CVAL=${C_VALUES[$SIZE]}

        for IPV4 in "${IPV4ADDRESS[@]}"; do
            for run in {1..10}; do
                echo "-a $IPV4 -rp $PORT -T $PROTOCOL -c $SIZE -t 10000 -C $CVAL" >> "$SCRIPT_FILE"
                ((PORT++))
            done
        done

        echo "Running IPv4 ITGSend for $PROTOCOL $SIZE..."
        ITGSend "$SCRIPT_FILE" -x "$RECV_LOG"

        echo "Completed IPv4 test for $PROTOCOL $SIZE"
        sleep 2
        PORT=$BASE_PORT  # Reset PORT for the next protocol/size combination
    done
done

# ==============================
# IPv6 Tests
# ==============================
for PROTOCOL in "${PROTOCOLS[@]}"; do
    for SIZE in "${PACKET_SIZE[@]}"; do
        SCRIPT_FILE="/tmp/itg_ipv6_${PROTOCOL}_${SIZE}"
        RECV_LOG="$LOGROOT/IPV6/${PROTOCOL}/${SIZE}/recv.log"
        rm -f "$SCRIPT_FILE"

        CVAL=${C_VALUES[$SIZE]}

        for IPV6 in "${IPV6ADDRESS[@]}"; do
            for run in {1..10}; do
                echo "-a $IPV6 -rp $PORT -T $PROTOCOL -c $SIZE -t 10000 -C $CVAL" >> "$SCRIPT_FILE"
                ((PORT++))
            done
        done

        echo "Running IPv6 ITGSend for $PROTOCOL $SIZE..."
        ITGSend "$SCRIPT_FILE" -x "$RECV_LOG"

        echo "Completed IPv6 test for $PROTOCOL $SIZE"
        sleep 2
        PORT=$BASE_PORT  # Reset PORT for the next protocol/size combination
    done
done

echo "All IPv4 and IPv6 ITG tests complete. Logs stored in: $LOGROOT"
