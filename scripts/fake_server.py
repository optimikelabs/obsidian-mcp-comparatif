"""Serveur MCP FACTICE du kit, jamais un candidat. Stdio JSON-RPC et HTTP local."""
import argparse
import queue
import sys
import threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from common import *

class Fake:
    def __init__(self,vault): self.vault=scoped(vault);self.lock=threading.Lock();self.state='idle';self.threads=[]
    def rpc(self,req):
        method=req.get('method');params=req.get('params',{});ident=req.get('id')
        if ident is None:return None
        if method=='initialize':result={'protocolVersion':params.get('protocolVersion','2025-03-26'),'capabilities':{'tools':{}},'serverInfo':{'name':'kit-factice','version':'1.0.0'}}
        elif method=='ping':result={}
        elif method=='tools/list':
            result={'tools':[{'name':n,'description':'FAKE qualification only','inputSchema':{'type':'object','properties':{'path':{'type':'string'},'content':{'type':'string'},'old':{'type':'string'},'new':{'type':'string'},'etag':{'type':'string'}},'required':['path']}} for n in ('read','create','write','patch','append','rank','refuse','deferred_patch','deferred_refuse','deferred_append','status')]}
        elif method=='tools/call':
            try:
                with self.lock: result=self.call(params['name'],params.get('arguments',{}))
            except Exception as e:result={'isError':True,'content':[{'type':'text','text':str(e)}]}
        else:return {'jsonrpc':'2.0','id':ident,'error':{'code':-32601,'message':'Method not found'}}
        return {'jsonrpc':'2.0','id':ident,'result':result}
    def call(self,name,args):
        p=target(self.vault,args['path'])
        if name=='plan':value={'state':'planned','content':args['content']}
        elif name=='status':value={'state':self.state,'operation_id':'fake-operation'}
        elif name.startswith('deferred_'):
            self.state='pending'
            def work():
                time.sleep(.1) # latence factice volontaire, aucun oracle ne la prend pour preuve
                with self.lock:
                    if name=='deferred_refuse':self.state='conflict';return
                    self.call('patch' if name=='deferred_patch' else 'append',args);self.state='committed'
            thread=threading.Thread(target=work,daemon=True);thread.start();self.threads.append(thread)
            value={'state':'pending','operation_id':'fake-operation'}
        elif name=='read_structured':
            props,body=split(p.read_bytes());value={'fm':props,'content':body}
        elif name=='read':value={'path':args['path'],'content':p.read_text(encoding='utf-8'),'etag':sha(p.read_bytes())}
        else:
            if args.get('etag') and (not p.exists() or sha(p.read_bytes())!=args['etag']):raise ValueError('REVISION_CONFLICT')
            if name=='refuse':raise ValueError('SAFE_REFUSAL')
            if name=='create':
                p.parent.mkdir(parents=True,exist_ok=True)
                with p.open('x',encoding='utf-8',newline='') as f:f.write(args['content'])
            elif name=='write':p.write_text(args['content'],encoding='utf-8',newline='')
            elif name=='append':
                with p.open('a',encoding='utf-8',newline='') as f:f.write(args['content'])
            elif name=='patch':
                text=p.read_text(encoding='utf-8')
                if text.count(args['old'])!=1:raise ValueError('NOT_UNIQUE')
                p.write_text(text.replace(args['old'],args['new']),encoding='utf-8',newline='')
            elif name=='rank':
                props,body=split(p.read_bytes());props['rang']=2;p.write_bytes(render(props,body))
            else:raise ValueError('Tool not found')
            value={'path':args['path'],'ok':True}
        return {'content':[{'type':'text','text':json.dumps(value,ensure_ascii=False)}]}

def http_server(fake,port=0,sse=False):
    messages=queue.Queue()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            if not sse or self.path!='/sse':self.send_error(404);return
            self.send_response(200);self.send_header('Content-Type','text/event-stream');self.end_headers()
            self.wfile.write(b'event: endpoint\ndata: /messages\n\n');self.wfile.flush()
            try:
                while True:
                    message=messages.get(timeout=60)
                    if message is None:return
                    self.wfile.write(b'event: message\ndata: '+json.dumps(message).encode()+b'\n\n');self.wfile.flush()
            except (BrokenPipeError,ConnectionResetError,queue.Empty):return
        def do_POST(self):
            req=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            result=fake.rpc(req)
            if sse:
                if result:messages.put(result)
                self.send_response(202);self.end_headers();return
            if result is None:self.send_response(202);self.end_headers();return
            value=json.dumps(result,ensure_ascii=False).encode()
            self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(value)));self.end_headers();self.wfile.write(value)
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler);server.daemon_threads=True;server.messages=messages
    return server

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--vault',required=True);p.add_argument('--http-port',type=int);a=p.parse_args();fake=Fake(a.vault)
    if a.http_port is not None:http_server(fake,a.http_port).serve_forever()
    else:
        for line in sys.stdin:
            guard();reply=fake.rpc(json.loads(line))
            if reply is not None:print(json.dumps(reply,ensure_ascii=False),flush=True)
