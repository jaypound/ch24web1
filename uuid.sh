#!/bin/bash

# Generate a UUID and convert it to lowercase
lowercase_uuid=$(uuidgen | tr '[:upper:]' '[:lower:]')

# Output the lowercase UUID
echo "$lowercase_uuid"

