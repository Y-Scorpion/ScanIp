import re
import sys
import requests
from threading import Thread, Lock
import time
import queue as Queue
import getopt

# url列表，这里是虚构的,现实情况这个列表里有大量的url
link_list = ['http://www.baidu.com',
             'http://www.qq.com',
             'http://www.xxx.com',
             'http://www.sogou.com',
             'http://www.dsds.com']


# 读取文档ip拼接成URL
def verdictIp(path, port):
    global link_list
    get_ip_res = get_url(path)
    if get_ip_res:
        for ip in get_ip_res:
            try:
                res = re.search(r'^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5]).(\d{1,2}|1\d\d|2[0-4]\d|25[0-5]).(\d{1,'
                                r'2}|1\d\d|2[0-4]\d|25[0-5]).(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$', ip).group()
                link_list.append('http://' + res + ':' + port)
            except Exception as err:
                print("OS error: {0}".format(err))
    else:
        print('文件不存在......')
        sys.exit(1)


# 读取文件内容
def get_url(path):
    """
    打开存放url的文件，并将结果返回出去
    :return:
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = f.readlines()
            return data
    except Exception:  # 文件不存在则返回False
        return False


class myThread(Thread):
    def __init__(self, name, q):
        Thread.__init__(self)
        self.name = name
        self.q = q

    def run(self):
        print("Starting " + self.name)
        while True:
            try:
                crawler(self.name, self.q)
            except:
                break
        print("Exiting " + self.name)


def crawler(threadName, q):
    """
    爬行方法
    """
    # 从队列里获取url
    ip_url = q.get(timeout=1)
    f = open('scan.txt', 'ab')
    try:
        r = requests.get(ip_url, timeout=2)
        # 打印：队列长度，线程名，响应吗，正在访问的url
        if r.status_code == 200:
            lock.acquire()
            data = "url:%s :status:%s \n" % (ip_url, r.status_code)
            f.write(data.encode())
            lock.release()
            print(q.qsize(), threadName, ip_url, "访问成功_状态码：", r.status_code)
    except Exception as e:
        print(q.qsize(), threadName, "目标访问超时/网络不可达: ")


def get_args_func(argv):
    port = '8080'  # 默认值
    path = 'ips.txt'
    try:
        opts, args = getopt.getopt(argv, "hp:f:", ["help", "port=", "File="])
    # 表示参数选项有：-h/ --help -p/ --port,
    # 它们相互对应；该方法的返回值有两个元素: 第一个是(opt, value)元组的列表，第二个是一般参数列表，包含那些没有 '-' 或 '--' 的参数
    except getopt.GetoptError:
        # 获取到非指定的- 或者长选项--的参数给出正确提示
        print('参数错误，格式: python %s -p <port> -f <path+FileNmae>' % sys.argv[0])
        print('参数错误，参考格式: python %s --port=<port> -File=<path+FileNmae>' % sys.argv[0])
        sys.exit(2)
    for opt, value in opts:  # 依次获取列表中的元组项
        if opt in ("-h", "--help"):
            print(' USAGE: %s -p <port> ')
            print('or: %s --port=<port>')
            sys.exit(0)
        elif opt in ('-p', '--port'):
            port = value
        elif opt in ('-f', '--File'):
            path = value
    print('-----------------------------------------------------------------------')
    print("获取到端口参数端口 -p or --port:", port)
    print("获取到文件参数端口 -f or --File:", path)
    verdictIp(path, port)


if __name__ == '__main__':
    get_args_func(sys.argv[1:])
    print("开始运行。。共扫描ip：%d 个。。。默认开启20线程，2秒超时等待" % len(link_list))
    print("_______________________________________________________________")
    start = time.time()  # 开始时间
    # 创建5个线程名
    threadList = ["Thread-1", "Thread-2", "Thread-3", "Thread-4", "Thread-5", "Thread-6", "Thread-7", "Thread-8",
                  "Thread-9", "Thread-10", "Thread-11", "Thread-12", "Thread-13", "Thread-14", "Thread-15",
                  "Thread-16", "Thread-17", "Thread-18", "Thread-19", "Thread-20"]
    # 设置队列长度
    workQueue = Queue.Queue(1000)
    # 线程池
    threads = []
    lock = Lock()  # 创建锁对象
    # 创建新线程
    for tName in threadList:
        thread = myThread(tName, workQueue)
        thread.start()
        threads.append(thread)

    # 将url填充到队列
    for url in link_list:
        workQueue.put(url)

    # 等待所有线程完成
    for t in threads:
        t.join()

    end = time.time()
    print('Queue多线程爬虫总时间为：', end - start)
    print('程序运行完成,结果默认写入当前目录下scan.txt')
