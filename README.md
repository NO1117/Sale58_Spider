# Sale58_Spider
##58同城爬虫实战项目
页面分析，详见：https://blog.csdn.net/m0_37903789/article/details/84310790

### 安装Python

至少Python3.5以上

### 安装MyProxyPool

源码链接：https://github.com/NO1117/MyProxyPool

### 配置代理池

```
cd proxypool
```

进入proxypool目录，修改settings.py文件

PASSWORD为Redis密码，如果为空，则设置为None
修改TEST_URL = 'http://bj.58.com/sale.shtml'
在启动代理池，先让代理池运行一会，抓取一定数量的代理


### 获取代理


利用requests获取方法如下

```
import requests

PROXY_POOL_URL = 'http://localhost:5000/random'

def get_proxy():
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
    except ConnectionError:
        return None
```

## 各模块功能

* 58_sale_spider.py

  > 爬虫模块，主要解析网页。并提取数据


* db.py

 > 数据库操作模块，用于数据的存储和查询 
  
* setting.py

  > 设置模块，包含数据块配置和模块开关，以及其他配置
  