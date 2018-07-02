#!/bin/bash
set -euvo pipefail

compose_file=${1:-}
if [[ -z "$compose_file" ]]; then
    echo "usage: $0 <compose_file>"
    exit 1
fi

~/sfs_update.py -d $1 ${SFS_URL}