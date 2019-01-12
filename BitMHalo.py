import BitMessage.class_api as class_api
import BitMessage.parallelTestModule as parallelTestModule
import time
import ast
import sys, os, inspect, re
if os.name == 'nt':
    import msvcrt as m
else:
    import curses as m
import imaplib
import smtplib
import email
import quopri
import base64
import pyzmail
from highlevelcrypto import *
import traceback
import re
import stopit
import xmlrpclib
import password
from email.parser import HeaderParser
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
#########################################
providers=[{'@gmail': {'imap':'imap.googlemail.com','smtp':'smtp.googlemail.com','port':587,'SSL':0}},{'@hotmail':{'imap':'imap-mail.outlook.com','smtp':'smtp-mail.outlook.com','port':587,'SSL':0}}, {'@outlook':{'imap':'imap-mail.outlook.com','smtp':'smtp-mail.outlook.com','port':587,'SSL':0}},{'@aol.com':{'imap':'imap.aol.com','smtp':'smtp.aol.com','port':587,'SSL':0}}]#Mail.com support removed. They now charge for imap/smtp {'@mail':{'imap':'imap.mail.com','smtp':'smtp.mail.com','port':587,'SSL':0}}
imapname = 'imap.googlemail.com'
smtpname = 'smtp.googlemail.com'
port=587
isSSL=0
username = ''
EmailPassword = ''
readmessages=[]
prevaccount=""
timeresult=False
typ=""
msg_data=""
connection=""
global mypassword
mypassword=""
global systemexit
systemexit=0
global lockTHIS
lockTHIS=0
#print txhash(open("blackhalo2.py", 'rb').read())
#########################################
from PyQt4.QtCore import QThread
import threading

os.environ['no_proxy'] = '127.0.0.1,localhost'
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)
class RPCThread(QThread): #threading.Thread
    def __init__(self, url):
        QThread.__init__(self)#super(RPCThread, self).__init__()
        self.url=url
    # Register an instance; all the methods of the instance are
    # published as XML-RPC methods (in this case, just 'div').
    class MyFuncs:
        def ExitBitmessage(self, passw):
            global systemexit
            sys.stderr.write(str("Closing Bitmessage..."))
            #if passw=='password'
            try:
                api.stop()
            except:
                traceback.print_exc()
            systemexit=1
            return True
        def StorePassword(self, password1, passw):
            global mypassword
            #To prevent sending mail loss, we only use this for retreiving mail
            mypassword=password1
            return True
        def FileLock(self, islocked):
            global lockTHIS
            if islocked=="0":#Checking
                if lockTHIS==1:
                    return False
                else:
                    return True
            if islocked=="1":
                lockTHIS=2
                return True
            else:
                lockTHIS=0
                return True             
    def run(self):
        # Create server
        server = SimpleXMLRPCServer(("localhost", 8878),requestHandler=RequestHandler, logRequests = False)
        server.register_introspection_functions()
        #Register functions
        server.register_instance(self.MyFuncs())
        # Run the server's main loop
        return server.serve_forever()
bitmrpc=RPCThread("RPC")
bitmrpc.start()

def waitlock():
    global lockTHIS
    count=0
    while count<300 and lockTHIS==2:
        time.sleep(.1)
        count+=1
    lockTHIS=0

def getPythonFileLocation():
    """  returns the location of where the python file is located """
    if os.path.dirname(__file__) != "":
        return os.path.dirname(__file__)
    elif os.path.dirname(os.path.abspath(__file__)) != "":
        return os.path.dirname(os.path.abspath(__file__))
    elif os.path.dirname(os.getcwd()) != "":
        return os.path.dirname(os.getcwd())
    else:
        from inspect import getsourcefile
        return os.path.dirname(os.path.abspath(getsourcefile(lambda _:None)))
application_path=getPythonFileLocation()

list_response_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')
def parse_list_response(line):
    flags, delimiter, mailbox_name = list_response_pattern.match(line).groups()
    mailbox_name = mailbox_name.strip('"')
    return (flags, delimiter, mailbox_name)

