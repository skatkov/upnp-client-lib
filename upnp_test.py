import unittest
from upnp import *

class TestSequenceFunctions(unittest.TestCase):

	def test_findRequestNotify(self):
		client = upnp(None, None, None)
		data = "NOTIFY * HTTP/1.1\r\nHost:239.255.255.250:1900\r\nCache-Control:max-age=60\r\n"
		data += "Location:http://192.168.1.1:80/upnp/service/descrip.xml\r\nNT:urn:schemas-upnp-org:device:WANConnectionDevice:1\r\n"
		data += "NTS:ssdp:alive\r\nServer:NT/5.0 UPnP/1.0\r\nUSN:uuid:upnp-WANConnectionDevice-1_0-001ee58cab66::urn:schemas-upnp-org:device:WANConnectionDevice:1"

		self.assertTrue(client.findRequest(data, "device", "WANConnectionDevice"))

	def test_findRequestNotifyRequest(self):
		client = upnp(None, None, None)
		data = "NOTIFY * HTTP/1.1\r\nHost:239.255.255.250:1900\r\nCache-Control:max-age=60\r\n"
		data += "Location:http://192.168.1.1:80/upnp/service/descrip.xml\r\nNT:urn:schemas-upnp-org:device:WANConnectionDevice:1\r\n"
		data += "NTS:ssdp:alive\r\nServer:NT/5.0 UPnP/1.0\r\nUSN:uuid:upnp-WANConnectionDevice-1_0-001ee58cab66::urn:schemas-upnp-org:device:WANConnectionDevice:1"

		client.findRequest(data, "device", "WANConnectionDevice")	
		
		self.assertEqual(client.upnpRequest['location'], "http://192.168.1.1:80/upnp/service/descrip.xml")
		self.assertEqual(client.upnpRequest['host'], '239.255.255.250:1900' )
		self.assertEqual(client.upnpRequest['server'], 'NT/5.0 UPnP/1.0')

	def test_findRequestFalse(self):
		client = upnp(None, None, None)
		data = "NOTIFY * HTTP/1.1\r\nHost:239.255.255.250:1900\r\nCache-Control:max-age=60\r\n"
		data += "Location:http://192.168.1.1:80/upnp/service/descrip.xml\r\nNT:urn:schemas-upnp-org:device:WANConnectionDevice:1\r\n"
		data += "NTS:ssdp:alive\r\nServer:NT/5.0 UPnP/1.0\r\nUSN:uuid:upnp-WANConnectionDevice-1_0-001ee58cab66::urn:schemas-upnp-org:device:WANConnectionDevice:1"

		self.assertFalse(client.findRequest(data, "device", "test"))

	def test_findNotificationTmApplicationServer(self):
		client = upnp(None, None, None)
		data = "NOTIFY * HTTP/1.1\r\nCache-control: max-age=1800\r\nHost: 239.255.255.250:1900\r\n"
		data += "Usn: uuid:547af669-7984-6c6a-0000-00000bcfbcb2::urn:schemas-upnp-org:service:TmApplicationServer:1\r\n"
		data += "Location: http://192.168.1.101:53712/dev/547af669-7984-6c6a-0000-00000bcfbcb2/desc.xml\r\n"
		data += "Nt: urn:schemas-upnp-org:service:TmApplicationServer:1\r\nNts: ssdp:alive\r\nServer: Linux/2.6.35.10-gd2564fb UPnP/1.0 4thLine-Cling/1.1\r\n"

		self.assertTrue(client.findRequest(data, "service", "TmApplicationServer"))

	def test_findNotificationTmServerDevice(self):
		client = upnp(None, None, None)
		data = "NOTIFY * HTTP/1.1\r\nCache-control: max-age=1800\r\nHost: 239.255.255.250:1900\r\n"
		data += "Usn: uuid:547af669-7984-6c6a-0000-00000bcfbcb2::urn:schemas-upnp-org:device:TmServerDevice:1\r\n"
		data += "Location: http://192.168.1.101:53712/dev/547af669-7984-6c6a-0000-00000bcfbcb2/desc.xml\r\nNt: urn:schemas-upnp-org:device:TmServerDevice:1\r\n"
		data += "Nts: ssdp:alive\r\nServer: Linux/2.6.35.10-gd2564fb UPnP/1.0 4thLine-Cling/1.1\r\n"

		self.assertTrue(client.findRequest(data, "device",  "TmServerDevice"))

	def test_findNotificationTmClientProfile(self):
		client = upnp(None, None, None)
		data = "NOTIFY * HTTP/1.1\r\nCache-control: max-age=1800\r\nHost: 239.255.255.250:1900\r\nUsn: uuid:547af669-7984-6c6a-0000-00000bcfbcb2::urn:schemas-upnp-org:service:TmClientProfile:1\r\n"
		data += "Location: http://192.168.1.101:53712/dev/547af669-7984-6c6a-0000-00000bcfbcb2/desc.xml\r\nNt: urn:schemas-upnp-org:service:TmClientProfile:1\r\n"
		data += " Nts: ssdp:alive\r\nServer: Linux/2.6.35.10-gd2564fb UPnP/1.0 4thLine-Cling/1.1\r\n"

		self.assertTrue(client.findRequest(data, "service", "TmClientProfile"))		

	def test_getTypeAndName(self):
		client = upnp(None, None, None)
		
		self.assertEqual(client.getTypeAndName("urn:schemas-upnp-org:device:WANConnectionDevice:1"), ("device", "WANConnectionDevice") )

	def test_findRequestMsearch(self):
		client = upnp(None, None, None)
		data = "M-SEARCH * HTTP/1.1\r\nHost:239.255.255.250:1900\r\n"
		
		self.assertFalse(client.findRequest(data, None, None))

	def test_buildMsearchRequest(self):
		client = upnp(None, None, None)		
		MsearchRequest = "M-SEARCH * HTTP/1.1\r\nHOST:239.255.255.250:1900\r\nST:urn:schemas-upnp-org:device:test:1"		
		
		self.assertTrue(client.buildMsearchRequest("device", "test").startswith(MsearchRequest)) 

	def test_findRequestMsearch(self):
		client = upnp(None, None, None)
		data = "M-SEARCH * HTTP/1.1\r\nHost:239.255.255.250:1900\r\nCache-Control:max-age=60\r\n"
		data += "Location:http://192.168.1.1:80/upnp/service/descrip.xml\r\nNT:urn:schemas-upnp-org:device:WANConnectionDevice:1\r\n"
		data += "NTS:ssdp:alive\r\nServer:NT/5.0 UPnP/1.0\r\nUSN:uuid:upnp-WANConnectionDevice-1_0-001ee58cab66::urn:schemas-upnp-org:device:WANConnectionDevice:1"

		self.assertFalse(client.findRequest(data, "device", "WANConnectionDevice"))

if __name__ == '__main__':
    unittest.main()