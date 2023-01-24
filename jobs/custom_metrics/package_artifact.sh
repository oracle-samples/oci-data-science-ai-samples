#! /bin/bash

set -eo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$DIR/build"
rm -f "$DIR/build/artifact.tar.gz"
pushd "$DIR/artifact"
tar czvf "$DIR/build/artifact.tar.gz" .
popd
