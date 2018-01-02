import unittest
import time
import tempfile
import class_api
import xmlrpclib
class XMLRPC_TEST(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        print 'Testing XMLRPC Implementation'
        

        
        global path
        path = tempfile.mkdtemp()
        
        global server
        server = class_api.XMLRPCServer(path)
        server.start('localhost',9000)
        
        global api
        api = xmlrpclib.ServerProxy("http://localhost:9000") 
        time.sleep(5)

    @classmethod
    def tearDownClass(cls):
        import shutil
        import time
        server.stop()
        time.sleep(10)
        try:
            shutil.rmtree(path)
        except:
            pass

    def test_00_delete_standard_subscription(self):
        api.deleteSubscription(api.listSubscriptions()[0]['address'])
        assert len(api.listSubscriptions())==0
        
            
    def test_01_addresses(self):
        api.createRandomAddress('a')
        assert api.listAddresses()[0]['label'] == 'a',api.listAddresses()[0]
        api.createDeterministicAddresses('b')
        assert api.listAddresses()[1]['label'] == 'b',api.listAddresses()[1]
        
        api.deleteAddress(api.listAddresses()[0]['address'])
        api.deleteAddress(api.listAddresses()[0]['address'])
        assert api.listAddresses() == [],api.listAddresses()

    def test_02_subscriptions(self):
        api.addSubscription('a','BM-2D9vJkoGoTBhqMyZyjvELKgBWFMr6iGCQQ')
        assert api.listSubscriptions()[0]['label'] == 'a',api.listSubscriptions()[0]
        api.deleteSubscription(api.listSubscriptions()[0]['address'])
        assert len(api.listSubscriptions()) == 0,api.listSubscriptions()

    def test_03_channels(self):
        api.joinChannel('general')
        assert api.listAddresses()[0]['label'] == '[chan] general',api.listAddresses()[0]
        assert api.listAddressBook()[0]['label'] == '[chan] general',api.listAddressBook()[0]
        api.deleteChannel(api.listAddresses()[0]['address'])
        assert len(api.listAddresses()) == 0 
        assert len(api.listAddressBook()) == 0 
        
    def test_04_manage_addressbook(self):
        api.addToAddressBook('a','a')
        assert api.listAddressBook()[0]['address'] == 'a',api.listContacts()[0]
        count = len(api.listAddressBook())
        api.deleteFromAddressBook('a')
        assert len(api.listAddressBook()) == 0

    def test_05_manage_blackwhitelist(self):
        assert api.getBlackWhitelist() == 'black'
        api.setBlackWhitelist('white')
        assert api.getBlackWhitelist() == 'white'
        api.setBlackWhitelist('black')
        assert api.getBlackWhitelist() == 'black'
        
        api.addToBlacklist('a','a')
        assert api.listBlacklist()[0]['label'] == 'a'
        api.deleteFromBlacklist('a')
        assert api.listBlacklist() == []
        
        api.addToWhitelist('a','a')
        assert api.listWhitelist()[0]['label'] == 'a'
        api.deleteFromWhitelist('a')
        assert api.listWhitelist() == []

    def test_06_send_messages(self):
        addr = api.createRandomAddress('sendtest')
        api.addSubscription('a','BM-2D9vJkoGoTBhqMyZyjvELKgBWFMr6iGCQQ')
        ackdata1 = api.sendMessage(addr,'BM-2D9vJkoGoTBhqMyZyjvELKgBWFMr6iGCQQ','apitest','apitest\nhttps://github.com/merlink01/PyBitAPI')
        ackdata2 = api.sendBroadcast(addr,'apitest','apitest')
        while api.getSentMessageByAckData(ackdata1) == 'notfound':
            pass
        while api.getSentMessageByAckData(ackdata2) == 'notfound':
            pass
            
        assert api.getSentMessageByAckData(ackdata1)[0]['status'] in ['msgqueued', 'broadcastqueued', \
        'broadcastsent', 'doingpubkeypow', 'awaitingpubkey', 'doingmsgpow', 'forcepow', 'msgsent', \
        'msgsentnoackexpected', 'ackreceived'],api.getSentMessageByAckData(ackdata1)
        assert api.getSentMessageByAckData(ackdata2)[0]['status'] in ['msgqueued', 'broadcastqueued', \
        'broadcastsent', 'doingpubkeypow', 'awaitingpubkey', 'doingmsgpow', 'forcepow', 'msgsent', \
        'msgsentnoackexpected', 'ackreceived'],api.getSentMessageByAckData(ackdata2)

    def test_07_manage_sent_messages(self):
        addr = api.createRandomAddress('sendtest')
        ackdata = api.sendMessage(addr,addr,'last','last')
        idnum = api.getSentMessageByAckData(ackdata)[0]['msgid']
        
        assert api.getAllSentMessages() != []
        assert api.getAllSentMessageIDs() != []
        assert api.getSentMessagesBySender(addr) != []
        assert api.getSentMessageByAckData(ackdata) != []
        assert api.getSentMessageByID(idnum) != []
        assert api.getSentMessageStatus(ackdata) in ['msgqueued'],api.getSentMessageStatus(ackdata)

        api.trashSentMessage(idnum)
        messages = api.getAllSentMessages()
        for message in messages:
            assert message['msgid'] != idnum
    #~ 
    def test_08_manage_inbox_messages(self):
        if api.clientStatus()['networkStatus'] == 'notConnected':
            raise IOError,'Not Connected'
        addr = api.createRandomAddress('sendtest')
        counter = 0
        ackdata = api.sendMessage(addr,addr,'test','test')
        while api.getAllInboxMessages() == []:
            if counter > 20:
                ackdata = api.sendMessage(addr,addr,'apitest','apitest\nhttps://github.com/merlink01/PyBitAPI')
            time.sleep(10)
            if api.clientStatus()['networkStatus'] == 'notConnected':
                raise IOError,'Not Connected'
            
        assert api.getAllInboxMessages() != [],api.getAllInboxMessages()
        assert api.getAllInboxMessageIDs() != [],api.getAllInboxMessageIDs()
        
        msgid = api.getAllInboxMessages()[0]['msgid']
        recv = api.getAllInboxMessages()[0]['toAddress']
        assert api.getInboxMessageByID(msgid) != []
        assert api.getInboxMessagesByReceiver(recv) != []
        
        assert api.getInboxMessageByID(msgid)[0]['read'] == 0,api.getInboxMessageByID(msgid)[0]['read']
        api.markInboxMessageAsRead(msgid)
        assert api.getInboxMessageByID(msgid)[0]['read'] == 1,api.getInboxMessageByID(msgid)[0]['read']
        api.markInboxMessageAsUnread(msgid)
        assert api.getInboxMessageByID(msgid)[0]['read'] == 0,api.getInboxMessageByID(msgid)[0]['read']
        
        api.trashInboxMessage(msgid)
        messages = api.getAllInboxMessages()
        for msg in messages:
            assert msg['msgid'] != msgid
        
        api.getAllInboxMessages()
