#!/bin/bash

# USAGE: tcp_port_scanner.sh -t <TARGET> -p <PORT_RANGE: START_PORT(Optional)-END_PORT(Optional)

# CONSTANTS
MAX_PORT=65535
MIN_PORT=1

# DEFAULT VALUES
target="127.0.0.1"
port_start=$MIN_PORT
port_end=1000
protocol="tcp"

#----------------------------------------------------------------- PARSE AND VALIDATE SCRIPT OPTIONS -----------------------------------------------------------------

while getopts "t:p:" opt; do
    case $opt in
    t)
        target="$OPTARG"
        ;;
    p)
        port_range="$OPTARG"

        if [[ $port_range == "-" ]]; then
            port_end=$MAX_PORT

        elif [[ $port_range == -* ]]; then
            port_end=${port_range:1}

        elif [[ $port_range == *- ]]; then
            port_start=${port_range::-1}
            port_end=$MAX_PORT

        elif [[ $port_range =~ ^[0-9]+$ ]]; then
            port_start=$port_range
            port_end=$port_range

        elif [[ $port_range =~ ^[0-9]+-[0-9]+$ ]]; then
            port_start=${port_range%-*}
            port_end=${port_range#*-}

        else
            echo "Invalid port range: $port_range"
            exit 1
        fi
        ;;
    \?)
        echo "Options: -t (target) | -p (port range: START_PORT(Optional)-END_PORT(Optional))"
        exit 1
        ;;
    :)
        case $OPTARG in
        *)
            echo "Option -$OPTARG requires an argument." >&2
            exit 1
            ;;
        esac
        ;;
    esac
done

# Validate port values
if [[ ($port_start -lt $MIN_PORT || $port_start -gt $MAX_PORT) || ($port_end -lt $MIN_PORT || $port_end -gt $MAX_PORT) ]]; then
    echo "[-] Error: Each port value must be from 1 to 65535"
    exit 1
fi

# Validate PORT_START <= PORT_END
if [[ $port_start -gt $port_end ]]; then
    echo "[-] Error: PORT_START must be less or equal to PORT_END"
    exit 1
fi

# ----------------------------------------------------------------- FUNCTIONS -----------------------------------------------------------------

# SCAN A SINGLE PORT
scan_port() {
    local target=$1
    local port=$2
    local protocol=$3

    timeout 1 bash -c "echo >/dev/$protocol/$1/$port" 2>/dev/null && echo "OPEN ${protocol^^} PORT: $port"
}

# SCAN A PORT RANGE
scan_port_range() {
    local target=$1
    local port_start=$2
    local port_end=$3
    local protocol=$4

    for ((port = port_start; port <= port_end; port++)); do
        scan_port "$target" "$port" "$protocol"
    done
}

# ----------------------------------------------------------------- MAIN -----------------------------------------------------------------

echo -e "-TARGET: $target\n-MIN_PORT: $port_start\n-MAX_PORT: $port_end\n-PROTOCOL: ${protocol^^}\n"
scan_port_range "$target" "$port_start" "$port_end" "$protocol"
