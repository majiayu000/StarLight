# A simple Golang-based file downloader may be made into a web disk

## For better downloading, Need a domain and cert.

## certbot instructions

```
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo certbot --nginx
sudo certbot renew --dry-run
```