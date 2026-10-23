"""Client commun préparé ; une configuration écrite n'est pas une qualification runtime."""
import shutil
import os
from campaign_runtime import *

FEATURES_OFF=['apps','plugins','multi_agent','multi_agent_v2','shell_tool','browser_use','browser_use_external',
              'browser_use_full_cdp_access','computer_use','in_app_browser','in_app_local_automation','image_generation',
              'view_image','code_mode','code_mode_host','memories','skill_search','tool_suggest','worktrees','goals','sleep_tool']

def make_config(out,enabled_tools,relay_port=27348,copy_auth=True):
    out=scoped(out);home=out/'codex-home';cwd=out/'client';home.mkdir(parents=True,exist_ok=True);cwd.mkdir(exist_ok=True)
    if any(cwd.iterdir()):raise RuntimeError('Le contexte client initial doit être vide')
    if relay_port in (27123,27124):raise ValueError('Port quotidien interdit')
    user=Path(os.environ['USERPROFILE'])
    if copy_auth:
        # Copie autorisée pour le client de test, jamais affichée ni projetée.
        auth=user/'.codex/auth.json';assert auth.is_file();shutil.copyfile(auth,home/'auth.json')
    instructions='Utilise uniquement le MCP candidat. Aucun shell, accès disque direct, navigateur, eval, installation, autre serveur ou outil de plugins/workspaces. Préserve tout hors de la demande ; aucune écriture des champs création/modification. Les fiches techniques décrivent les outils, sans présumer leur réussite.'
    config='\n'.join(['approval_policy = "never"','sandbox_mode = "read-only"','web_search = "disabled"','model = "gpt-6.1-sol"',
        'model_provider = "openai"','model_reasoning_effort = "high"','service_tier = "default"','project_doc_max_bytes = 0',
        'developer_instructions = '+json.dumps(instructions,ensure_ascii=False),'[features]']+[f'{x} = false' for x in FEATURES_OFF])+'\n'
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

if __name__=='__main__':
    home,cwd=make_config(RUN/'client-calibration-preparation',['read','patch','append','create'],copy_auth=False)
    print(json.dumps({'config_prepared':True,'runtime_qualified':False,'auth_copied':False,'client_directory_empty':not any(cwd.iterdir())}))
