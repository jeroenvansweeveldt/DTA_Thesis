#!/bin/bash

for f in $1
do
	tesseract "$f" "$2/$(basename $f | cut -f 1 -d '.')" hocr
done