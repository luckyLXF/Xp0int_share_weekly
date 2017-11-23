# Tomcat 远程代码执行漏洞分析

# 0x00介绍
### Tomcat
Tomcat服务器是一个免费的开放源代码的Web应用服务器。Tomcat是Apache软件基金会（Apache SoftwareFoundation）的Jakarta项目中的一个核心项目，由Apache、Sun和其他一些公司及个人共同开发而成。
### 漏洞介绍
2017年9月19日，Apache Tomcat官方确认并修复了两个高危漏洞，其中就有远程代码执行漏洞(CVE-2017-12615)当存在漏洞的Tomcat 运行在 Windows 主机上，且启用了 HTTP PUT请求方法，恶意访问者通过构造的请求向服务器上传包含任意代码的 JSP 文件，造成任意代码执行，危害十分严重。
### 影响范围：Apache Tomcat 7.0.0 - 7.0.81
### 不受影响的版本：
Apache Tomcat 8.x
Apache Tomcat 9.x

# 0x01漏洞分析
- 在Tomcat安装目录下的配置文件web.xml中的org.apache.catalina.servlets.DefaultServlet方法下如果该方法有如下代码，即表示Tomcat已开启PUT方法

>  <init-param> 
    <param-name>readonly</param-name> 
    <param-value>false</param-value> 
   </init-param>

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(1).png?raw=true)

然后我们就可以通过PUT方法直接上传我们的一句话了。


# 0x02Exp分析

分析从网上找到的exp，加上个人的注释

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(2).png?raw=true)
![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(1).jpg?raw=true)

对exp中的payload进行分析

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(2).jpg?raw=true)

需要注意的是：其中的以字节流的方式读取非常重要，不然会出问题，这个后面会讲到

而以靶机的角度来看，上传的shell首先以.jsp的形式存放在根目录的webapps文件夹下

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(3).png?raw=true)

当在网站上访问时，就会在work目录内创建一个.class和.java文件

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(4).png?raw=true)





# 0x03搭建环境+脚本测试
### 首次搭建
在官网上下载了一份安装包，需要有JDK的环境，安装好了之后访问网站，正常打开，环境搭建成功

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(5).png?raw=true)


然后需要查看web.xml中的配置，在实际操作中发现，web.xml中默认是没有readonly的选项的，也就是说readonly默认为TRUE，这样该漏洞就有点鸡肋了，不过这里先不管，继续测试，添加上readonly的项并设为false


![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(6).png?raw=true)

然后先尝试使用脚本测试

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(3).jpg?raw=true)

一直回显错误
采用手动抓包该包的方式，同样报错，但是显示的是403forbidden

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(8).png?raw=true)

这里搞了很久，以为是环境没有搭好或者权限配置出错，上网也查不到原因
重新看整个实验过程，发现下载的版本是7.0.82，而漏洞出现的版本是7.0.0到7.0.81！！！（白忙活了……）



### 再次搭建环境
在官网上找安装包的时候发现，官网上tomcat7的只有7.0.82的安装包，没有其他版本的，只能在其他网站搜旧版本的安装包，找到7.0.75的

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(9).png?raw=true)

接下来仍然是修改web.xml中的配置，然后再次用脚本测试

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(4).jpg?raw=true)





# 0x04手动测试
### 利用方式
首先抓包把请求方式改成PUT，尝试put一个jsp文件，显示404错误

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(11).png?raw=true)

利用：通过描述中的 Windows 受影响，可以结合 Windows 的特性。其一是 NTFS 文件流，其二是文件名的相关限制（如 Windows 中文件名不能以空格结尾）来绕过限制


### NTFS文件流方式
首先尝试NTFS文件流，回显code为201，代表写入成功

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(12).png?raw=true)


在网站测试其功能
出现问题：虽然命令执行成功，但是没有正确分行，分行符被当成字符打印了出来
原因：脚本中的采用PUT方式访问网站是用httplib库来访问的，而httplib是一个相对底层的http请求模块，而抓包修改是直接把payload放在put的内容里，可能就是因为这个原因导致识别错误
![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(13).png?raw=true)


### 文件名截断方式
#### 测试
之后尝试用文件名截断的方式上传


![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(14).png?raw=true)


用空格截断文件名上传，上传成功，也成功执行了命令

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(15).png?raw=true)

当再次上传相同文件时，脚本中的代码显示code的值应该是204，而实际测试出来的
结果为409

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(16).png?raw=true)


#### 分析
Tomcat 的 Servlet 是在 conf/web.xml 配置的，通过配置文件可知，当后缀名为 .jsp 和 .jspx 的时候，是通过JspServlet处理请求的，而其他的静态文件是通过DeafaultServlet处理的
![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(17).png?raw=true)

当上传的*.jsp文件的文件名有一个空格时，就不能匹配到JspServlet，而是会交由DefaultServlet去处
理。当处理 PUT 请求时，会经过层层调用


![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(18).png?raw=true)


doPut函数会调用resources.bind

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(19).png?raw=true)
![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(20).png?raw=true)

调用 rebind创建文件


![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(21).png?raw=true)


又由于 Windows 不允许“ ”作为文件名结尾，所以会创建一个 .jsp 文件，导致代码执行

### 加‘/’上传
#### 测试
在网上搜索可用的利用方式，发现还有一种方式可以在Linux下搭建的tomcat中同样可以利用，当 PUT 地址为/1.jsp/时，仍然会创建 JSP，会影响 Linux 和 Windows 服务器
抓包进行测试，回显201表示创建成功


![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(22).png?raw=true)
测试功能，同样成功



![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(23).png?raw=true)


#### 分析
在进入 bind 函数时，会声明一个 File 变量，而进入了File后，会对name（即上传的文件名）进行normalize

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(24).png?raw=true)

这里会把jsp后面的“/”去掉，最后生成的路径就没有“/”了



# 0x05修改exp

对exp进行了一点修改，使之可以在得到shell之后获取要执行的命令并访问shell执行

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(25).png?raw=true)



这里的修改还是出现了不少的问题，慢慢说……
问题一：访问的网址错误
原因：脚本采用put方式访问时是以文件流的方式访问的，即.jsp后还有“::$DATA”字符串，而得到shell之后访问时要把后缀去掉，以.jsp形式访问

修改过后再次执行，发现成功回显，但字符编码出错了，这个是小问题先不管

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(26).png?raw=true)

继续尝试其他命令
又出现问题……问题二：执行arp –a命令时出错，显示HTTP Error 400: Bad Request。

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(27).png?raw=true)

在网站上访问这个shell，执行同样的命令，回显正常
思考：其他命令都能执行而这条却不行，肯定不是urllib2库的问题，那就观察一下是不是这条命令有什么不一样的地方，发现只是这个命令里面有一个空格而其他没有，那就可能是这个空格的原因


上网查询了很多资料
发现可能是访问的网址的写法出现了问题，可能URLlib2的库遇到空格会出现问题，换一种方式写

![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(28).png?raw=true)

再次执行，成功回显，在回显中可以看到，采用urllib.quote()后，会对字符串进行url编码，这时成功执行，说明确实是空格的问题


![](https://github.com/luckyLXF/Xp0int_share_weekly/blob/master/tomcat/1%20(29).png?raw=true)


# 0x06后记
参考资料：
- http://www.freebuf.com/vuls/148283.html
- https://www.ichunqiu.com/course/59209







