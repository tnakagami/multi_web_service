# Create .evn file
An example follows:

```bash
MYDNSJP_MASTER_ID=masterid
MYDNSJP_PASSWORD=password
MYDNS_EMAIL_ADDR=user@example.com
BASE_DOMAIN_NAME=example.com
VHOST_NAME=www.example.com
SSL_CERT_PATH=/etc/nginx/default_certs/default.crt
SSL_CERTKEY_PATH=/etc/nginx/default_certs/default.key
SSL_STAPLING_VERIFY=off
SSL_TRUSTED_CERTIFICATE_PATH=/etc/nginx/default_certs/default.crt
```

# Create .htpasswd file
An example follows:

```bash
user:rox7Jdqy.byUU
```

In this way, username is "user", password is "password".

Then, run the following command to enable it.

```bash
# The directory path is /path/to/multi_web_service
cat env_file/nginx/.htpasswd > nginx/htpasswd
```