if __name__ ==  '__main__':
    #extractor = parallelTestModule.ParallelExtractor()
    #extractor.runInParallel(numProcesses=1, numThreads=1)#EDIT:Was two processes is now one
    path1=sys.argv[0]
    os.environ['no_proxy'] = '127.0.0.1,localhost'
    myrpc = xmlrpclib.ServerProxy('http://127.0.0.1:8877')
    application_path=path1
    application_path=application_path.replace("python ","")
    application_path=application_path.replace("python2.7 ","")
    application_path=application_path.replace("BitMHalo.py","")
    application_path=application_path.replace("BitMHalo.exe","")
    application_path=application_path.replace("BitMHalo","")
    if os.name != "nt":
        if application_path=="":
            application_path+="./"
        application_path=application_path.replace("//","/")
    sys.stderr.write("\nBITMHALO PATH: "+application_path+"\n")
    os.environ["BITMESSAGE_HOME"]=application_path
    api = class_api.getAPI(workingdir=application_path, silent=True)
    ch=""
    path=os.path.join(application_path,"BitTMP.dat")
    outpath=os.path.join(application_path,"Outbox.dat")
    mailpath=os.path.join(application_path,"MailCache.dat")
    data=[]
    data.append("0")
    data.append("0")
    data.append("0")
    data.append("0")
    data.append("0")
    data.append("0")
    data.append("0")
    with open(outpath,'a+') as f:
        f.close()
    if os.stat(outpath)[6]==0:
        with open(outpath,'w') as f:
            f.write("[]")
            f.flush()
            os.fsync(f)
            f.close()
    with open(mailpath,'a+') as f:
        f.close()
    if os.stat(mailpath)[6]==0:
        with open(mailpath,'w') as f:
            f.write("{}")
            f.flush()
            os.fsync(f)
            f.close()
    ticker=0
    ticker2=22
    ticker3=0
    while ch != "exit":
        if systemexit==1:
            systemexit=2
            sys.stderr.write(str("Closing Bitmessage..."))
            sys.exit()
        time.sleep(0.23456)
        ticker+=1 #We dont check email messages as compulsively not do we try resending outbox messages as compulsively
        ticker2+=1
        ticker3+=1
        if ticker3>1000:
            ticker3=0
            readmessages=[]#We check read messages again after a while.
        if ticker==1000:
            ticker=0
            try:
                with open(outpath,'r') as f:
                    outbox=f.readline()
                    f.close()
                #Sends a message
                pos=0
                try:
                    outbox=ast.literal_eval(outbox)
                except:
                    sys.stderr.write(str("OUTBOX ERROR"))
                    outbox=[]
                for data1 in outbox:#Lets try sending some of these messages again
                    time.sleep(.1)
                    next=1
                    EmailPassword=""
                    fromAddress=""
                    if "ENCRYPTED:" in data1:
                        if "PASSWORD:" in data1:
                            matchObj = re.match( r'(PASSWORD:)(.*?)(MY:)', data1, re.M|re.I)
                            EmailPassword=matchObj.group(2)
                            data1=data1.replace("PASSWORD:"+EmailPassword,"")
                        matchObj = re.match( r'(MY:)(.*?)(THEIR:)(.*?)(ENCRYPTED:)(.*?)(###)', data1, re.M|re.I)
                        content=matchObj.group(5)+matchObj.group(6)
                        fromAddress=matchObj.group(2)
                        toAddress=matchObj.group(4)
                    else:
                        try:
                            content=ast.literal_eval(data1)
                            fromAddress=content['MyBMAddress']
                            toAddress=content['TheirBMAddress']
                            if 'password' in content:
                                EmailPassword=content['password']
                                content.pop("password", None)
                        except:
                            sys.stderr.write(str("OUTBOX PARSE ERROR"))
                            toAddress="####"
                    verified=0
                    for prov in providers:
                        for key, val in prov.items():
                            pass
                        if key in fromAddress.lower():
                            verified=1
                            imapname = prov[key]['imap']
                            smtpname = prov[key]['smtp']
                            port = prov[key]['port']
                            isSSL = prov[key]['SSL']
                            break
                    ret = True
                    try:
                        EmailPassword=password.DecryptWithAES("Halo Master", EmailPassword)
                    except:
                        sys.stderr.write(str("PASSWORD DECRYPTION ERROR"))
                    if "@" in toAddress and verified==1:
                        if "You have received a payment of " not in str(content) and "If you are new to Cryptocurrency, somebody may have sent you these coins" not in str(content):
                            content="****"+str(content)+"****"
                            attach=0
                        else:
                            attach=1
                        if attach==0:
                            try:
                                connection = imaplib.IMAP4_SSL(imapname)
                                connection.login(fromAddress, EmailPassword)
                            except:
                                sys.stderr.write(str("OUTBOX AUTHENTICATION ERROR"))
                                ret = False
                        try:
                            if attach==0:
                                connection = smtplib.SMTP(smtpname, port)
                                connection.ehlo()
                                connection.starttls()
                                headers = ["from: " + fromAddress, "subject: " + "Halo", "to: " + toAddress,"mime-version: 1.0","content-type: text/html"]
                                headers = "\r\n".join(headers)
                                connection.login(fromAddress, EmailPassword)
                                connection.sendmail(fromAddress, toAddress, headers+"\r\n\r\n"+str(content))
                                connection.close()
                            else:
                                b64=base64.b64decode(content['b64img'])
                                text_content=unicode(content['Data'])
                                html_content=u'<html><body>' + content['Data'] + \
                                          '<img src="cid:doge" />.\n' \
                                          '</body></html>'
                                payload, mail_from, rcpt_to, msg_id=pyzmail.compose_mail(\
                                    (unicode(fromAddress), fromAddress), \
                                    [(unicode(toAddress), toAddress)], \
                                    u'Halo', \
                                    'iso-8859-1', \
                                    (text_content, 'iso-8859-1'), \
                                    (html_content, 'iso-8859-1'), \
                                    embeddeds=[(b64, 'image', 'bmp', 'doge', None), ])
                                ret=pyzmail.send_mail(payload, fromAddress, toAddress, smtpname, \
                                    smtp_port=port, smtp_mode='tls', \
                                    smtp_login=fromAddress, smtp_password=EmailPassword)
                                if isinstance(ret, dict):
                                    if ret:
                                        float("A")
                                    else:
                                        pass
                                else:
                                    float("A")
                        except Exception, e:
                            sys.stderr.write(str("OUTBOX SENDING ERROR: ")+str(e))
                            ret = False
                    if ret != False or toAddress=="####":#We are not resending bitmessage at the moment
                        outbox.pop(pos)
                        next=0
                        with open(outpath,'w') as f:
                            f.write(str(outbox))
                            f.flush()
                            os.fsync(f)
                            f.close()
                    if next==1:
                        pos+=1
            except Exception, e:
                traceback.print_exc()
        try:
            with open(path,'r') as f:
                data[0]=f.readline().strip()
                data[1]=f.readline().strip()
                try:
                    data[2]=f.readline().strip()
                except:
                    sys.stderr.write(str("File error"))
                try:
                    data[3]=f.readline().strip()
                except:
                    pass
                f.close()
        except Exception,e:
            traceback.print_exc()
        if data[0] == "0":
            time.sleep(.23456)
            try:
                ch=data[1]
                if ch == "Send":
                    #Sends a message
                    EmailPassword=""
                    fromAddress=""
                    original=data[2]
                    if "ENCRYPTED:" in data[2]:
                        try:
                            if "PASSWORD:" in data[2]:
                                matchObj = re.match( r'(PASSWORD:)(.*?)(MY:)', data[2], re.M|re.I)
                                EmailPassword=matchObj.group(2)
                                data[2]=data[2].replace("PASSWORD:"+EmailPassword,"")
                            matchObj = re.match( r'(MY:)(.*?)(THEIR:)(.*?)(ENCRYPTED:)(.*?)(###)', data[2], re.M|re.I)
                            content=matchObj.group(5)+matchObj.group(6)
                            fromAddress=matchObj.group(2)
                            toAddress=matchObj.group(4)
                        except:
                            sys.stderr.write(str("ENCRYPTION ERROR"))
                    else:
                        try:
                            content=ast.literal_eval(data[2])
                            fromAddress=content['MyBMAddress']
                            toAddress=content['TheirBMAddress']
                            if 'password' in content:
                                EmailPassword=content['password']
                                content.pop("password", None)
                        except:
                            sys.stderr.write(str("PARSE ERROR"))
                            toAddress=""
                            content="####"
                    verified=0
                    for prov in providers:
                        for key, val in prov.items():
                            pass
                        if key in fromAddress.lower():
                            verified=1
                            imapname = prov[key]['imap']
                            smtpname = prov[key]['smtp']
                            port = prov[key]['port']
                            isSSL = prov[key]['SSL']
                            break
                    ret = True
                    try:
                        EmailPassword=password.DecryptWithAES("Halo Master", EmailPassword)
                    except:
                        sys.stderr.write(str("PASSWORD DECRYPTION ERROR"))
                    if "@" in toAddress and verified==1:
                        if "You have received a payment of " not in str(content) and "If you are new to Cryptocurrency, somebody may have sent you these coins" not in str(content):
                            attach=0
                            content="****"+str(content)+"****"
                        else:
                            attach=1
                        if attach==0:
                            try:
                                connection = imaplib.IMAP4_SSL(imapname)
                                connection.login(fromAddress, EmailPassword)
                            except:
                                sys.stderr.write(str("AUTHENTICATION ERROR"))
                                ret = False
                        try:
                            if attach==0:
                                connection = smtplib.SMTP(smtpname, port)
                                connection.ehlo()
                                connection.starttls()
                                headers = ["from: " + fromAddress, "subject: " + "Halo", "to: " + toAddress,"mime-version: 1.0","content-type: text/html"]
                                headers = "\r\n".join(headers)
                                connection.login(fromAddress, EmailPassword)
                                connection.sendmail(fromAddress, toAddress, headers+"\r\n\r\n"+str(content))
                                connection.close()
                            else:                               
                                b64=base64.b64decode(content['b64img'])
                                text_content=unicode(content['Data'])
                                html_content=u'<html><body>' + content['Data'] + \
                                          '<img src="cid:doge" />.\n' \
                                          '</body></html>'
                                payload, mail_from, rcpt_to, msg_id=pyzmail.compose_mail(\
                                    (unicode(fromAddress), fromAddress), \
                                    [(unicode(toAddress), toAddress)], \
                                    u'Halo', \
                                    'iso-8859-1', \
                                    (text_content, 'iso-8859-1'), \
                                    (html_content, 'iso-8859-1'), \
                                    embeddeds=[(b64, 'image', 'bmp', 'doge', None), ])
                                ret=pyzmail.send_mail(payload, fromAddress, toAddress, smtpname, \
                                    smtp_port=port, smtp_mode='tls', \
                                    smtp_login=fromAddress, smtp_password=EmailPassword)
                                #For sending attachment: attachments=[(b64, 'image', 'bmp', 'image.bmp', None)
                                if isinstance(ret, dict):
                                    if ret:
                                        float("A")
                                    else:
                                        pass
                                else:
                                    float("A")
                                ret = True
                        except Exception, e:
                            sys.stderr.write(str("SEND ERROR: ")+ str(e))
                            ret = False
                        if ret== False:#It failed lets write it to an outbox... We could also try repeating until solved. Reporting an email fail via api.
                            outbox=[]
                            try:
                                with open(outpath,'r') as f:
                                    outbox=f.readline().strip()
                                    outbox=ast.literal_eval(outbox)
                                    f.close()
                            except Exception,e:
                                pass
                            try:
                                if str(original) not in outbox:
                                    outbox.append(str(original))
                                with open(outpath,'w') as f:
                                    f.write(str(outbox))
                                    f.flush()
                                    os.fsync(f)
                                    f.close()
                            except:
                                sys.stderr.write(str("File Error"))
                            ret="False"+str(data[2])
                    else:
                        try:
                            ret = api.sendMessage(fromAddress,toAddress,"BitHalo",str(content))
                        except Exception, e:
                            ret = "False"+str(content)
                    try:
                        waitlock()
                        lockTHIS=1
                        with open(path,'w') as f:
                            f.write("1"+"\n")
                            f.write("Send1"+"\n")
                            f.write(str(ret)+"\n")
                            f.write(str(data[3])+"\n")
                            f.flush()
                            os.fsync(f)
                            f.close()
                        lockTHIS=0
                    except:
                        lockTHIS=0
                        sys.stderr.write(str("File Error"))
                if ch == "GetMessages" or ch == "Remove Order" or ch == "Clean Inbox":
                    if ticker2>22:
                        sys.stderr.write(str("\n\n\nChecking Inbox...\n\n\n"))
                        ticker2=0
                        #Gets messages
                        inbox=[]
                        ret=""
                        try:
                            dat=ast.literal_eval(data[2])
                            if 'Password' in dat:
                                if dat['Password']=="#!#":
                                    dat['Password']=mypassword
                                try:
                                    dat['Password']=password.DecryptWithAES("Halo Master", dat['Password'])
                                except:
                                    sys.stderr.write(str("PASSWORD DECRYPTION ERROR"))
                                verified=0
                                for prov in providers:
                                    for key, val in prov.items():
                                        pass
                                    if key in dat['Email Address'].lower():
                                        verified=1
                                        imapname = prov[key]['imap']
                                        smtpname = prov[key]['smtp']
                                        port = prov[key]['port']
                                        isSSL = prov[key]['SSL']
                                        break
                                if verified==1:
                                    try:
                                        if dat['Email Address']!=prevaccount or ch == "Remove Order" or ch == "Clean Inbox":
                                            readmessages=[]#reset on new accounts or maintenance
                                            #For now we maintain the record of read messages on the client side
                                        prevaccount=dat['Email Address']
                                        connection = imaplib.IMAP4_SSL(imapname)
                                        connection.login(dat['Email Address'], dat['Password'])
                                        typ, mailbox_data = connection.list()
                                        inbox = []
                                        try:
                                            with open(mailpath,'r') as f:
                                                mailbox=f.readline()
                                                f.close()
                                            mailbox=ast.literal_eval(mailbox)
                                            if mailbox=="":
                                                float('a')
                                            if dat['Email Address'] not in mailbox:
                                                mailbox[dat['Email Address']]={}
                                        except:
                                            mailbox={str(dat['Email Address']):{}}                                        
                                        for line in mailbox_data:
                                            try:
                                                flags, delimiter, mailbox_name = parse_list_response(line)
                                                if "sent" in mailbox_name.lower() or "all" in mailbox_name.lower() or "deleted" in mailbox_name.lower() or "trash" in mailbox_name.lower() or "drafts" in mailbox_name.lower():
                                                    continue
                                                if ch == "Remove Order":
                                                    connection.select(mailbox_name)
                                                else:
                                                    connection.select(mailbox_name, readonly=True)
                                                msg_ids1=set([])
                                                try:
                                                    typ, msg_ids1 = connection.uid('search', None, '(SUBJECT "Halo")')#connection.search(None, '(SUBJECT "Halo")')
                                                except Exception, e:
                                                    sys.stderr.write(str("SEARCH ERROR")+str(e))
                                                    continue
                                                msg_ids = msg_ids1[0]
                                                try:
                                                    msg_ids = msg_ids.split()
                                                except:
                                                    sys.stderr.write(str("Split Error"))
                                                src=""
                                                src1=""
                                                mydict2={}
                                                if 'uids' in dat:
                                                    for elem in dat['uids']:
                                                        try:
                                                            ordnum=elem.split("#")[1]
                                                            orduid=elem.split("#")[0]
                                                            mydict2[orduid]=ordnum
                                                        except:
                                                            mydict2[elem]=''
                                                for msg_id in msg_ids:
                                                    if 'uids' in dat:#If they ask to skip any messages we do so
                                                        if msg_id in mydict2:
                                                            if 'ordernumber' in dat:
                                                                if dat['ordernumber']==mydict2[msg_id]:
                                                                    pass
                                                                else:
                                                                    continue
                                                            else:
                                                                continue
                                                    sys.stderr.write("\n\n"+str(msg_id)+"\n\n")
                                                    mymessage={}
                                                    if msg_id in mailbox[str(dat['Email Address'])]:
                                                        try:
                                                            mymessage['toAddress']=mailbox[str(dat['Email Address'])][msg_id]['toAddress']
                                                            mymessage['fromAddress']=mailbox[str(dat['Email Address'])][msg_id]['fromAddress']
                                                            mymessage['body']=mailbox[str(dat['Email Address'])][msg_id]['body']
                                                            mymessage['uid']=mailbox[str(dat['Email Address'])][msg_id]['uid']
                                                            body=mymessage['body']
                                                        except:
                                                            body=""
                                                            mymessage={}
                                                            sys.stderr.write("\n\nMessage reading error!\n\n")
                                                    else:
                                                        try:
                                                            if systemexit==1:#Attempt a clean exit when possible
                                                                systemexit=2
                                                                sys.stderr.write(str("Closing Bitmessage..."))
                                                                sys.exit()
                                                            sys.stderr.write(str("\n\nFETCHING...\n\n"))
                                                            #This is to prevent dropped connections, for now only on fetching
                                                            timeresult = False
                                                            try:#Let Halo know through RPC we started to download
                                                                myrpc.MessageStatus("1","password")
                                                            except Exception, e:
                                                                pass
                                                            @stopit.threading_timeoutable(timeout_param='my_timeout')
                                                            def timethis():#If we get dropped, we can time out
                                                                global timeresult, typ, msg_data, connection
                                                                typ, msg_data = connection.uid('fetch', msg_id, '(RFC822)') #connection.fetch(msg_id, '(RFC822)')
                                                                timeresult = True
                                                            timethis(my_timeout=600)#10 minutes is very generous
                                                            if timeresult==False:
                                                                float("A")
                                                            try:#Let Halo know through RPC we finished
                                                                myrpc.MessageStatus("0","password")
                                                            except Exception, e:
                                                                pass
                                                            sys.stderr.write(str("\n\nFETCHED!!\n\n"))
                                                            #readmessages.append(msg_id)
                                                        except:
                                                            connection.close()
                                                            sys.stderr.write(str("FETCH ERROR"))
                                                            if systemexit==2:
                                                                sys.exit()
                                                            continue
                                                        body = ""
                                                        try:
                                                            for part in msg_data:
                                                                if isinstance(part, tuple):
                                                                    msg = email.message_from_string(part[1])
                                                                    try:
                                                                        src = (msg['from'].split('<')[1].split('>')[0]).strip()
                                                                    except:
                                                                        src = msg['from'].strip()
                                                                    try:
                                                                        src1 = (msg['to'].split('<')[1].split('>')[0]).strip()
                                                                    except:
                                                                        src1 = msg['to'].strip()
                                                                    try:
                                                                        if msg.is_multipart():
                                                                            for msub in msg.get_payload():
                                                                                body = msub.get_payload(decode = True).decode(msub.get_content_charset())
                                                                                break
                                                                        else:
                                                                            body = msg.get_payload(decode = True).decode(msg.get_content_charset())
                                                                    except:
                                                                        try:
                                                                            body=str(msg.encode('utf8'))
                                                                        except:
                                                                            body=str(msg)
                                                        except Exception, e:
                                                            sys.stderr.write(str("MESSAGE ERROR "))
                                                            sys.stderr.write(str(e))
                                                        mymessage['toAddress']=str(src1)
                                                        mymessage['fromAddress']=str(src)
                                                        try:
                                                            body=str(body.encode('utf8'))
                                                        except:
                                                            sys.stderr.write(str("Not encoded"))
                                                        try:
                                                            body = body.split('****')[1].split('****')[0]
                                                        except:
                                                            try:
                                                                if 'You have received a payment of ' not in str(body):
                                                                    body=""
                                                                else:
                                                                    #I'm hoping email providers will not change this as identifying the full base64 string would be challenging.
                                                                    #Any added padding gets changed when uploading the base64 image with the pyzmail library, although the bitmap is lossless
                                                                    body = body.split('<doge>\nContent-Disposition: inline\n\n')[1].split('\n--=========')[0]
                                                                    body="PAY TO EMAIL BASE64 IMAGE:"+body
                                                            except:#Okay they changed it we can try something else
                                                                try:
                                                                    bodymsg = email.message_from_string(str(body))
                                                                    x=0
                                                                    posx=0
                                                                    while x<len(bodymsg.get_payload()):
                                                                        attachment = bodymsg.get_payload()[x]
                                                                        if "bmp" in attachment.get_content_type():
                                                                            posx=x
                                                                        x+=1
                                                                    attachment = msg.get_payload()[posx]
                                                                    img=attachment.get_payload(decode=False)
                                                                    body=img
                                                                    body="PAY TO EMAIL BASE64 IMAGE:"+body
                                                                except:
                                                                    sys.stderr.write(str("PARSE ERROR"))
                                                                    body = ""
                                                        if 'fromAddress' in mymessage and body!="": #decode emails
                                                            if '@aol' in mymessage['fromAddress'].lower() or '@mail' in mymessage['fromAddress'].lower():
                                                                body=body.encode('utf8').replace("\r\n ","")
                                                                if "ENCRYPTED:" in body:
                                                                    body=body.replace(" ","")
                                                        mymessage['body']=str(body)
                                                        mymessage['uid']=msg_id
                                                        if 'fromAddress' in mymessage and 'toAddress' in mymessage:
                                                            mailbox[str(dat['Email Address'])][msg_id]=ast.literal_eval(str(mymessage))                                                        
                                                    if 'ordernumber' in dat:
                                                        if "ENCRYPTED:" in str(body):
                                                            try:
                                                                MyCipher=body.replace("ENCRYPTED:","")
                                                                MyCipher=base64.b64decode(MyCipher)
                                                                MyCipher=decrypt(MyCipher, dat['Private Key'])
                                                                body=MyCipher
                                                            except Exception, e:
                                                                try:
                                                                    body=body.replace("=\r\n","")
                                                                    body=body.replace("\r\n","")
                                                                    body=body.replace(" ","")
                                                                    body=body.replace("****","")
                                                                    try:
                                                                        body=body.encode('utf8')
                                                                    except:
                                                                        pass
                                                                    try:
                                                                        MyCipher=quopri.decodestring(body)
                                                                    except:
                                                                        MyCipher=body
                                                                    MyCipher=MyCipher.replace("ENCRYPTED:","")
                                                                    missing_padding = len(MyCipher) % 4
                                                                    if missing_padding != 0:
                                                                        MyCipher += b'='* (4 - missing_padding)
                                                                    MyCipher=base64.b64decode(MyCipher)
                                                                    MyCipher=decrypt(MyCipher, dat['Private Key'])
                                                                    body=MyCipher
                                                                except:
                                                                    pass
                                                        if dat['ordernumber'] in str(body):
                                                            try:
                                                                body=ast.literal_eval(body)
                                                                if body['ordernumber']==dat['ordernumber']:
                                                                    connection.uid('STORE', msg_id, '+FLAGS', '(\Deleted)')#The flags should always be in parenthesis
                                                                    connection.expunge()                                                                    
                                                                    sys.stderr.write(str("\n\n\REMOVED!!\n\n"))
                                                                    try:
                                                                        mailbox[str(dat['Email Address'])].pop(msg_id)
                                                                    except:
                                                                        sys.stderr.write(str("\n\nNOT REMOVED FROM CACHE\n\n"))
                                                            except:
                                                                sys.stderr.write(str("\n\nNOT REMOVED\n\n"))
                                                        else:
                                                            sys.stderr.write(str("\n\nNOT REMOVED\n\n"))
                                                    if mymessage not in inbox:
                                                        inbox.append(mymessage)
                                                #To save time and to avoid duplicates, i used to break at INBOX but we should also check Junk folder
                                                #if str(mailbox_name)=="INBOX":
                                                #   break
                                            except:#Mailbox error
                                                traceback.print_exc()
                                                sys.stderr.write(str("INBOX ERROR"))
                                                if systemexit==2:
                                                    sys.exit()
                                                pass
                                        sys.stderr.write(str("\n\nClosing...\n\n"))
                                        connection.close()
                                        sys.stderr.write(str("\n\nCLOSED!\n\n"))
                                        try:
                                            waitlock()
                                            lockTHIS=1                                            
                                            with open(mailpath,'w') as f:
                                                f.write(str(mailbox))
                                                f.flush()
                                                os.fsync(f)
                                                f.close()
                                            lockTHIS=0
                                        except:
                                            lockTHIS=0
                                            sys.stderr.write(str("\n\Cache write error!\n\n"))
                                    except Exception, e:
                                        if systemexit==2:
                                            sys.exit()
                                        sys.stderr.write(str("\n\n\nException with inbox\n\n\n"))
                                        ret=False
                                        traceback.print_exc()
                        except Exception, e:
                            if systemexit==2:
                                sys.exit()
                            traceback.print_exc()
                            pass
                        try:
                            if ch == "Clean Inbox":
                                msgids=api.getAllInboxMessageIDs()
                                a = api.getAllInboxMessages()
                                dat['Address']=dat['Bitmessage Address']
                                sentmessages = api.getSentMessagesBySender(dat['Address'])
                                #Clear Sent symbolizes we have no open contracts to worry about message loss
                                if 'Clear Sent' in dat:
                                    Smsgids=api.getAllSentMessageIDs()
                                    for msg in Smsgids:
                                        message=api.getSentMessageByID(msg)
                                        if message[0]['fromAddress']==dat['Bitmessage Address']:
                                            if 'msgsent' in message[0]['status'] or 'ackreceived' in message[0]['status']:
                                                api.trashSentMessage(msg)
                                for msg in msgids:
                                    message=api.getInboxMessageByID(msg)
                                    if message[0]['toAddress']==dat['Bitmessage Address'] and 'Clear Sent' in dat:
                                        api.trashInboxMessage(msg)
                                    if message[0]['toAddress'] in dat['MyMarkets']:#Market orders are more expendable
                                        api.trashInboxMessage(msg)
                        except:
                            a = api.getAllInboxMessages()
                            sentmessages = "False"
                            sys.stderr.write(str("Inbox Clean Error"))
                        if ch != "Clean Inbox":
                            a = api.getAllInboxMessages()
                        try:
                            if ch != "Clean Inbox":
                                sentmessages = api.getSentMessagesBySender(dat['Address'])
                        except:
                            sentmessages = "False"
                        for inmessage in inbox:
                            a.append(inmessage)
                        try:
                            status=api.clientStatus()
                        except:
                            sys.stderr.write(str("Status Error"))
                            status=""
                        sys.stderr.write(str("\n\n\nInbox Checked\n\n\n"))
                        try:
                            waitlock()
                            lockTHIS=1                          
                            with open(path,'w') as f:
                                f.write("1"+"\n")
                                if ch=="GetMessages" or ch=="Clean Inbox":
                                    if ret==False:
                                        f.write(ch+"1:False:"+str(status)+"\n")
                                    else:
                                        f.write(ch+"1:"+str(status)+"\n")
                                    f.write(str(a)+"\n")
                                    f.write(str(sentmessages)+"\n")
                                if ch=="Remove Order":
                                    f.write("RemoveOrder1\n")
                                    f.write("True\n")
                                    f.write("True\n")
                                f.flush()
                                os.fsync(f)
                                f.close()
                            lockTHIS=0
                        except Exception, e:
                            lockTHIS=0
                            traceback.print_exc()
                            pass
                if ch == "new":
                    #Make a new address and return it
                    dat=ast.literal_eval(data[2])
                    try:
                        waitlock()
                        lockTHIS=1                      
                        with open(path,'w') as f:
                            if dat["Pubs"]==[]:
                                addr=api.createRandomAddress("BitHalo")
                            else:
                                key=str(dat['Pubs'][0])
                                key2=str(dat['Pubs'][1])
                                addr=api.createDeterministicAddresses(str(key[:14]+key2[-14:]),"BitHalo")
                                try:
                                    addr=addr[0]
                                except:
                                    try:
                                        addr=api.getDeterministicAddress(str(key[:14]+key2[-14:]))
                                    except:
                                        addr=" "
                                addr2=api.createDeterministicAddresses(str(key2[:14]+key[-14:]),"BitHalo")
                                sys.stderr.write(str("\n\n\n"))
                                sys.stderr.write(str(addr))
                            f.write("1"+"\n")
                            f.write("new1"+"\n")
                            f.write(addr+"\n")
                            f.write(dat["multisig"]+"\n")
                            f.flush()
                            os.fsync(f)
                            f.close()
                        lockTHIS=0
                    except:
                        lockTHIS=0
                        traceback.print_exc()
                        sys.stderr.write(str("New Address Error"))
                if ch == "Add Channel":
                    #Make a new channel address and return it
                    dat=ast.literal_eval(data[2])

                    try:
                        waitlock()
                        lockTHIS=1                      
                        with open(path,'w') as f:
                            #addr=api.createDeterministicAddresses(dat['Address'],dat['Address'])
                            #api.addSubscription(dat['Address'], addr)
                            try:
                                addr=api.joinChannel(dat['Address'])
                            except:
                                try:
                                    addrdata=api.listAddressBook()
                                    for add in addrdata:
                                        if add['label']=="[chan] "+dat['Address']:
                                            addr=add['address']
                                            break
                                except:
                                    addr="Exception"
                            f.write("1"+"\n")
                            f.write("chan1"+"\n")
                            f.write(addr+"\n")
                            f.write(dat['Address']+"\n")
                            f.flush()
                            os.fsync(f)
                            f.close()                   
                        lockTHIS=0
                    except:
                        lockTHIS=0
                        sys.stderr.write(str("New Address Error"))
                if ch == "Remove Channel":
                    #Make a new channel address and return it
                    dat=ast.literal_eval(data[2])
                    try:
                        waitlock()
                        lockTHIS=1                      
                        with open(path,'w') as f:
                            #addr=api.createDeterministicAddresses(dat['Address'],dat['Address'])
                            #api.addSubscription(dat['Address'], addr)
                            try:
                                addr=api.deleteChannel(dat['Address'])
                                if addr:
                                    addr="Success"
                                else:
                                    addr="Failed"
                            except:
                                traceback.print_exc()
                                addr="Exception"
                            f.write("1"+"\n")
                            f.write("remchan"+"\n")
                            f.write(addr+"\n")
                            f.write(dat['Address']+"\n")
                            f.flush()
                            os.fsync(f)
                            f.close()
                        lockTHIS=0
                    except:
                        lockTHIS=0
                        traceback.print_exc()
                        sys.stderr.write(str("New Address Error"))
            except:
                if systemexit==2:
                    sys.exit()
                sys.stderr.write(str("Checking/Thread Error"))