"""Client commun préparé ; une configuration écrite n'est pas une qualification runtime."""
import shutil
import os
from campaign_runtime import *

FEATURES_OFF=['apps','plugins','multi_agent','multi_agent_v2','shell_tool','browser_use','browser_use_external',
              'browser_use_full_cdp_access','computer_use','in_app_browser','in_app_local_automation','image_generation',
              'view_image','code_mode','memories','skill_search','tool_suggest','worktrees','goals','daemon_auto_start']

def make_config(out,enabled_tools,relay_port=27348,copy_auth=True):
    out=scoped(out);home=out/'codex-home';cwd=out/'client';home.mkdir(parents=True,exist_ok=True);cwd.mkdir(exist_ok=True)
    if any(cwd.iterdir()):raise RuntimeError('Le contexte client initial doit être vide')
    if relay_port in (27123,27124):raise ValueError('Port quotidien interdit')
    user=Path(os.environ['USERPROFILE'])
    if copy_auth:
        # Copie autorisée pour le client de test, jamais affichée ni projetée.
        auth=user/'.codex/auth.json';assert auth.is_file();shutil.copyfile(auth,home/'auth.json')
    instructions='Pour le coffre, utilise uniquement le MCP candidat. Aucun shell, accès disque direct, navigateur, eval, installation, autre serveur ou outil de plugins/workspaces. Un outil neutre d’attente est autorisé pour respecter une échéance de statut ; il ne lit ni n’écrit le coffre. Préserve tout hors de la demande ; aucune écriture des champs création/modification. Les fiches techniques décrivent les outils, sans présumer leur réussite.'
    config='\n'.join(['approval_policy = "never"','sandbox_mode = "read-only"','web_search = "disabled"','model = "gpt-6.1-sol"',
        'model_provider = "openai"','model_reasoning_effort = "high"','service_tier = "default"','project_doc_max_bytes = 0',
        'developer_instructions = '+json.dumps(instructions,ensure_ascii=False),'[windows]','sandbox = "unelevated"','[features]','sleep_tool = true','code_mode_host = true']+[f'{x} = false' for x in FEATURES_OFF])+'\n'
    for root in (user/'.agents/skills',user/'.codex/skills'):
        if root.exists():
            for path in sorted(root.rglob('SKILL.md')):
                config+='\n[[skills.config]]\npath = '+json.dumps(str(path),ensure_ascii=False)+'\nenabled = false\n'
    config+='\n[mcp_servers.candidate]\nurl = '+json.dumps(f'http://127.0.0.1:{relay_port}/mcp')+'\nenabled_tools = '+json.dumps(enabled_tools)+'\nstartup_timeout_sec = 60\ntool_timeout_sec = 120\ndefault_tools_approval_mode = "approve"\n'
    (home/'config.toml').write_text(config,encoding='utf-8',newline='')
    import tomllib
    parsed=tomllib.loads(config)
    assert parsed['service_tier']=='default' and parsed['features']['shell_tool'] is False
    assert set(parsed['mcp_servers'])=={'candidate'}
    proof={'cli_version':'0.160.1','model':parsed['model'],'provider':parsed['model_provider'],'effort':parsed['model_reasoning_effort'],
           'service_tier':parsed['service_tier'],'features_off':FEATURES_OFF,'config_sha256':sha(config.encode()),'enabled_tools':enabled_tools,
           'runtime_qualified':False,'official_reference':'https://learn.chatgpt.com/docs/config-file/config-reference'}
    writej(out/'client-config-proof.json',proof)
    return home,cwd

def executable():
    npm=Path(os.environ['APPDATA'])/'npm/node_modules/@openai/codex/node_modules/@openai/codex-win32-x64/vendor/x86_64-pc-windows-msvc/bin/codex.exe'
    if not npm.is_file():raise RuntimeError('Binaire Codex 0.160.1 à relocaliser, aucune substitution automatique')
    return npm

