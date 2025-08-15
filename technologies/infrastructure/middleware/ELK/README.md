# What is ELK?
The ELK Stack is a collection of three open source products:
- `Elasticsearch`
- `Logstash`
- `Kibana`


# When to use ELK?

ELK is designed to allow us to take data from any source, in any format, and to search, analyze, visualize data in real time.

At this time, we want to analyze django logs by ELK.


# Setup ELK
It is a little trouble to install three soft ware separate. Here we use [docker-elk](https://github.com/deviantony/docker-elk#host-setup).

```shell
git clone https://github.com/deviantony/docker-elk.git
cd docker-elk
docker-compose up setup
# initialize the users 
docker-compose up
```

```shell
# use docker ps to see the status of docker
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/a8b2765f9720431da2da48c8f2c1adbf.png)

# Store logs

We can store logs by `logstash`.

## TCP input
By default, the stack exposes the following ports: 
`50000: Logstash TCP input`

We can send log by tcp in django.

```py
# Add this in settings.py in django
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'logstash': {
            'level': 'INFO',
            'class': 'logstash.TCPLogstashHandler',
            'host': 'localhost',
            'port': 50000,  # Default value: 5000
            'version': 1,
            'message_type': 'django_logstash',  # 'type' field in logstash message. Default value: 'logstash'.
            'fqdn': False,  # Fully qualified domain name. Default value: false.
            'tags': ['django.request'],  # list of tags. Default: None.
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['logstash'],
            'level': 'WARNING',
            'propagate': True,
        },
    }
}
```

