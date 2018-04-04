#-*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
from cryptokit import AESCrypto
import threading
import Queue
import sys,os,time,random
import logging
import webbrowser
user_agents = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]
header = {'user_agents':random.choice(user_agents)}
def try_get(url):
	content = None
	count = 0
	file_name = url.split("/")[-1].encode("utf-8")
	if len(file_name)>20:
		file_name = "初始页面"
	while content==None and count<10:
		try:
			content = requests.get(url,timeout=20,headers = header)
			if content.status_code==200:
				logging.info("成功获取 %s" %file_name)
				return content
			else :
				logging.error("请于网页输入验证码")
				#网页设置了防爬虫，用于手动输入验证码
				#webbrowser.open(url)
				content=None
				input("请按任意键继续")
		except Exception as e:
			count += 1
			if count ==1:			
				logging.error(e)
			logging.info("第%i次重新下载 %s" %(count,file_name))

			#由于网络环境定制get异常处理
	#logging.error("获取%s失败" %file_name)
	sys.exit()

def save_data():
	while q.qsize() != 0: 
		piece = q.get()
		index = int(piece[-6:-3])
		temp_file_content = try_get(url_pre2+piece).content
		offset = 16 - len(str(index))
		iv = "\0"*offset + str(index)
		#iv为文件序列号
		crypto = AESCrypto(key,iv)
		decode_data = crypto.decrypt(temp_file_content)
		#源程序修改去掉了decode(),返回bytes
		data[index] = decode_data
		#放入data字典中，用文件名进行索引
		logging.info("完成"+piece.encode("utf-8")+"解码  剩余%i个"%(q.qsize()+threading.active_count()-2))
		#本身一个，主进程一个
logging.basicConfig(level = logging.INFO,format='%(asctime)s %(threadName)s %(levelname)s: %(message)s',datefmt="%Y/%m/%d %H:%M:%S")
start = time.time()
logging.info("开始程序")
if len(sys.argv)!= 2 :
	logging.warn("请有且仅输入一个网址！")
	sys.exit()
#获取ts文件url和文件名
start_url = sys.argv[1]
r = try_get(start_url)
soup = BeautifulSoup(r.content,"lxml")
m1_file_url = soup.find('source').get('src')
title = soup.title.text.encode("utf-8")
url_pre = m1_file_url[:-10]
m1_file = try_get(m1_file_url)
m2_file_url = url_pre + m1_file.text.split("\n")[-1]
m2_file = try_get(m2_file_url)
url_pre2 = m2_file_url[:-10]
key_file_url = url_pre2 + "key.key"
ts_files = []
raw = m2_file.text.split("\n")
for item in raw:
	if "ts" in item:
		ts_files.append(item)
key = try_get(key_file_url).content
#检验是否存在文件，如果有再进行选择
if os.path.isfile(title+".mp4"):
	 inp = input("是否删除已经存在文件 %s ？(Y/N)" %(title+".mp4"))
	 if inp == "y":
	 	os.remove(title+".mp4")
	 elif inp == "n":
	 	sys.exit()
	 else :
	 	logging.warn("输入错误退出系统!")
	 	sys.exit()

#开启线程进行下载
#进行pdb调试
#pdb.set_trace()
data = {}
q = Queue.Queue()
t_count = 30
for piece in ts_files:
	q.put(piece)

for i in range(t_count):
	t = threading.Thread(target = save_data)
	t.start()
while threading.active_count() != 1:
	#阻塞主程序
	pass
#开始合并文件
logging.info("开始合并！！！")
mp4 = open('%s.mp4' %title,"ab")
for i in range(len(ts_files)):
	try:
		mp4.write(data[i])
	except:
		logging.warn("缺少第%i个文件" %i)
mp4.close()

logging.info("合并完成")
end = time.time()
logging.info("成功获取 %s，大小:%.2fMB，耗时:%.2f秒" %(title[:10],os.path.getsize(title+".mp4")/1024**2,(end-start)))
