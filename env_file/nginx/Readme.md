# Create .evn file
An example follows:

```bash
MYDNSJP_MASTER_ID=masterid
MYDNSJP_PASSWORD=password
MYDNS_EMAIL_ADDR=user@example.com
BASE_DOMAIN_NAME=example.com
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
