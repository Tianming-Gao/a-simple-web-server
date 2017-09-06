# a-simple-web-server
简易的Web服务器

这个项目来自《500 Lines or Less》中的“A Simple Web Server”，作者是Greg Wilson。  
我估计作者使用的非常老旧的版本，这使我花费了很多时间在debug上。  
不过，最终我完成了它！
实现的功能有：  
1. 如果路径代表文件，就显示它；如果文件不存在就显示404
2. 如果路径代表目录，我们找寻index.html并展示它；如果找不到index.html，就显示目录内容的列表
3. 通过CGI协议，添加新的功能

# [A Simple Web Server](http://aosabook.org/en/500L/a-simple-web-server.html)
