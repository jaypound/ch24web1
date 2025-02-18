sudo certbot renew --dry-run --manual --preferred-challenges http \
  --manual-auth-hook /home/ubuntu/ch24web1/auth.sh \
  --manual-cleanup-hook /home/ubuntu/ch24web1/cleanup.sh
