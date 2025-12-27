#!/bin/bash

HOTZONE_SIZE=10

while true; do
  eval $(xdotool getmouselocation --shell)
  
  if [ "$X" -lt $HOTZONE_SIZE ] && [ "$Y" -lt $HOTZONE_SIZE ]; then
    echo "Top-left corner reached"
    sleep 2
  fi

  sleep 0.1
done

