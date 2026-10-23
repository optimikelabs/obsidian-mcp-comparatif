"""Relais HTTP local vers MCP stdio ou Streamable HTTP. Arguments originaux inchangés.
Les schémas des candidats sont déclarés par adaptateur avant admission. Le relais ne les invente pas.
"""
import argparse
import queue
import socket
import subprocess
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from common import *

class Stdio:
    def __init__(self,command,cwd,stderr,env=None):
        self.err=open(scoped(stderr),'a',encoding='utf-8')
        self.p=subprocess.Popen(command,cwd=cwd,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.err,text=True,encoding='utf-8',bufsize=1)
        self.q=queue.Queue();self.lock=threading.Lock()
        threading.Thread(target=self._reader,daemon=True).start()
    def _reader(self):
        for line in self.p.stdout:self.q.put(json.loads(line))
        self.q.put(None)
    def rpc(self,req):
        with self.lock:
            self.p.stdin.write(json.dumps(req,ensure_ascii=False)+'\n');self.p.stdin.flush()
            if 'id' not in req:return None
            end=time.monotonic()+60
            while time.monotonic()<end:
                guard();reply=self.q.get(timeout=max(.1,end-time.monotonic()))
                if reply is None:raise RuntimeError('Amont stdio fermé')
                if reply.get('id')==req['id']:return reply
            raise TimeoutError('Amont stdio')
    def close(self):
        self.p.terminate()
        try:self.p.wait(timeout=5)
        except subprocess.TimeoutExpired:self.p.kill();self.p.wait(timeout=5)
        self.err.close()

class HTTP:
    def __init__(self,url,headers=None):
        from urllib.parse import urlparse
        u=urlparse(url)
        if u.hostname not in ('127.0.0.1','localhost') or u.port in (27123,27124):raise ValueError('Amont hors boucle locale ou port quotidien')
        self.url=url;self.headers=headers or {};self.session=None
    def rpc(self,req):
        headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream',**self.headers}
        if self.session:headers['Mcp-Session-Id']=self.session
        r=urllib.request.Request(self.url,data=json.dumps(req).encode(),headers=headers)
        with urllib.request.urlopen(r,timeout=60) as response:
            self.session=response.headers.get('Mcp-Session-Id',self.session)
            if response.status in (202,204):return None
            if 'text/event-stream' in response.headers.get('Content-Type',''):
                for line in response:
                    guard()
                    if line.startswith(b'data:'):
                        obj=json.loads(line[5:])
                        if obj.get('id')==req.get('id'):return obj
                raise RuntimeError('SSE terminé sans réponse')
            return json.load(response)
    def close(self):pass

class LegacySSE:
    """Connexion legacy gardée au relais ; le client commun reste Streamable HTTP."""
    def __init__(self,url,headers=None):
        HTTP(url,headers) # validation boucle locale et exclusion ports quotidiens
        self.url=url;self.headers=headers or {};self.endpoint=None;self.ready=threading.Event();self.q=queue.Queue();self.lock=threading.Lock();self.error=None
        self.response=urllib.request.urlopen(urllib.request.Request(url,headers={'Accept':'text/event-stream',**self.headers}),timeout=60)
        threading.Thread(target=self._reader,daemon=True).start()
        if not self.ready.wait(10):raise TimeoutError('SSE endpoint non reçu')
        if self.error:raise RuntimeError(self.error)
    def _reader(self):
        from urllib.parse import urljoin,urlparse
        event='';lines=[]
        try:
            for raw in self.response:
                line=raw.decode('utf-8').rstrip('\r\n')
                if line.startswith('event:'):event=line[6:].strip()
                elif line.startswith('data:'):lines.append(line[5:].lstrip())
                elif not line and lines:
                    payload='\n'.join(lines);lines=[]
                    if event=='endpoint':
                        endpoint=urljoin(self.url,payload);a,b=urlparse(self.url),urlparse(endpoint)
                        if (a.scheme,a.hostname,a.port)!=(b.scheme,b.hostname,b.port):raise ValueError('Endpoint SSE hors amont')
                        self.endpoint=endpoint;self.ready.set()
                    elif event in ('message',''):self.q.put(json.loads(payload))
                    event=''
        except Exception as e:self.error=str(e);self.ready.set();self.q.put(None)
    def rpc(self,req):
        with self.lock:
            r=urllib.request.Request(self.endpoint,data=json.dumps(req).encode(),headers={'Content-Type':'application/json',**self.headers})
            with urllib.request.urlopen(r,timeout=60) as response:response.read()
            if 'id' not in req:return None
            end=time.monotonic()+60
            while time.monotonic()<end:
                guard();obj=self.q.get(timeout=max(.1,end-time.monotonic()))
                if obj is None:raise RuntimeError(self.error)
                if obj.get('id')==req['id']:return obj
            raise TimeoutError('SSE réponse manquante')
    def close(self):
        # Le thread est daemon ; fermer le flux peut être bloquant tant qu'il lit, shutdown socket d'abord.
        try:self.response.fp.raw._sock.shutdown(socket.SHUT_RDWR)
        except (AttributeError,OSError):pass
        threading.Thread(target=self.response.close,daemon=True).start()

