import os
import commonlib.apicom.share;
import commonlib.apicom.cmdSvr;

#create two pipes
cmdSvrRecv,clientSend = os.pipe();
clientRecv,cmdSvrSend = os.pipe();

commonlib.apicom.share.clientSend = clientSend;
commonlib.apicom.share.clientRecv = clientRecv;

childPid = os.fork();
if childPid == 0:
    commonlib.apicom.share.stopCmdSvr = False;
    commonlib.apicom.cmdSvr.run(cmdSvrRecv,cmdSvrSend);
