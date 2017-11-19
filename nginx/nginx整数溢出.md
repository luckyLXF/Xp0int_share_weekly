# Nginx整数溢出漏洞

## 0x00 介绍
### Nginx
Nginx是一款轻量级的Web 服务器/反向代理服务器及电子邮件（IMAP/POP3）代理服务器，并在一个BSD-like 协议下发行。其特点是占有内存少，并发能力较强，Nginx 可以在大多数 UnixLinux OS 上编译运行，并有 Windows 移植版。
### 漏洞介绍
近期，Nginx官方发布最新的安全公告，漏洞CVE编号为CVE-2017-7529，该在nginx范围过滤器中发现了一个安全问题，通过精心构造的恶意请求可能会导致整数溢出并且不正确处理范围，从而导致敏感信息泄漏，存在安全风险。该漏洞影响所有0.5.6 - 1.13.2版本内默认配置模块的Nginx只需要开启缓存恶意访问者即可发送恶意请求进行远程访问造成信息泄露。
当Nginx服务器使用代理缓存的情况下恶意访问者通过利用该漏洞可以拿到服务器的后端真实IP或其他敏感信息。通过我们的分析判定该漏洞利用难度低可以归属于low-hanging-fruit的漏洞在真实网络中也有一定的风险。




## 0x01 基础知识
### （1）curl的基础用法
介绍：curl是一个利用URL规则在命令行下工作的文件传输工具，可以说是一款很强大的http命令行工具
1.  curl http://www.baidu.com
执行后，baidu的html页面（相当于网页源代码）就会显示在屏幕上了
2.	保存访问的网页 curl http://www.baidu.com >> baidu.html（linux重定向功能）
或者直接用curl内置的选项 –o 保存网页
curl -o baidu.html http://www.baidu.com
3.	指定proxy服务器以及其端口
curl -x 192.168.100.100:1080 http://www.baidu.com
4.	保存http的response里面的cookie信息
curl -c cookiec.txt  http://www.baidu.com
5.	保存http的response里面的header信息
curl -D cookied.txt http://www.daidu.com
6.  输出时包括protocol头信息   -i/--include 
7.  检索来自HTTP/1.1或FTP服务器字节范围  -r/--range <range> 

Curl还有很多其他的功能，有需要的可自行查找
在这个漏洞中主要用到的是-i参数和-r参数
参考网站：https://www.cnblogs.com/duhuo/p/5695256.html
### （2）Nginx Cache
Nginx可以作为缓存服务器，将Web应用服务器返回的内容缓存起来。如果客户端请求的内容已经被缓存，那么就可以直接将缓存内容返回，而无需再次请求应用服务器。由此，可降低应用服务器的负载，并提高服务的响应性能。
Nginx配置缓存主要由以下命令完成：
proxy_cache_key用于区分cache文件。（相当于每个缓存文件的身份证）
proxy_cache_path设置cache文件的路径和参数。（缓存文件的路径）
- cache文件会保存在指定的目录下面，文件名是cache key的MD5值（可以确保每个缓存文件的名字不重复）
- 通过level参数将cache文件分多层目录保存，以避免某个目录下存在大量文件造成的性能开销
- 通过keys_zone参数指定cache key在内存中的区域及其大小，1M的区域大概可以保存8000条key的信息
proxy_cache_valid对不同返回状态值设定cache有效时间

例如，下面这条配置：