class Relay:
    def __init__(self,upstream,vault,task,out,adapter,ui=None,initialization=None):
        self.upstream=upstream;self.vault=scoped(vault);self.task=task;self.out=scoped(out);self.out.mkdir(parents=True,exist_ok=True)
        self.adapter=adapter;self.ui=ui;self.events=[];self.injected=False;self.lost=False;self.lock=threading.Lock();self.first_done=False;self.pending_first=False;self.first_lock=threading.Lock()
        self.before=snapshot(vault);writej(self.out/'before.json',self.before)
        self.human=self.first=self.cut=None
        self.initial_read=None
        self.initialization=initialization
        self.safety_check=lambda:None
        self.held_since=None;self.held_seconds=0
    def budget_extension(self):
        return min(60,self.held_seconds+(time.monotonic()-self.held_since if self.held_since is not None else 0))
    def event(self,name,**fields):
        value={'event':name,'seq':len(self.events)+1,'monotonic_ns':time.monotonic_ns(),'utc':time.time(),**fields};self.events.append(value)
        with (self.out/'events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(value,ensure_ascii=False)+'\n')
    def capture(self,name):
        snap=snapshot(self.vault);writej(self.out/f'{name}.json',snap);return snap
    def first_snapshot(self):
        with self.first_lock:
            if self.first is None:
                self.first=self.capture('first');self.event('first_snapshot',snapshot_sha256=manifest(self.first)['tree_sha256'])
            self.pending_first=False
    def result_object(self,reply):
        try:return json.loads(reply['result']['content'][0]['text'])
        except (KeyError,TypeError,ValueError,IndexError):return {}
    def observe_first(self):
        rel=N if self.task=='T5' else P;expected=data(self.human,rel);end=time.monotonic()+60
        while self.pending_first and time.monotonic()<end:
            guard();p=self.vault/rel
            if not p.exists() or p.read_bytes()!=expected:self.first_snapshot();return
            time.sleep(.005)
    def process(self,req,disconnect=None):
        with self.lock:
            guard()
            self.safety_check()
            if self.initialization is not None and req.get('method')=='initialize':
                reply=dict(self.initialization,id=req.get('id'));self.event('bootstrap_response',id=req.get('id'))
                self.event('response_delivered',id=req.get('id'));return reply,False
            if self.initialization is not None and req.get('method')=='notifications/initialized':return None,False
            if self.lost:
                self.event('client_reconnected',id=req.get('id'));self.lost=False
            call=req.get('method')=='tools/call';params=req.get('params',{});name=params.get('name');args=params.get('arguments',{})
            if call:self.event('tool_request',id=req.get('id'),tool=name,arguments_sha256=sha(json.dumps(args,ensure_ascii=False,sort_keys=True).encode()))
            def matches(rules):
                for rule in rules:
                    try:
                        if rule['tool']==name and field(args,rule['key']) in rule['values']:return True
                    except (KeyError,TypeError):continue
                return False
            preparation=call and (name in self.adapter.get('preparation_tools',[]) or matches(self.adapter.get('preparation_rules',[])))
            mutation=call and not preparation and (name in self.adapter['mutation_tools'] or matches(self.adapter.get('mutation_rules',[])))
            read=call and (name in self.adapter['read_tools'] or matches(self.adapter.get('read_rules',[])))
            if self.pending_first and mutation:
                rel=N if self.task=='T5' else P
                if (self.vault/rel).read_bytes()!=data(self.human,rel):self.first_snapshot()
                else:raise RuntimeError('Première mutation différée non réglée : ne pas permettre une réparation sans preuve')
            digest=sha(json.dumps(req,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
            selected=(mutation and not self.injected and self.task in ('T5','T6','T7','T8')) or (
                self.task=='T7b' and not self.injected and (preparation or mutation))
            if selected:
                if self.task=='T7b':
                    if self.initial_read is None:raise RuntimeError('T7b : aucune lecture MCP de P livrée avant plan/écriture')
                    if not read_matches(self.initial_read,(self.vault/P).read_bytes()):raise RuntimeError('T7b : disque divergent avant injection')
                self.injected=True
                if self.task!='T8':
                    self.event('request_held',id=req.get('id'),request_sha256=digest)
                    if self.ui is None:raise RuntimeError('Aucune retouche UI qualifiée configurée')
                    self.held_since=time.monotonic()
                    try:self.ui(self.task)
                    finally:self.held_seconds+=time.monotonic()-self.held_since;self.held_since=None
                    self.human=self.capture('human');self.event('ui_disk_verified',snapshot_sha256=manifest(self.human)['tree_sha256'])
                self.safety_check()
                self.event('dispatch',id=req.get('id'),request_sha256=digest,kind='preparation' if preparation else 'mutation')
            elif mutation:self.event('mutation_dispatch',id=req.get('id'),request_sha256=digest)
            observe_mutation=mutation and self.injected and self.first is None and not self.pending_first and self.task in ('T5','T6','T7','T7b')
            lost_errors=[];observer=None
            if selected and self.task=='T8':
                # Fermer le portillon de réponse AVANT dispatch effectif ; observer le disque en parallèle.
                self.event('response_held',id=req.get('id'),mode='response_gate_closed')
                def observe_effect():
                    try:
                        expected=data(self.before,P)+EVENT.encode()+b'\n'
                        # Détecter l'effet métier ; les dates restent jugées séparément
                        # par l'oracle avec attribution FDM et hash de cette coupure.
                        deadline=time.monotonic()+60
                        while True:
                            guard();actual=(self.vault/P).read_bytes()
                            if actual==expected:break
                            try:
                                a,ab=split(actual);e,eb=split(expected)
                                for key in ('création','modification'):a.pop(key,None);e.pop(key,None)
                                if a==e and ab==eb:break
                            except (ValueError,yaml.YAMLError,UnicodeError):pass
                            if time.monotonic()>=deadline:raise TimeoutError('Effet T8 non observé')
                            time.sleep(.005)
                        self.cut=self.capture('cut');self.event('effect_disk_verified',snapshot_sha256=manifest(self.cut)['tree_sha256'])
                        if disconnect:disconnect()
                        self.event('client_disconnected',id=req.get('id'));self.lost=True
                    except BaseException as e:lost_errors.append(e)
                observer=threading.Thread(target=observe_effect,daemon=True);observer.start()
            upstream_start=time.monotonic();reply=self.upstream.rpc(req)
            if call:self.event('upstream_response',id=req.get('id'),tool=name,duration_s=time.monotonic()-upstream_start,
                               bytes=len(json.dumps(reply,ensure_ascii=False).encode()),is_error=bool(reply.get('error') or reply.get('result',{}).get('isError')) if reply else None)
            if (read or mutation or preparation) and reply and not reply.get('error') and not reply.get('result',{}).get('isError'):
                try:
                    rel=field(args,self.adapter.get('read_mappings',{}).get(name,{}).get('path_key',self.adapter.get('path_key','path')))
                    if isinstance(rel,str) and rel.endswith('.md'):
                        self.event('candidate_note_access',id=req.get('id'),path=rel,response_received=True)
                except (KeyError,TypeError):pass
            writej(self.out/f'rpc-{len(self.events):04}-{req.get("id","notification")}.json',{'request':req,'response':reply})
            if mutation and self.adapter.get('technical_receipts_policy')=='c08-transactions-v1':
                try:
                    obj=reply['result']['structuredContent']['data']
                    self.event('technical_transaction_receipt',id=req.get('id'),path=args['path'],
                               transaction_id_sha256=sha(obj['transaction_id'].encode()))
                except (KeyError,TypeError,AttributeError):pass
            if selected and self.task=='T8':
                observer.join(timeout=61)
                if observer.is_alive():raise TimeoutError('Observation effet T8 non terminée')
                if lost_errors:raise lost_errors[0]
                return None,True
            if observe_mutation:
                obj=self.result_object(reply);state=obj.get(self.adapter.get('status_state_key','state'),obj.get('status'))
                if state in self.adapter.get('pending_states',['pending','accepted','running']):
                    self.pending_first=True;self.event('first_mutation_pending',id=req.get('id'))
                    threading.Thread(target=self.observe_first,daemon=True).start()
                else:self.first_snapshot()
            if self.pending_first and call and name in self.adapter.get('status_tools',[]):
                state=self.result_object(reply).get(self.adapter.get('status_state_key','state'))
                if state in self.adapter.get('terminal_states',['committed','verified','conflict','rejected','failed']):self.first_snapshot()
            if read and reply and not reply.get('error') and not reply.get('result',{}).get('isError'):
                try:
                    mapping=self.adapter.get('read_mappings',{}).get(name,{})
                    form=mapping.get('format',self.adapter.get('read_format','json'))
                    raw=reply['result']['content'][0]['text']
                    obj=reply['result']['structuredContent'] if mapping.get('source')=='structuredContent' else json.loads(raw) if form not in ('raw','numbered_lines') else None
                    # Mapping explicite ; jamais lecture disque fabriquée comme relecture MCP.
                    content=raw if obj is None else obj if form=='json_string' else field(obj,mapping.get('content_key',self.adapter.get('read_content_key','content')))
                    if form=='numbered_lines':content=decode_numbered(content)
                    rel=field(args,mapping.get('path_key',self.adapter.get('path_key','path')))
                    projection=({'projection':'body_frontmatter','properties':field(obj,mapping['frontmatter_key']),'body_sha256':sha(content.encode())}
                                if form=='body_frontmatter' else {'content_sha256':sha(content.encode())})
                    self.event('mcp_read_response',id=req.get('id'),path=rel,**projection,response_received=True)
                    if self.task=='T7b' and not self.injected and rel==P:
                        self.initial_read={'id':req.get('id'),**projection}
                        self.event('agent_read_delivered',**self.initial_read)
                except (KeyError,ValueError,TypeError,IndexError):self.event('readback_unmapped',id=req.get('id'))
            if reply:self.event('response_delivered',id=req.get('id'))
            return reply,False

    def finish(self):
        # Refus au plan : aucune mutation n'a été envoyée. État terminal conservé,
        # distinct d'un snapshot pris après une vraie mutation.
        if self.task=='T7b' and self.injected and self.first is None:
            if self.pending_first:raise RuntimeError('Mutation T7b encore indéterminée')
            self.first_snapshot();self.event('no_mutation_after_preparation')

def serve(relay,port):
    if port in (27123,27124):raise ValueError('Port quotidien interdit')
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            try:
                def disconnect():
                    try:self.connection.shutdown(socket.SHUT_RDWR)
                    except OSError:pass
                    self.connection.close()
                req=json.loads(self.rfile.read(int(self.headers['Content-Length'])));reply,drop=relay.process(req,disconnect)
                if drop:
                    disconnect();return
                if reply is None:self.send_response(202);self.end_headers();return
                payload=json.dumps(reply,ensure_ascii=False).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
            except BaseException as e:
                relay.event('relay_error',error=str(e));self.send_error(503,'Relay stopped: inspect private log')
    return ThreadingHTTPServer(('127.0.0.1',port),Handler)

def editor_hook(config):
    def apply(task):
        cfg=readj(config);vault=Path(cfg['vault'])
        if task=='T5':
            r=subprocess.run(['node',str(KIT/'scripts'/'ui_cdp.mjs'),str(config),'inject',task],capture_output=True,text=True,encoding='utf-8',timeout=30)
            if r.returncode:raise RuntimeError(r.stderr)
            wait_bytes(vault/N,json.loads(r.stdout)['expected'].encode());return
        source=(vault/P).read_text(encoding='utf-8');old,new=(HOLD,HNEW) if task=='T6' else (OLD,CONFLICT)
        if source.count(old)!=1:raise ValueError('Injection non unique')
        offset=len(source[:source.index(old)].encode('utf-16-le'))//2
        r=subprocess.run(['node',str(KIT/'scripts'/'retouche-editeur.mjs'),'--port',str(cfg['port']),
            '--vault',str(vault),'--note',P,'--position',str(offset),'--delete-length',str(len(old)),
            '--text',new,'--expected-before-sha256',sha(source.encode())],capture_output=True,text=True,encoding='utf-8',timeout=65)
        if r.returncode:raise RuntimeError(r.stderr)
    return apply

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);a=p.parse_args();cfg=readj(a.config)
    upstream=Stdio(cfg['command'],cfg.get('cwd'),KIT/'preuves'/'upstream-stderr.log') if cfg['transport']=='stdio' else LegacySSE(cfg['url']) if cfg['transport']=='sse' else HTTP(cfg['url'])
    relay=Relay(upstream,cfg['vault'],cfg['task'],cfg['out'],cfg['adapter'],editor_hook(cfg['ui_config']) if cfg.get('ui_config') else None)
    server=serve(relay,cfg['port'])
    try:server.serve_forever(poll_interval=.2)
    finally:server.server_close();upstream.close()
