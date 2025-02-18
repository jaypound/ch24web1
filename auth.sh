#!/bin/bash
# Path to your webroot where the challenge files should be placed.
WEBROOT="/home/ubuntu/ch24web1"  # e.g., /var/www/html

# The directory that will host the challenge files.
CHALLENGE_DIR="$WEBROOT/acme-challenge"

# Ensure the directory exists.
mkdir -p "$CHALLENGE_DIR"

# Create the challenge file.
echo "$CERTBOT_VALIDATION" > "$CHALLENGE_DIR/$CERTBOT_TOKEN"

