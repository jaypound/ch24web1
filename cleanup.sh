#!/bin/bash
# Path to your webroot where the challenge files are stored.
WEBROOT="/home/ubuntu/ch24web1"  # same as above

CHALLENGE_DIR="$WEBROOT/acme-challenge"

# Remove the challenge file.
rm -f "$CHALLENGE_DIR/$CERTBOT_TOKEN"

