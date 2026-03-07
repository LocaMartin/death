From direct URL 
```
https://bbscope.com/static/scope/latest-bc.json
https://bbscope.com/static/scope/latest-ywh.json
https://bbscope.com/static/scope/latest-it.json
https://bbscope.com/static/scope/latest-h1.json
```
To API
```yml
GET
/api/v1/targets/wildcards
Wildcard root domains, useful for subdomain enumeration.
```
```yml
GET
/api/v1/targets/domains
Domains (non-URL, non-wildcard targets).
```
```yml
GET
/api/v1/targets/urls
URL targets (http:// or https://).
```
```yml
GET
/api/v1/targets/ips
IP addresses (extracted from IPs and URLs).
```
```yml
GET
/api/v1/targets/cidrs
CIDR ranges and IP ranges.
```