def run_turn(out,prompt,home,cwd,monitor,turn='01',resume=None,max_seconds=300,disconnect=None,budget_extension=None,injection_failed=None):
    import subprocess
    binary=executable();args=[str(binary),'exec']
    if resume:args+=['resume',resume]
    args+=['--json','--skip-git-repo-check','--output-last-message',str(out/(turn+'.final.json'))]
    if not resume:args+=['--color','never','-C',str(cwd),'-s','read-only']
    args+=[prompt];writej(out/(turn+'.command.json'),args)
    env=dict(os.environ,CODEX_HOME=str(home),PYTHONUTF8='1');start=time.monotonic();reason=None
    with (out/(turn+'.stdout.jsonl')).open('w',encoding='utf-8') as stdout,(out/(turn+'.stderr.txt')).open('w',encoding='utf-8') as stderr:
        proc=subprocess.Popen(args,env=env,cwd=cwd,stdout=stdout,stderr=stderr,stdin=subprocess.DEVNULL)
        record(out,'measurement_client_started',pid=proc.pid,turn=turn,binary_sha256=sha(binary.read_bytes()))
        while proc.poll() is None:
            if injection_failed is not None and injection_failed.is_set():reason='INJECTION_INVALIDE';break
            if monitor.stopped.is_set():reason='ARRET_MEMOIRE_SOUS_2GIO';break
            if disconnect is not None and disconnect.lost:reason='T8_REPLY_LOST';break
            if time.monotonic()-start>=max_seconds+(budget_extension() if budget_extension else 0):reason='BUDGET_5_MIN';break
            time.sleep(.2)
        if reason:
            proc.terminate()
            try:proc.wait(timeout=10)
            except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
    events=[]
    for line in (out/(turn+'.stdout.jsonl')).read_text(encoding='utf-8').splitlines():
        try:events.append(json.loads(line))
        except ValueError:pass
    forbidden=[e for e in events if e.get('item',{}).get('type') in ('command_execution','file_change','web_search')]
    thread=next((e.get('thread_id') for e in events if e.get('type')=='thread.started'),resume)
    result={'returncode':proc.returncode,'duration_s':time.monotonic()-start,'stop_reason':reason,'forbidden_tool_events':forbidden,'thread_id':thread,
            'usage':[e for e in events if e.get('type')=='turn.completed'],'errors':[e for e in events if e.get('type') in ('error','turn.failed')]}
    writej(out/(turn+'.exit.json'),result)
    return result

def effective_config(out,home,cwd):
    import subprocess,queue,threading
    env=dict(os.environ,CODEX_HOME=str(home));q=queue.Queue()
    with (out/'config-read.stderr.txt').open('w',encoding='utf-8') as err:
        p=subprocess.Popen([str(executable()),'app-server'],cwd=cwd,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,text=True,encoding='utf-8')
        def reader():
            for line in p.stdout:q.put(json.loads(line))
        threading.Thread(target=reader,daemon=True).start()
        try:
            def rpc(i,method,params):
                p.stdin.write(json.dumps({'id':i,'method':method,'params':params})+'\n');p.stdin.flush()
                deadline=time.monotonic()+30
                while time.monotonic()<deadline:
                    r=q.get(timeout=max(.1,deadline-time.monotonic()))
                    if r.get('id')==i:
                        if 'error' in r:raise RuntimeError(str(r['error']))
                        return r['result']
                raise TimeoutError(method)
            rpc(1,'initialize',{'clientInfo':{'name':'comparatif-config','version':'1.1'},'capabilities':{}})
            value=rpc(2,'config/read',{'includeLayers':False})['config']
            proof={k:value.get(k) for k in ('model','model_provider','model_reasoning_effort','service_tier','approval_policy','sandbox_mode','web_search','features','mcp_servers')}
            # Un seul serveur, sans clé dans cette configuration côté client.
            assert set(proof['mcp_servers'])=={'candidate'}
            assert proof['model']=='gpt-6.1-sol' and proof['model_reasoning_effort']=='high' and proof['service_tier']=='default'
            writej(out/'effective-config.json',proof);return proof
        finally:
            p.terminate()
            try:p.wait(timeout=5)
            except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)

if __name__=='__main__':
    home,cwd=make_config(RUN/'client-calibration-preparation',['read','patch','append','create'],copy_auth=False)
    print(json.dumps({'config_prepared':True,'runtime_qualified':False,'auth_copied':False,'client_directory_empty':not any(cwd.iterdir())}))
