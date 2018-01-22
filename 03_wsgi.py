import socket
import re
import multiprocessing
import sys

# import mini_web_03

class WEBServer(object):
    def __init__(self,port): # 谁用谁传

        # 1. 创建套接字
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 2. 绑定
        self.tcp_server_socket.bind(("", port))

        # 3. 变为监听套接字
        self.tcp_server_socket.listen(128)

    def service_client(self, new_socket,moudle): # 谁用谁传
        """为这个客户端返回数据"""

        # 1. 接收浏览器发送过来的请求 ，即http请求
        # GET / HTTP/1.1
        # .....
        request = new_socket.recv(1024).decode("utf-8")
        # print(">>>"*50)
        # print(request)

        request_lines = request.splitlines()
        print("")
        print(">" * 20)
        print(request_lines)

        # GET /index.html HTTP/1.1
        # get post put del
        file_name = ""
        ret = re.match(r"[^/]+(/[^ ]*)", request_lines[0])
        if ret:
            file_name = ret.group(1)
            # print("*"*50, file_name)
            if file_name == "/":
                file_name = "/index.html"
        # 2. 返回http格式的数据，给浏览器
        # 如果文件的缀是.py那么我们服务器返回 数据,如果是其他的,还是原先去硬盘读取数据返回
        if file_name.endswith('.py'):
            url_dict = dict()  # 空字典

            url_dict["file_name"] = file_name
            # 动态返回数据
            body = moudle.application(url_dict, self.set_head_params)
            # head = "HTTP/1.1 200 OK\r\n"
            head = "HTTP/1.1 %s\r\n"%self.status

            # 通过循环去添加我们的头部
            for temp in self.params:
                head += "%s:%s\r\n"%(temp[0],temp[1])


            content = head + "\r\n" + body

            new_socket.send(content.encode("utf-8"))


        else:
            # 静态返回数据
            try:
                f = open("./static" + file_name, "rb")
            except:
                response = "HTTP/1.1 404 NOT FOUND\r\n"
                response += "\r\n"
                response += "------file not found-----"
                new_socket.send(response.encode("utf-8"))
            else:
                html_content = f.read()
                f.close()
                # 2.1 准备发送给浏览器的数据---header
                response = "HTTP/1.1 200 OK\r\n"
                response += "\r\n"
                # 2.2 准备发送给浏览器的数据---boy
                # response += "hahahhah"

                # 将response header发送给浏览器
                new_socket.send(response.encode("utf-8"))
                # 将response body发送给浏览器
                new_socket.send(html_content)

        # 关闭套接
        new_socket.close()

    def run_server(self,moudle):
        """用来完成整体的控制"""
        # # 1. 创建套接字
        # tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #
        # # 2. 绑定
        # tcp_server_socket.bind(("", 7890))
        #
        # # 3. 变为监听套接字
        # tcp_server_socket.listen(128)

        while True:
            # 4. 等待新客户端的链接
            new_socket, client_addr = self.tcp_server_socket.accept()

            # 5. 为这个客户端服务
            p = multiprocessing.Process(target=self.service_client, args=(new_socket,moudle))
            p.start()

            new_socket.close()

        # 关闭监听套接字
        tcp_server_socket.close()

    def set_head_params(self,status,params):
        self.status = status
        self.params = params


def main():

    try:
        # print(sys.argv)
        #
        # port = int(sys.argv[1])


        # params_dict = {"port":8989}

        with open("wsgi.config") as f:
            content = f.read()

        # 转成字典
        params_dict = eval(content)
        port = params_dict['port']

        # 告诉系统去哪里找
        sys.path.append("./dynamic")

        # moudle = __import__('mini_web_03')
        moudle = __import__(params_dict['moudle_name'])

        # 得到方法对象的引用
        center = getattr(moudle, "center")
        print(center())

        web_server = WEBServer(port)  # 开启服务器
        web_server.run_server(moudle)  # 运行服务
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
