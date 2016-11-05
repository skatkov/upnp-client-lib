import sys
import struct
import IN
from socket import *


class upnp():
	mreq = None
	port = None
	msearchHeaders = {
		'MAN' : '"ssdp:discover"',
		'MX'  : '1'
	}
	DEFAULT_IP = "239.255.255.250"
	DEFAULT_PORT = 1900
	DEFAULT_domainName = "schemas-upnp-org"	
	UPNP_VERSION = '1.0'
	IFACE = None
	csock = None
	ssock = None
	VERBOSE = False
	UNIQ = True	
	
	upnpRequest = {
			"location": None,
			"server": None,
			"host" : None,
			"NT" : None,  
			"urn": None
	}


	def __init__(self, ip, port, iface):
		if self.initSockets(ip,port,iface) == False:
			print 'UPNP class initialization failed!'
			sys.exit(1)

	
	def initSockets(self,ip,port,iface):
		#protective closing of code
		if self.csock:
			self.csock.close()
		if self.ssock:
			self.ssock.close()

		if iface != None:
			self.IFACE = iface
		if not ip:
                	ip = self.DEFAULT_IP
                if not port:
                	port = self.DEFAULT_PORT
                self.port = port
                self.ip = ip

		try:
			#This is needed to join a multicast group
			#FIXME: failed to join multicast group if localare connection is gone.
			self.mreq = struct.pack("4sl",inet_aton(ip),INADDR_ANY)

			#Set up client socket
			self.csock = socket(AF_INET,SOCK_DGRAM)
			self.csock.setsockopt(IPPROTO_IP,IP_MULTICAST_TTL,2)
			
			#Set up server socket
			self.ssock = socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
			self.ssock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
			
			#Only bind to this interface
			if self.IFACE != None:
				print '\nBinding to interface',self.IFACE,'...\n'
				self.ssock.setsockopt(SOL_SOCKET,IN.SO_BINDTODEVICE,struct.pack("%ds" % (len(self.IFACE)+1,), self.IFACE))
				self.csock.setsockopt(SOL_SOCKET,IN.SO_BINDTODEVICE,struct.pack("%ds" % (len(self.IFACE)+1,), self.IFACE))

			try:
				self.ssock.bind(('',self.port))
			except Exception, e:
				print "WARNING: Failed to bind %s:%d: %s" , (self.ip,self.port,e)
			try:
				self.ssock.setsockopt(IPPROTO_IP,IP_ADD_MEMBERSHIP,self.mreq)
			except Exception, e:
				print 'WARNING: Failed to join multicast group:',e
		except Exception, e:
			print "Failed to initialize UPNP sockets:",e
			return False
		return True

	def createNewListener(self,ip,port):
		try:
			newsock = socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP)
			newsock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
			newsock.bind((ip,port))
			return newsock
		except:
			return False

	#Listen for network data
	def listen(self,size,socket):
		if socket == False:
			socket = self.ssock
		try:
			return socket.recv(size)
		except:
			return False

	#Send network data
	def send(self,data,socket):
		#By default, use the client socket that's part of this class
		if socket == False:
			socket = self.csock
		try:
			socket.sendto(data,(self.ip,self.port))
			return True
		except Exception, e:
			print "SendTo method failed for %s:%d : %s" % (self.ip,self.port,e)
			return False

	def parseHeader(self,data,header):
		delimiter = "%s:" % header
		defaultRet = False

		lowerDelim = delimiter.lower()
		dataArray = data.split("\r\n")
	
		#Loop through each line of the headers
		for line in dataArray:
			lowerLine = line.lower()
			#Does this line start with the header we're looking for?
			if lowerLine.startswith(lowerDelim):
				try:
					return line.split(':',1)[1].strip()
				except:
					print "Failure parsing header data for %s" % header
		return defaultRet

	#Build request query
	def buildMsearchRequest(self, searchType, searchName):
		st = "urn:%s:%s:%s:%s" % (self.DEFAULT_domainName,searchType,searchName,self.UPNP_VERSION.split('.')[0])
		
		request = 	"M-SEARCH * HTTP/1.1\r\n"\
				"HOST:%s:%d\r\n"\
				"ST:%s\r\n" % (self.ip,self.port,st)
		for header,value in self.msearchHeaders.iteritems():
				request += header + ':' + value + "\r\n"	
		request += "\r\n" 
		
		return request

	def getTypeAndName(self, strUrn):
		try:		
			return (strUrn.split(":")[2], strUrn.split(":")[3])
		except:
			#it's rootdevice as i understand
			return (None, None)

	#Find approriate Upnp device
	def findRequest(self, data, searchType, searchName):		
		returnVal = False
		knownHeaders = {				
				'HTTP/1.1 200 OK' : 'reply',
				'NOTIFY' : 'notification'
				#'M-SEARCH' : "search"
		}

		#get message type
		for text,messageType in knownHeaders.iteritems():			
			if data.upper().startswith(text):
				#we found it!
				break
			else:
				messageType = False				

		if messageType != False:			

			actualType, actualName = self.getTypeAndName(self.parseHeader(data, "ST"))
			
			if (actualType == searchType) & (actualName == searchName):
				#collect all the data
				for dataType in self.upnpRequest.iterkeys():				
					self.upnpRequest[dataType] = self.parseHeader(data,dataType.upper())
				returnVal = True


		return returnVal

	#Actively search for UPNP devices
	def msearch(self,searchType,searchName):	
		print "Entering active search"	
		myip = '' #should be localhost
			
		#Have to create a new socket since replies will be sent directly to our IP, not the multicast IP
		server = self.createNewListener(myip,self.port)
		if server == False:
			print 'Failed to bind port %d' % self.port
			return

		self.send(self.buildMsearchRequest(searchType, searchName),server)
		
		while True:			
			if self.findRequest(self.listen(1024,server), searchType, searchName): return True





	#Passively listen for UPNP NOTIFY packets
	def pcap(self, searchType, searchName):
		print 'Entering passive search mode'

		myip = '' #should be localhost
			
		#Have to create a new socket since replies will be sent directly to our IP, not the multicast IP
		server = self.createNewListener(myip,self.port)
		if server == False:
			print 'Failed to bind port %d' % self.port
			return

		while True:			
			if self.findRequest(self.listen(1024, server), searchType, searchName): return True
	
