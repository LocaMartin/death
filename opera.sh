#!/bin/bash

# List of Node Exporter endpoints
targets=(
http://82.145.211.104:9100/metrics
http://82.145.211.160:9100/metrics
http://82.145.211.165:9100/metrics
http://82.145.211.144:9100/metrics
http://82.145.211.158:9100/metrics
http://82.145.211.163:9100/metrics
http://82.145.211.175:9100/metrics
http://82.145.211.186:9100/metrics
http://82.145.211.207:9100/metrics
http://82.145.211.157:9100/metrics
http://82.145.211.208:9100/metrics
http://82.145.211.222:9100/metrics
http://82.145.211.221:9100/metrics
http://82.145.211.239:9100/metrics
http://82.145.211.247:9100/metrics
http://82.145.211.38:9100/metrics
http://82.145.211.34:9100/metrics
http://82.145.211.42:9100/metrics
http://82.145.211.176:9100/metrics
http://82.145.211.55:9100/metrics
http://82.145.211.50:9100/metrics
http://82.145.211.13:9100/metrics
http://82.145.211.63:9100/metrics
http://82.145.211.91:9100/metrics
http://82.145.211.95:9100/metrics
http://82.145.211.92:9100/metrics
)

# Fields to search for (you can add more)
patterns=(
"node_uname_info"
"node_os_info"
"node_dmi_info"
"node_disk_filesystem_info"
"node_filesystem_size_bytes"
"node_filesystem_free_bytes"
"node_systemd_version"
"node_exporter_build_info"
"node_cpu"
"node_memory"
)

echo "============ NODE EXPORTER INFO LEAK SCAN ============"

for url in "${targets[@]}"; do
    echo ""
    echo "▶ Checking: $url"

    # Download metrics
    data=$(curl -s --max-time 5 "$url")

    if [[ -z "$data" ]]; then
        echo "  ✘ No response"
        continue
    fi

    # Count matches
    for p in "${patterns[@]}"; do
        count=$(echo "$data" | grep -c "$p")
        if [[ "$count" -gt 0 ]]; then
            echo "  [+] $p : $count entries leaked"
        fi
    done
done

echo ""
echo "============ DONE ============"
