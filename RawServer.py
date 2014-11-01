#!/usr/bin/env python

import threading
import Queue
import time
import logging
import struct
import socket, binascii

global IP, TCP, UDP, HTTP 
IP, TCP, UDP, HTTP = False, False, False, False

#FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
LOG_FILENAME = 'rawserver.log'
logging.basicConfig(filename=LOG_FILENAME,
			level=logging.DEBUG)

#d = {'clientip': '192.168.0.1'}
logger = logging.getLogger('Rawserver')


class WorkerThread(threading.Thread):
	'''Threads ready to work !'''
	def __init__(self, queue) :
		threading.Thread.__init__(self)
		self.queue = queue

	def run(self):
		while True :
			data = self.queue.get()
			logger.info("Data received : %s \n"%str(data))
			#time.sleep(2)
			self.queue.task_done()


def createThreads(number):
	'''Call me to start n(number) Threads !'''
	try:	
		for i in range(number):
			logger.info("Creating %d threads"%i)
			worker =  WorkerThread(queue)
			worker.setDaemon(True)
			worker.start()	
	except:
		logger.error("Error : Threads not created")


def parseETH(header):
	'''Parse Ethernet headers'''
	global IP
	eth_hdr = struct.unpack("!6s6s2s", header)
	source = binascii.hexlify(eth_hdr[0])
	dest = binascii.hexlify(eth_hdr[1])
	print "\nEthernet"
	print "-Source:\t ", source
	print "-Dest:\t\t ", dest

	if binascii.hexlify(eth_hdr[2]) == '0800':
		IP = True

def parseIP(header):
	'''Parse IP headers'''
	global TCP, UDP
	ip_hdr = struct.unpack("!9s1s2s4s4s", header)
	source = socket.inet_ntoa(ip_hdr[3])
	dest = socket.inet_ntoa(ip_hdr[4])

	print "\nIP"
	print "-Source:\t ", source
	print "-Dest:\t\t ", dest

	if binascii.hexlify(ip_hdr[1]) == '06':
		TCP = True

	elif binascii.hexlify(ip_hdr[1]) == '11':
		UDP = True

def parseTCP(header):
	global HTTP
	tcp_hdr = struct.unpack("!2s2s16s", header)
	src_port = binascii.hexlify(tcp_hdr[0])
	dst_port = binascii.hexlify(tcp_hdr[1])

	#converted ports in hex to decimal value
	print "\nTCP"
	print "-Source port:\t\t", int(src_port, 16)
	print "-Destination port:\t", int(dst_port, 16)

	if (int(src_port, 16) == 80 ) or (int(dst_port, 16) == 80):
		HTTP = True

def parseUDP(header):
	udp_hdr = struct.unpack("!2s2s16s", header)
	src_port = binascii.hexlify(udp_hdr[0])
	dst_port = binascii.hexlify(udp_hdr[1])


	#converted ports in hex to decimal value
	print "\nUDP"
	print "-Source port:\t\t", int(src_port, 16)
	print "-Destination port:\t", int(dst_port, 16)


def parseHTTP(data):
	print data


rawSocket = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x800))
#queue=Queue.Queue()
while True:

	pkt = rawSocket.recvfrom(2048)
	print "Received packet:"

	parseETH(pkt[0][0:14])

	if IP:
		parseIP(pkt[0][14:34])

	if TCP:
		parseTCP(pkt[0][34:54])

	elif UDP:
		parseUDP(pkt[0][34:54])

	if HTTP:
		parseHTTP(pkt[0][54:])

	print "\nDone\n\n"



#returnThreads = createThreads(10)

#for j in range(10):
#	queue.put(j)

#Don't forget to join queues
queue.join()












