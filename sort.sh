#!/bin/bash

h1url="https://bbscope.com/static/scope/latest-h1.json"
bcurl="https://bbscope.com/static/scope/latest-bc.json"
ywhurl="https://bbscope.com/static/scope/latest-ywh.json"
intiurl="https://bbscope.com/static/scope/latest-it.json"

declare -A map
map["h1"]=$h1url
map["bugc"]=$bcurl
map["ywh"]=$ywhurl
map["inti"]=$intiurl

categories=(android api hardware ios iot ip_address network other website)

for platform in "${!map[@]}"; do
    url="${map[$platform]}"
    dir="res/$platform"

    echo -e "\n[*] Sorting: $platform"
    mkdir -p "$dir"
    rm -f "$dir"/*.txt

    json=$(curl -s "$url")

    for category in "${categories[@]}"; do
        echo "[*] Extracting: $category for $platform"
        echo "$json" |
            jq -r --arg cat "$category" '
                .[] 
                | select(.InScope != null)
                | .InScope[]
                | select(.Category == $cat)
                | .Target
            ' >> "$dir/$category.txt"
    done

    echo "[+] Sorting & removing duplicates for $platform"
    for f in "$dir"/*.txt; do
        [ -f "$f" ] && sort -u "$f" -o "$f"
    done

done

echo -e "\n✔ All Scopes Sorted Successfully!"
tree re