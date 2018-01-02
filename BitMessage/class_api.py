import os
import sys
import time
import json
import threading
import logging
from SimpleXMLRPCServer import SimpleXMLRPCServer

import addresses
import cmd
import datetime
import signal
from  pyelliptic import openssl
import helper_sent
import helper_inbox

###############
import parallelTestModule

if __name__ ==  '__main__':
  extractor = parallelTestModule.ParallelExtractor()
  extractor.runInParallel(numProcesses=2, numThreads=4)
###############  

SUPPORTED_VERSIONS = ['0.4.1']

logger = logging.getLogger('class_api')

#A hack to let pybitmessage source directory exist as Subdir for testing
if os.path.exists(os.path.abspath('PyBitmessage')):
    sys.path.append(os.path.abspath('PyBitmessage/src'))


class APIError(Exception):
    def __init__(self, error_message):
        self.error_message = error_message
    def __str__(self):
        return "API Error: %s" % self.error_message

def getAPI(workingdir=None,silent=False):
    
    if workingdir:
        os.environ["BITMESSAGE_HOME"] = workingdir
    
    #Workaround while logging is not completed 
    if silent:
        import StringIO
        fobj = StringIO.StringIO()
        sys.stdout = fobj    
        
    import bitmessagemain
    
    version = bitmessagemain.shared.softwareVersion
    if not version in SUPPORTED_VERSIONS:
        sys.stderr.write('Bitmessage Vesion %s is not Supported officially.\n'%version)
    print "Hello"
    if version == '0.4.1':
        global ADDRESSVERSION
        ADDRESSVERSION = 4
    else:
        ADDRESSVERSION = 4
        
    class MainAPI(bitmessagemain.Main):
        def _close_and_wait(self):
            
            """For Testing purposes only"""
            
            self.stop()
            while 1:
                import time
                time.sleep(2)
                print self._count_threads()
                bitmessagemain.shared.shutdown = 1
                
            
        def _count_threads(self):

            """This function counts running Threads"""

            thcount = 0
            threads = threading.enumerate()
            for th in threads:
                if th.is_alive():
                    print th
                    thcount += 1
            return thcount

        def addToAddressBook(self, label, address):

            '''Add a Conact to the Addressbook
            Usage: api.addContact(label,bmaddress)'''

            unicode(label, 'utf-8')
            queryreturn = bitmessagemain.shared.sqlQuery('''select * from addressbook where address=?''',address)
            if queryreturn != []:
                raise APIError('Given Address is already inside: %s'%address)
            queryreturn = bitmessagemain.shared.sqlExecute('''INSERT INTO addressbook VALUES (?,?)''',label, address)
            return True

        def addSubscription(self, label, address):
            
            '''Add a Subscription
            Usage: api.addSubscription(label,bmaddressl)'''
            
            logger.info('Label: %s Address: %s'%(label, address))
            unicode(label, 'utf-8')
            address = addresses.addBMIfNotPresent(address)
            status, addressVersionNumber, streamNumber, toRipe = addresses.decodeAddress(address)
            if status != 'success':
                raise APIError('Address Error: %s , %s'%(address,status))
            # First we must check to see if the address is already in the
            # subscriptions list.
            queryreturn = bitmessagemain.shared.sqlQuery('''select * from subscriptions where address=?''',address)
            if queryreturn != []:
                raise APIError('AlreadySubscribedError')
            bitmessagemain.shared.sqlExecute('''INSERT INTO subscriptions VALUES (?,?,?)''',label, address, True)
            bitmessagemain.shared.reloadBroadcastSendersForWhichImWatching()
            return True


        def addToBlacklist(self, label, address, enabled=True):
            
            '''Add a Bitmessage Address to the Blacklist
            Usage: api.addToBlacklist(label,bmaddress,enabled[True,False])'''
            
            logger.info('Label: %s Address: %s Enabled: %s'%(label, address, enabled))
            unicode(label, 'utf-8')
            bitmessagemain.shared.sqlExecute('''INSERT INTO blacklist VALUES (?,?,?)''',label,address,enabled)
            return True


        def addToWhitelist(self, label, address, enabled=True):
            
            '''Add a Bitmessage Address to the Whitelist
            Usage: api.addToBlacklist(label,bmaddress,enabled[True,False])'''
            
            logger.info('Label: %s Address: %s Enabled: %s'%(label, address, enabled))
            unicode(label, 'utf-8')
            bitmessagemain.shared.sqlExecute('''INSERT INTO whitelist VALUES (?,?,?)''',label,address,enabled)
            return True


        def clientStatus(self):
            
            '''Returns the Status of the Bitmessage Daemon
            Usage: status = api.clinetStatus()
            print status['externalIPAddress']
            print status['networkConnections']
            print status['numberOfMessagesProcessed']
            print status['numberOfBroadcastsProcessed']
            print status['numberOfPubkeysProcessed']
            print status['networkStatus']
            '''
            
            if len(bitmessagemain.shared.connectedHostsList) == 0:
                networkStatus = 'notConnected'
            elif len(bitmessagemain.shared.connectedHostsList) > 0 and not bitmessagemain.shared.clientHasReceivedIncomingConnections:
                networkStatus = 'connectedButHaveNotReceivedIncomingConnections'
            else:
                networkStatus = 'connectedAndReceivingIncomingConnections'
            info = {}
            try:
                info['externalIPAddress'] = bitmessagemain.shared.myExternalIP
            except:
                info['externalIPAddress'] = 'Not implemented jet'
            info['networkConnections'] = len(bitmessagemain.shared.connectedHostsList)
            info['numberOfMessagesProcessed'] = bitmessagemain.shared.numberOfMessagesProcessed
            info['numberOfBroadcastsProcessed'] = bitmessagemain.shared.numberOfBroadcastsProcessed
            info['numberOfPubkeysProcessed'] = bitmessagemain.shared.numberOfPubkeysProcessed
            info['networkStatus'] = networkStatus
            logger.debug('Status: %s'%info)
            return info

        def createDeterministicAddresses(self,passphrase,label='',numberOfAddresses=1,eighteenByteRipe=False,totalDifficulty=1,smallMessageDifficulty=1,streamNumberForAddress=1):
            
            '''Creates a Deterministic Bitmessage Address (an Address based on a password)
            Usage: api.createDeterministicAddresses(passphrase,label,numberOfAddresses,eighteenByteRipe,totalDifficulty,smallMessageDifficulty)'''
            
            logger.debug('Passphrase: %s Label: %s'%(passphrase,label))
            if len(passphrase) == 0:
                raise APIError('The specified passphrase is blank.')
            
            if not isinstance(eighteenByteRipe, bool):
                raise APIError('Bool expected in eighteenByteRipe, got %s instead' % type(eighteenByteRipe))
            
            if streamNumberForAddress != 1:
                raise APIError('Only Stream Number 1 is Supported jet. Got: %s' % streamNumberForAddress)
            
            if numberOfAddresses == 0:
                raise APIError('Why do you want to create 0 Addresses.')
            
            if numberOfAddresses > 999:
                raise APIError('You have (accidentally?) specified too many addresses to make. Maximum 999. \
                This check only exists to prevent mischief; if you really want to create more addresses than this, \
                contact the Bitmessage developers and we can modify the check or you can do it yourself by \
                searching the source code for this message.')

            if not label:
                label = passphrase

            label = unicode(label, 'utf-8')
            nonceTrialsPerByte = int(bitmessagemain.shared.networkDefaultProofOfWorkNonceTrialsPerByte * totalDifficulty)
            payloadLengthExtraBytes = int(bitmessagemain.shared.networkDefaultPayloadLengthExtraBytes * smallMessageDifficulty)
            bitmessagemain.shared.apiAddressGeneratorReturnQueue.queue.clear()
            bitmessagemain.shared.addressGeneratorQueue.put(
                ('createDeterministicAddresses', ADDRESSVERSION, streamNumberForAddress,
                 label, numberOfAddresses, passphrase, eighteenByteRipe, nonceTrialsPerByte, payloadLengthExtraBytes))
            queueReturn = bitmessagemain.shared.apiAddressGeneratorReturnQueue.get()
            return queueReturn

        def createRandomAddress(self,label,eighteenByteRipe=False,totalDifficulty=1,smallMessageDifficulty=1,streamNumberForAddress=1):

            '''Create a reandom Bitmessage Address
            Usage: api.createRandomAddress(label,eighteenByteRipe,totalDifficulty,smallMessageDifficulty)'''

            if not isinstance(eighteenByteRipe, bool):
                raise APIError('Bool expected in eighteenByteRipe, got %s instead' % type(eighteenByteRipe))
            
            if streamNumberForAddress != 1:
                raise APIError('Only Stream Number 1 is Supported jet. Got: %s' % streamNumberForAddress)
                
            unicode(label, 'utf-8')
            nonceTrialsPerByte = int(bitmessagemain.shared.networkDefaultProofOfWorkNonceTrialsPerByte * totalDifficulty)
            payloadLengthExtraBytes = int(bitmessagemain.shared.networkDefaultPayloadLengthExtraBytes * smallMessageDifficulty)
            bitmessagemain.shared.apiAddressGeneratorReturnQueue.queue.clear()
            bitmessagemain.shared.addressGeneratorQueue.put((
                'createRandomAddress', ADDRESSVERSION, streamNumberForAddress, label, 1, "", eighteenByteRipe, nonceTrialsPerByte, payloadLengthExtraBytes))
            return bitmessagemain.shared.apiAddressGeneratorReturnQueue.get()

        def deleteAddress(self,address):

            status, addressVersionNumber, streamNumber, toRipe = self._verifyAddress(address)
            address = addresses.addBMIfNotPresent(address)
            if not bitmessagemain.shared.config.has_section(address):
                raise APIError('Could not find this address in your keys.dat file.')

            bitmessagemain.shared.config.remove_section(address)
            with open(bitmessagemain.shared.appdata + 'keys.dat', 'wb') as configfile:
                bitmessagemain.shared.config.write(configfile)
            
            bitmessagemain.shared.reloadMyAddressHashes()
            return True

        def deleteChannel(self,address):
            self.deleteAddress(address)
            self.deleteFromAddressBook(address)
            return True
            
        def deleteFromAddressBook(self,address):

            '''Delete a Contact from Address Book
            Usage: api.deleteContact(bmaddress)'''

            queryreturn = bitmessagemain.shared.sqlExecute('''delete from addressbook where address=?''',address)
            return True

        def deleteFromBlacklist(self,address):
            
            '''Delete a Contact from Blacklist
            Usage: api.deleteFromBlacklist(bmaddress)'''
            
            bitmessagemain.shared.sqlExecute('''delete from blacklist where address=?''',address)
            return True
            
        def deleteFromWhitelist(self,address):
            
            '''Delete a Contact from Whitelist
            Usage: api.deleteFromWhitelist(bmaddress)'''
            
            bitmessagemain.shared.sqlExecute('''delete from whitelist where address=?''',address)
            return True

        def deleteSubscription(self,address):

            '''Delete a Subscription
            Usage: api.deleteSubscription(bmaddress)'''
            
            address = addresses.addBMIfNotPresent(address)
            bitmessagemain.shared.sqlExecute('''DELETE FROM subscriptions WHERE address=?''',address)
            bitmessagemain.shared.reloadBroadcastSendersForWhichImWatching()
            return True

        def getAllInboxMessageIDs(self):
            
            '''Get a List of IDs of all Inbox Messages
            Usage: api.getAllInboxMessageIDs()'''
            
            queryreturn = bitmessagemain.shared.sqlQuery('''SELECT msgid FROM inbox where folder='inbox' ORDER BY received''')
            data = []
            for msgid in queryreturn:
                data.append(msgid[0].encode('hex'))
            return data
            
        def getAllInboxMessages(self):
            
            '''Return a List of all Inbox Messages
            Usage: api.getAllInboxMessages()'''
            
            queryreturn = bitmessagemain.shared.sqlQuery('''SELECT msgid, toaddress, fromaddress, subject, received, message, encodingtype, read FROM inbox where folder='inbox' ORDER BY received''')
            messages = []
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, received, message, encodingtype, read = row
                subject = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(subject)
                message = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(message)
                messages.append({'msgid': msgid.encode('hex'),'toAddress': toAddress, 'fromAddress': fromAddress, 'subject': subject, 'message': message, 'encodingType': encodingtype, 'receivedTime': received, 'read': read})
            return messages
            
        def getAllSentMessageIDs(self):
            
            '''Get a List of IDs of all Outbox Messages
            Usage: getAllSentMessageIDs()'''
            
            queryreturn = bitmessagemain.shared.sqlQuery('''SELECT msgid FROM sent where folder='sent' ORDER BY lastactiontime''')
            data = []
            for row in queryreturn:
                msgid = row[0]
                data.append(msgid.encode('hex'))
            return data
            
        def getAllSentMessages(self):
            
            '''Get a List of all Outbox Messages
            Usage: api.getAllSentMessages()'''
            
            queryreturn = bitmessagemain.shared.sqlQuery('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent where folder='sent' ORDER BY lastactiontime''')
            data = []
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, lastactiontime, message, encodingtype, status, ackdata = row
                subject = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(subject)
                message = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(message)
                data.append({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject, 'message':message, 'encodingType':encodingtype, 'lastActionTime':lastactiontime, 'status':status, 'ackData':ackdata.encode('hex')})
            return data
            
        def getBlackWhitelist(self):
            
            '''Returns the Black- or Whitelist Configuration
            usage: print api.getBlackWhitelist'''
            
            return bitmessagemain.shared.config.get('bitmessagesettings', 'blackwhitelist')
            
        def getDeterministicAddress(self,passphrase):
            
            '''Returns a Deterministic Address for a give Passphrase
            Usage: api.getDeterministicAddress()'''
            
            #hardcoded in correct version and stream number, because they shouldn't be changed until now
            streamNumberForAddress = 1
            streamNumber=1
            numberOfAddresses = 1
            eighteenByteRipe = False
            bitmessagemain.shared.addressGeneratorQueue.put(
                ('getDeterministicAddress', ADDRESSVERSION,
                 streamNumber, 'unused API address', numberOfAddresses, passphrase, eighteenByteRipe))
            return bitmessagemain.shared.apiAddressGeneratorReturnQueue.get()
            
        def getInboxMessageByID(self, msgid):

            '''Return an Inbox Message by a given ID
            Usage: print api.getInboxMessageByID(MessageID)'''

            msgid = msgid.decode('hex')
            queryreturn = bitmessagemain.shared.sqlQuery('''SELECT msgid, toaddress, fromaddress, subject, received, message, encodingtype, read FROM inbox WHERE msgid=?''',msgid)
            data = []
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, received, message, encodingtype, read = row
                subject = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(subject)
                message = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(message)
                data.append({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject, 'message':message, 'encodingType':encodingtype, 'receivedTime':received, 'read': read})
            return data
            
        def getInboxMessagesByReceiver(self,toAddress):
            
            '''Return an Inbox Message by a given Sender Address
            Usage: print api.getInboxMessagesByReceiver(SenderAddress)'''
            
            queryreturn = bitmessagemain.shared.sqlQuery('''SELECT msgid, toaddress, fromaddress, subject, received, message, encodingtype FROM inbox WHERE folder='inbox' AND toAddress=?''',toAddress)
            data = []
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, received, message, encodingtype = row
                subject = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(subject)
                message = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(message)
                data .append({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject.encode('base64'), 'message':message.encode('base64'), 'encodingType':encodingtype, 'receivedTime':received})
            return data
            
        def getSentMessageByAckData(self,ackData):
            
            '''Return an Inbox Message by a AckData
            Usage: print api.getSentMessageByAckData(AckData)'''
            
            ackData = ackData.decode('hex')
            queryreturn = bitmessagemain.shared.sqlQuery('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent WHERE ackdata=?''',ackData)
            data = []
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, lastactiontime, message, encodingtype, status, ackdata = row
                subject = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(subject)
                message = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(message)
                data.append({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject, 'message':message, 'encodingType':encodingtype, 'lastActionTime':lastactiontime, 'status':status, 'ackData':ackdata.encode('hex')})
            return data
            
        def getSentMessageByID(self,msgid):

            '''Return an Outbox Message by a given ID
            Usage: print api.getSentMessageByID(MessageID)'''

            msgid = msgid.decode('hex')
            queryreturn = bitmessagemain.shared.sqlQuery('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent WHERE msgid=?''',msgid)
            data = []
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, lastactiontime, message, encodingtype, status, ackdata = row
                subject = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(subject)
                message = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(message)
                data.append({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject.encode('base64'), 'message':message.encode('base64'), 'encodingType':encodingtype, 'lastActionTime':lastactiontime, 'status':status, 'ackData':ackdata.encode('hex')})
            return data
            
        def getSentMessageStatus(self,ackdata):
            
            '''Returns the Status of an Outbox Message by AckData
            Usage: print api.getSentMessageStatus(AckData)'''

            ackdata = ackdata.decode('hex')
            queryreturn = bitmessagemain.shared.sqlQuery('''SELECT status FROM sent where ackdata=?''',ackdata)
            if queryreturn == []:
                return 'notfound'
            for row in queryreturn:
                status, = row
                return status
                
        def getSentMessagesBySender(self, fromAddress):

            '''Return a List of Message by a given Send Address
            Usage: print api.getSentMessagesBySender(SendAddress)'''

            queryreturn = bitmessagemain.shared.sqlQuery('''SELECT msgid, toaddress, fromaddress, subject, lastactiontime, message, encodingtype, status, ackdata FROM sent WHERE folder='sent' AND fromAddress=? ORDER BY lastactiontime''',fromAddress)
            data = []
            for row in queryreturn:
                msgid, toAddress, fromAddress, subject, lastactiontime, message, encodingtype, status, ackdata = row
                subject = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(subject)
                message = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(message)
                data.append({'msgid':msgid.encode('hex'), 'toAddress':toAddress, 'fromAddress':fromAddress, 'subject':subject, 'message':message, 'encodingType':encodingtype, 'lastActionTime':lastactiontime, 'status':status, 'ackData':ackdata.encode('hex')})
            return data
            
        def joinChannel(self, label, testaddress=None):

            '''Join a Channel by a Given Name or Password
            api.joinChannel(label,testaddress[Only for Testing if the Name is correct])'''

            str_chan = '[chan]'
            
            #Precheck Address Book
            queryreturn = bitmessagemain.shared.sqlQuery('''select * from addressbook where label=?''',str_chan + ' ' + label)
            if queryreturn != []:
                raise APIError('Channel already in Addressbook: %s'%label)
            
            #Add Channel to Own Addresses
            bitmessagemain.shared.apiAddressGeneratorReturnQueue.queue.clear()
            bitmessagemain.shared.addressGeneratorQueue.put(('createChan', 4, 1, str_chan + ' ' + label ,label))
            addressGeneratorReturnValue = bitmessagemain.shared.apiAddressGeneratorReturnQueue.get()

            if len(addressGeneratorReturnValue) == 0:
                raise APIError('The Channel is already in use: %s'%label)
                
            address = addressGeneratorReturnValue[0]
            if testaddress:
                if str(address) != str(testaddress):
                    raise APIError('The entered address does not match the address generated by the label')
                    
            #Precheck Address Book
            queryreturn = bitmessagemain.shared.sqlQuery('''select * from addressbook where label=?''',address)
            if queryreturn != []:
                raise APIError('Channel already in Addressbook: %s'%label)
                    
            #Add Address to Address Book
            bitmessagemain.shared.sqlExecute('''INSERT INTO addressbook VALUES (?,?)''',str_chan + ' ' + label, address)
            return address
            
        def listAddresses(self):

            '''List own Addresses
            Usage: print api.listAddresses()'''

            address1 = []
            configSections = bitmessagemain.shared.config.sections()
            for addressInKeysFile in configSections:
                if addressInKeysFile != 'bitmessagesettings':
                    status, addressVersionNumber, streamNumber, hash = addresses.decodeAddress(addressInKeysFile)
                    address1.append({'label': bitmessagemain.shared.config.get(addressInKeysFile, 'label'), 'address': addressInKeysFile, 'stream':streamNumber, 'enabled': bitmessagemain.shared.config.getboolean(addressInKeysFile, 'enabled')})
            return address1
            
        def listBlacklist(self):
            
            '''List all Blacklist Entries
            Usage: print api.listBlacklist()'''
            
            queryreturn = bitmessagemain.shared.sqlQuery('''select * from blacklist''')
            data = []
            for row in queryreturn:
                label, address, enabled = row
                label = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(label)
                data.append({'label':label, 'address': address, 'enabled': bool(enabled)})
            return data
            
        def listAddressBook(self):
            
            '''List the Address Book
            Usage: print api.listContacts()'''
            
            queryreturn = bitmessagemain.shared.sqlQuery('''select * from addressbook''')
            data = []
            for row in queryreturn:
                label, address = row
                label = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(label)
                data.append({'label':label, 'address': address})
            return data
            
        def listSubscriptions(self):
            
            '''List the all Subscriptions
            Usage: print api.listSubscriptions()'''
            
            queryreturn = bitmessagemain.shared.sqlQuery('''SELECT label, address, enabled FROM subscriptions''')
            data = []
            for row in queryreturn:
                label, address, enabled = row
                label = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(label)
                data.append({'label':label, 'address': address, 'enabled': enabled})
            return data
            
        def listWhitelist(self):
            
            '''List all Whitelist Entries
            Usage: print api.listBlacklist()'''
            
            queryreturn = bitmessagemain.shared.sqlQuery('''select * from whitelist''')
            data = []
            for row in queryreturn:
                label, address, enabled = row
                label = bitmessagemain.shared.fixPotentiallyInvalidUTF8Data(label)
                data.append({'label':label, 'address': address, 'enabled': bool(enabled)})
            return data
            
        def markInboxMessageAsRead(self,msgid):
            
            '''Mark an Inbox Message as read
            Usage: api.markInboxMessageAsRead()'''
            
            msgid = msgid.decode('hex')
            bitmessagemain.shared.sqlExecute('''UPDATE inbox SET read='1' WHERE msgid=?''', msgid) 
            return True
            
            
        def markInboxMessageAsUnread(self,msgid):
            
            '''Mark an Inbox Message as unread
            Usage: api.markInboxMessageAsUnread()'''
            
            msgid = msgid.decode('hex')
            bitmessagemain.shared.sqlExecute('''UPDATE inbox SET read='0' WHERE msgid=?''', msgid)
            return True

        def sendBroadcast(self,fromAddress,subject,message):
            
            '''Send a Broadcast to a given Address
            Usage: api.sendBroadcast(BmAddress, Subject, Message)'''
            
            #Hardcoded Encoding Type, no othe supported jet
            encodingType = 2
            
            status, addressVersionNumber, streamNumber, toRipe = addresses.decodeAddress(fromAddress)
            fromAddress = addresses.addBMIfNotPresent(fromAddress)
            try:
                fromAddressEnabled = bitmessagemain.shared.config.getboolean(fromAddress, 'enabled')
            except:
                return (fromAddress,'fromAddressNotPresentError')
            if not fromAddressEnabled:
                return (fromAddress,'fromAddressDisabledError')
            ackdata = openssl._OpenSSL.rand(32)
            toAddress = '[Broadcast subscribers]'
            ripe = ''
            t = ('', toAddress, ripe, fromAddress, subject, message, ackdata, int(
                time.time()), 'broadcastqueued', 1, 1, 'sent', 2)
            helper_sent.insert(t)
            toLabel = '[Broadcast subscribers]'
            bitmessagemain.shared.workerQueue.put(('sendbroadcast', ''))
            return ackdata.encode('hex')
            
        def sendMessage(self, fromAddress, toAddress, subject, message):
            
            '''Send a Message to a given Address or Channel
            Usage: api.sendBroadcast(OwnAddress, TargetAddress, Subject, Message)'''
            
            #Hardcoded Encoding Type, no othe supported jet
            encodingType = 2
            
            status, addressVersionNumber, streamNumber, toRipe = addresses.decodeAddress(toAddress)
            if status != 'success':
                with bitmessagemain.shared.printLock:
                    print 'ToAddress Error: %s , %s'%(toAddress,status)
                return (toAddress,status)
            status, addressVersionNumber, streamNumber, fromRipe = addresses.decodeAddress(fromAddress)
            if status != 'success':
                with bitmessagemain.shared.printLock:
                    print 'fromAddress Error: %s , %s'%(fromAddress,status)
                return (fromAddress,status)
            toAddress = addresses.addBMIfNotPresent(toAddress)
            fromAddress = addresses.addBMIfNotPresent(fromAddress)
            try:
                fromAddressEnabled = bitmessagemain.shared.config.getboolean(fromAddress, 'enabled')
            except:
                return (fromAddress,'fromAddressNotPresentError')
            if not fromAddressEnabled:
                return (fromAddress,'fromAddressDisabledError')
            ackdata = openssl.OpenSSL.rand(32)
            t = ('', toAddress, toRipe, fromAddress, subject, message, ackdata, int(
                time.time()), 'msgqueued', 1, 1, 'sent', 2)
            helper_sent.insert(t)
            toLabel = ''
            queryreturn = bitmessagemain.shared.sqlQuery('''select label from addressbook where address=?''',toAddress)
            if queryreturn != []:
                for row in queryreturn:
                    toLabel, = row
            bitmessagemain.shared.UISignalQueue.put(('displayNewSentMessage', (
                toAddress, toLabel, fromAddress, subject, message, ackdata)))
            bitmessagemain.shared.workerQueue.put(('sendmessage', toAddress))
            return ackdata.encode('hex')
            
        def setBlackWhitelist(self, value):
            
            '''Changes the Settings to Black- or Whitelist
            Usage: api.setBlackWhitelist('black' or 'white')'''
            
            if value not in ['black','white']:
                raise APIError('WrongValueGivenError:%s'%value)

            bitmessagemain.shared.config.set('bitmessagesettings', 'blackwhitelist', value)
            return True
            
        def trashInboxMessage(self,msgid):
            
            '''Trash a Message from Inbox by a given ID
            Usage: api.trashInboxMessage(MessageID)'''

            msgid = msgid.decode('hex')
            helper_inbox.trash(msgid)
            return True
            
        def trashSentMessage(self,msgid):

            '''Trash a Message from Outbox by a given ID
            Usage: api.trashSentMessage(MessageID)'''

            msgid = msgid.decode('hex')
            bitmessagemain.shared.sqlExecute('''UPDATE sent SET folder='trash' WHERE msgid=?''',msgid)
            return True
            
        def _verifyAddress(self, address):
            status, addressVersionNumber, streamNumber, ripe = addresses.decodeAddress(address)
            if status != 'success':
                logger.warn('API Error 0007: Could not decode address %s. Status: %s.', address, status)

                if status == 'checksumfailed':
                    raise APIError('Checksum failed for address: ' + address)
                if status == 'invalidcharacters':
                    raise APIError('Invalid characters in address: ' + address)
                if status == 'versiontoohigh':
                    raise APIError('Address version number too high (or zero) in address: ' + address)
                raise APIError('Could not decode address: ' + address + ' : ' + status)
            if addressVersionNumber < 2 or addressVersionNumber > 4:
                raise APIError('The address version number currently must be 2, 3 or 4. Others aren\'t supported. Check the address.')
            if streamNumber != 1:
                raise APIError('The stream number must be 1. Others aren\'t supported. Check the address.')

            return (status, addressVersionNumber, streamNumber, ripe)

    api = MainAPI()
    api.start(daemon=True)
    time.sleep(5)
    return api