![](https://raw.githubusercontent.com/luckyLXF/Xp0int_share_weekly/master/nginx/image001.png)

指定了以下信息：

- 使用协议、请求方法、域名、URI作为cache key
- cache文件保存在目录/tmp/Nginx/下，采取两层目录，keys_zone名称为my_zone，大小为10M（key_zone相当于存放的仓库的名称）
- proxy_cache_valid表示对于返回状态值为200的内容，cache有效时间为10分钟
这几条命令相当于在nginx中开辟出一块地方用于存放缓存的文件
接着对文件进行缓存
![](https://raw.githubusercontent.com/luckyLXF/Xp0int_share_weekly/master/nginx/image002.png)

配置命令解释如下：
proxy_cache指定使用的keys_zone名称（即仓库名称），就是之前的my_zone
add_header在Nginx返回的HTTP头中，增加一项X-Proxy-Cache，如果缓存命中其值为HIT，未命中则为MISS（意思是如果在服务器中没有缓存此文件则回显MISS，有缓存则为HIT）
proxy_ignore_headers由于百度对图片的请求也会Set-Cookie设置，而Nginx不会缓存带有Set-Cookie的返回，因此我们这里设置忽略该HTTP头

### （3）HTTP头部range域

http协议从1.1开始支持获取文件的部分内容，这为并行下载以及断点续传提供了技术支持。它通过在Header里两个参数实现的，客户端发请求时对应的是Range，服务器端响应时对应的是Content-Range
当在header中定义了range时相当于请求文件的一个或者多个子范围内的字节
例如：
表示头500个字节：bytes=0-499  
表示第二个500字节：bytes=500-999  
表示最后500个字节：bytes=-500  
表示500字节以后的范围：bytes=500-  
同时指定几个范围：bytes=500-600,601-999 







## 0x03 漏洞原理
该漏洞出现的地方为对http header中range域处理不当造成，主要是在ngx_http_range_parse 函数中的循环
该函数要把“-”两边的数字取出分别赋值给 start 和 end 变量标记读取文件的偏移和结束位置。而对于有额外头部的缓存文件若start值为负（合适的负值）那么就意味着缓存文件的头部也会被读取。
首先，如果传入完整的range参数，如start-end，则在ngx_http_range_parse()中会检查start，确保其不会溢出为负值：
![](https://raw.githubusercontent.com/luckyLXF/Xp0int_share_weekly/master/nginx/image003.png)

这就意味着不能再start处做手脚，而要让start为负数来读取到头文件，就只能通过-end这类后缀型range参数实现
![](https://raw.githubusercontent.com/luckyLXF/Xp0int_share_weekly/master/nginx/image005.png)

此时的start等于content-length减去读入的end值，这里的content-length为文件的总字节数，当传入的end的值比实际长度还要长，就可以使start变为负数，而结尾则为总字节数大小减1，这样一来读取的字节数就比原来的大，因此能读取到头部信息
![](https://raw.githubusercontent.com/luckyLXF/Xp0int_share_weekly/master/nginx/image006.png)

但这里存在一个问题，Nginx对range总长度会有检查，当size的值大于content_length，即要读取的值大于文件的字节数大小，就直接将原文件返回了
这个漏洞就是用一个整除溢出来绕过这一限制，具体而言，检查用到的size是将multipart的全部range长度相加得到的：
![](https://raw.githubusercontent.com/luckyLXF/Xp0int_share_weekly/master/nginx/image009.png)

那我们可以定义多个range，使其长度之和溢出为负数，就可以绕过总长度的检查

- 要得到一个很大长度的range，同样可以采用-end这种后缀型，将end设置为一个非常大的数即可。
- 此处的start, end, size均为64位有符号整形，所以只需要最终相加得到的size为0×8000000000000000即可。而其中的两个range，第一个用于向前读其他数据，据漏洞报告称该range和content length的差值最好保持在600左右才能较好地读取到数据，第二个范围值range2=size-range1，用于相加后溢出为负数
- 例如：文件缓存的字节数为16585，那么选取的range1的值可以为17185，range2 值为 0x8000000000000000-17185, 也就是 9223372036854758623，然后构造请求
- curl -i http://127.0.0.1:8000/proxy/demo.png -r -17208,-9223372036854758600
即可成功读取到缓存信息









## 0x04 漏洞演示
首先先跟新缓存，第一次访问时X-Proxy-Cache为MISS，没有该缓存文件
![](https://raw.githubusercontent.com/luckyLXF/Xp0int_share_weekly/master/nginx/image010.png)

再次访问，可知已经命中缓存

![](https://raw.githubusercontent.com/luckyLXF/Xp0int_share_weekly/master/nginx/image013.jpg)
然后尝试读取缓存信息，从Content type可知是采用多段range来读取的，但没有返回缓存的KEY

![](https://raw.githubusercontent.com/luckyLXF/Xp0int_share_weekly/master/nginx/image015.png)


在网上查到的信息：如执行以上命令无结果显示，可多次执行此命令

- 这里出现的问题：尝试了很多都只显示了如上的信息，没有返回缓存的信息
- 解决方法：尝试了改变range的值，没有效果，最后发现是curl的参数设错了-I参数表示只显示文档信息，而-i参数表示输出时包括protocol头信息，这里应该采用-i参数而不是-I
再次尝试，成功读取缓存的key

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/nginx/image017.jpg?raw=true)

接下去的乱码为该文件的缓存内容

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/nginx/image019.jpg?raw=true)

这里发现一个有趣的bug，当执行完上一条curl的命令读取缓存信息时，会自动填上我的下一条命令，目前还找不出原因

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/nginx/image021.jpg?raw=true)





## 0x05 POC分析
![](https://raw.githubusercontent.com/luckyLXF/Xp0int_share_weekly/master/nginx/image022.png)








## 0x06 漏洞修复
可以对ngx_http_range_parse函数进行修复
进一步检测了size的溢出情况，防止size溢出后造成小于content-length这条判断的绕过 
－　限定使用后缀的情况下，start不能为负的，最小只能是0，也就是说使用“-xxx”的方式对Cache文件的读取只能从0开始到结束
－　在不升级的情况下，可以在Nginx配置文件中添加max_ranges 1，从而禁用multipart range。


## 0x07 后记
这个漏洞的参考资料较少，且涉及的内容较多，虽然漏洞的利用较为简单，但却要学习很多额外的东西才能搞懂，在这个过程中也学到了不少知识。
参考资料：
- https://www.ichunqiu.com/course/59767
- http://www.freebuf.com/articles/terminal/140402.html
- http://blog.csdn.net/ski_12/article/details/76944203
- https://q.cnblogs.com/q/51666/










