#!/bin/bash

# Stops the script, if an error occurred.
set -e

printenv

DESTINATION_DIR=$DESTINATION_DIR
mkdir -p $DESTINATION_DIR

DESTINATION="$DESTINATION_DIR/master.zip"
# Remove source file if exist.
if [[ -f "$DESTINATION" ]]; then
  rm -rf "$DESTINATION";
fi

wget -O $DESTINATION https://github.com/zapret-info/z-i/archive/master.zip

## Remove source folder if exist.
SOURCE_DIR="$DESTINATION_DIR/z-i-master"
if [[ -d "$SOURCE_DIR" ]]; then
  rm -rf "$SOURCE_DIR";
fi
unzip $DESTINATION -d $DESTINATION_DIR

# Create destination folder if not exist.
IMPORT_DIR="$DESTINATION_DIR/utf8"
if [[ ! -d "$IMPORT_DIR" ]]; then
  mkdir "$IMPORT_DIR";
fi

# Iterate over *.csv files and fix encoding.
for filename in $SOURCE_DIR/*.csv; do
  [ -e "$filename" ] || continue
  name=${filename##*/}
  base=${name%.csv}
  iconv -f windows-1251 -t utf-8 "$filename" > "${IMPORT_DIR}/${base}_utf8.csv";
done;

# Run update script.
MONGODB_IMPORT_COLLECTION="blocked_$(date +"%m_%d_%Y")"
MONGODB_IMPORT_COLLECTION=$MONGODB_IMPORT_COLLECTION \
IMPORT_DIR=$IMPORT_DIR \
/usr/local/bin/python /updater/update.py