class XMLRPCServer:
    def __init__(self,path=None):
        self.path = path
        self.quit = False
        
    def start(self,address='localhost',port=9000):
        if self.path:
            self.api = getAPI(self.path)
        else:
            self.api = class_api.getAPI()
        self.server = SimpleXMLRPCServer((address, port),logRequests=False)
        self.server.register_instance(self.api)
        server_thread = threading.Thread(target=self._work_loop)
        server_thread.start()
        
    def _work_loop(self):
        while not self.quit:
            self.server.handle_request()
        print 'Server exits'
        self.api.stop()

    def stop(self):
        
        """Stops the API"""
        
        self.quit = True
        
    def close(self):
        
        """Stops the API"""
        
        self.quit = True

class SimpleProgramAPI:
    """This API is created to simply let programs communicate over the BitMessage Network.
    It is concepted to be used extremely easy, so an own Address is automatically generated at startup.
    
    Examples:
    #Send data to a Program 
    api = SimpleProgramAPI()
    print api.get_address()
    >BM-...
    mydata = {'a':'b'}
    toAddress = BM-...
    api.send_data_wait(toAddress,mydata)
    api.close()
    
    #Recieve data for my program
    api = SimpleProgramAPI()
    print api.get_address(),'This Address should be entered in the Sending example.'
    while api.get_data() == []:
        time.sleep(1)
        print 'Waiting for a Message'
    recdata = api.get_data()
    for data in recdata:
        print 'got:',data
    >{'a':'b'}
    """
    
    def __init__(self,name,path=None,url=None):
        self.name = name
        self.url = url
        
        #Create Working Path
        if not path:
            path = os.path.abspath('bm_working_dir')
            try:
                os.makedirs(path)
            except:
                pass
            
        #Starting the API
        self.api = getAPI(workingdir=path,silent=True)

        #Delete Addresses that are not used
        for entry in self.api.listAddresses():
            if entry['label'] != name:
                self.api.deleteAddress(entry['address'])
        
        #Create the one Address that is used
        if len(self.api.listAddresses()) == 0:
            self.api.createRandomAddress(name)
        
        #Wait for the Address to be fully generated
        while len(self.api.listAddresses()) == 0:
            time.sleep(0.5)
            
        #Save our Address for later usage
        self.address = self.api.listAddresses()[0]['address']
        
    def get_address(self):
        
        """The automatically generated Address could be read out with this function."""
        
        return self.address

    def get_header(self):
        
        """Create a Header, used in the Subject Field"""
        if self.url:
            header = 'This is an autogenerated Mail by the Software:%s (%s)'%(self.name,self.url)
        else:
            header = 'This is an autogenerated Mail by the Software:%s'%self.name
        
        return header

    def send_data(self,ToAddress,data):
        
        """The send_data function simply sends Json compatible data to an address of your choice."""
        
        data = json.dumps(data)
        return self.api.sendMessage(self.address,ToAddress,self.get_header(),data)
        
    def send_data_wait(self,ToAddress,data):
        
        """The send_data_wait function blocks, until the message is sent correctly"""
        
        data = json.dumps(data)
        ack = self.api.sendMessage(self.address,ToAddress,self.get_header(),data)
        while not 'msgsent' in self.api.getSentMessageByAckData(ack)[0]['status']:
            time.sleep(1)

    def get_data(self):
        
        """The get_data function returns a list of objects recreated from the Json strings"""
        
        out = []
        for message in self.api.getAllInboxMessages():
            sys.stderr.write(str(message)) 
            if message['subject'] == self.get_header():
                out.append(json.loads(message['message']))
        return out
        
    def close(self):
        
        """This function closes the API"""
        
        self.api.stop()
        

