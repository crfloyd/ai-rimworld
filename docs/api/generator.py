def main():
    import collections, hashlib, json, pathlib
    import argparse
    parser=argparse.ArgumentParser(description='Inventory captured RimMolt inputs, observed output shapes, and decompiled handler mappings; no game calls.')
    parser.add_argument('--project-root', '--root', dest='project_root', type=pathlib.Path, required=True)
    parser.add_argument('--source-root', '--source', dest='source_root', type=pathlib.Path, required=True)
    parser.add_argument('--output-dir', '--out', dest='output_dir', type=pathlib.Path, required=True)
    opts=parser.parse_args()
    ROOT=opts.project_root.resolve()
    RUN=ROOT/'campaigns/continuance'
    OUT=opts.output_dir.resolve()
    OUT.mkdir(parents=True,exist_ok=True)
    def dump(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
    catalog_path=RUN/'raw/catalog.json'; cat=json.loads(catalog_path.read_text())
    inputs={n:{k:v for k,v in t.items()} for n,t in cat['tools'].items()}
    records=[]; sources=[]
    for rel in ['reference/legacy/history.jsonl','reference/lab/runner-calls.jsonl','reference/lab/calls.jsonl']:
     p=RUN/rel;sources.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p)})
     for i,line in enumerate(p.read_text().splitlines(),1):
      r=json.loads(line); records.append((r,str(p.relative_to(ROOT))+':'+str(i)))
    for p in sorted((RUN/'raw').glob('obs-*.json')):
     sources.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p)}); records.append((json.loads(p.read_text()),str(p.relative_to(ROOT))))
    def decode(x):
     if isinstance(x,str):
      try:return decode(json.loads(x))
      except json.JSONDecodeError:return x
     if isinstance(x,dict) and 'jsonrpc' in x:
      if 'error'in x:return {'_jsonRpcError':x['error']}
      return decode(x.get('result'))
     if isinstance(x,dict) and 'content'in x and isinstance(x['content'],list):
      text=[decode(v['text']) for v in x['content'] if v.get('type')=='text' and 'text'in v]
      if len(text)==1:return text[0]
      return {'_mcpContent':text,'_mcpIsError':x.get('isError')}
     return x
    def typ(x):
     return 'null' if x is None else 'boolean' if isinstance(x,bool) else 'object' if isinstance(x,dict) else 'array' if isinstance(x,list) else 'number' if isinstance(x,float) else 'integer' if isinstance(x,int) else 'string'
    def walk(x,p='$'):
     yield p,typ(x)
     if isinstance(x,dict):
      for k,v in x.items(): yield from walk(v,p+'/'+k.replace('~','~0').replace('/','~1'))
     elif isinstance(x,list):
      for v in x:yield from walk(v,p+'/*')
    def explicit_error(payload):
     if not isinstance(payload,dict):return False
     if payload.get('isError') is True:return True
     if 'jsonrpc'in payload:
      return 'error'in payload or explicit_error(payload.get('result'))
     return False
    by=collections.defaultdict(list); seen={}; rpc_fingerprints=collections.defaultdict(set); overlap=0; unknown=collections.Counter()
    for r,ref in records:
     n=r.get('tool'); payload=r.get('payload',r.get('response',r.get('result')))
     rpc=payload.get('id') if isinstance(payload,dict) and 'jsonrpc'in payload else None
     fingerprint=hashlib.sha256(json.dumps([n,r.get('args',{}),payload],sort_keys=True,separators=(',',':')).encode()).hexdigest()
     if rpc is not None:rpc_fingerprints[str(rpc)].add(fingerprint)
     key=('rpc',str(rpc),fingerprint) if rpc is not None else ('record',ref)
     if key in seen:
      seen[key]['provenance'].append(ref);overlap+=1;continue
     e={'tool':n,'args':r.get('args',{}),'data':decode(payload),'provenance':[ref],'rpc_id_available':rpc is not None,'mcp_or_rpc_error':explicit_error(payload)};seen[key]=e;by[n].append(e)
     if n not in inputs:unknown[n]+=1
    result={}
    for n,t in inputs.items():
     fields={};variants={};selectors={};errors=0
     for e in by[n]:
      d=e['data']; ps=set(walk(d))
      for path,tp in ps:
       f=fields.setdefault(path,{'types':collections.Counter(),'records_present':0,'example_provenance':e['provenance'][0]})
       f['types'][tp]+=1
      for path in {path for path,tp in ps}:fields[path]['records_present']+=1
      keys=sorted(d) if isinstance(d,dict) else []
      signature=json.dumps([typ(d),keys]);v=variants.setdefault(signature,{'root_type':typ(d),'top_level_keys':keys,'records':0,'example_provenance':e['provenance'][0]});v['records']+=1
      sel={k:e['args'][k] for k in ['tab','action','category','verbose','summary','detail','kind'] if k in e['args']}
      sk=json.dumps(sel,sort_keys=True);s=selectors.setdefault(sk,{'selectors':sel,'records':0,'example_provenance':e['provenance'][0]});s['records']+=1
      if e['mcp_or_rpc_error'] or (isinstance(d,dict) and (d.get('ok') is False or 'error'in d or '_jsonRpcError'in d)):errors+=1
     result[n]={'declared':t,'observed':{'unique_records':len(by[n]),'deduplication':'RPC id plus matching tool/arguments/full-payload SHA256; historical records without ids remain distinct','error_records_by_explicit_markers':errors,'root_variants':list(variants.values()),'query_selector_variants':list(selectors.values()),'field_paths':dict(sorted(fields.items())),'record_provenance':[e['provenance'] for e in by[n]]}}
    meta={'catalog':{'path':str(catalog_path.relative_to(ROOT)),'sha256':sha(catalog_path),'captured_at':cat.get('captured_at'),'server':cat.get('server'),'schema_digest':cat.get('schema_digest')},'tool_count':len(inputs),'declared_output_schema_count':sum('outputSchema'in t for t in inputs.values()),'corpus_input_records':len(records),'deduplicated_rpc_overlaps':overlap,'rpc_ids_with_conflicting_content':sum(len(v)>1 for v in rpc_fingerprints.values()),'unique_records':sum(map(len,by.values())),'observed_catalog_tools':sum(bool(by[n]) for n in inputs),'unobserved_catalog_tools':[n for n in inputs if not by[n]],'observed_non_catalog_tools':dict(unknown),'sources':sources}
    dump(OUT/'inventory.json',{'metadata':meta,'tools':result})
    lines=['# RimMolt captured API reference','','This inventory covers every tool in the captured catalog. Declared input schemas are complete copies; response models describe recorded evidence, not exhaustive contracts. No tool declares `outputSchema`. Dynamic menus, mods, DLC, state, compact/verbose modes, errors, and future versions can introduce unobserved output variants.','','The machine-readable companion `inventory.json` contains full declarations, all observed nested field paths and JSON types, per-field presence counts, query selectors, root-key variants, and source file/line pointers. Array elements use `/*`; object property names use JSON Pointer escaping. Field counts count records containing a path, not array elements. A type count counts records with that type at the path; heterogeneous arrays can contribute multiple types.','','Corpus overlap is deduplicated only when an actual JSON-RPC response id and a matching tool/arguments/full-payload SHA256 exist. Conflicting content sharing an RPC id remains separate. Explicit MCP isError and JSON-RPC errors are counted even when the decoded payload is plain text. Historical records without response ids are distinct evidence records, not necessarily unique game actions. Bundled child results remain nested under their actual calling tool; they do not count as standalone observations of the child tool. Empty arrays reveal no element schema. Missing fields are not false or empty unless the tool contract explicitly says so.','','Do not load this whole reference during routine play. Use the index to retrieve the relevant tool section or machine-readable entry. Full raw records remain the authority for interpreting returned values.','','## Coverage','','- Catalog tools: '+str(len(inputs))+'.','- Tools with standalone observed responses: '+str(meta['observed_catalog_tools'])+'.','- Tools without standalone observed responses: '+str(len(meta['unobserved_catalog_tools']))+'.','- Evidence records after identified RPC overlap removal: '+str(meta['unique_records'])+' ('+str(overlap)+' duplicate RPC references merged).','','## Index','']
    lines += ['- ['+n+'](#'+n.replace('_','-')+')' for n in inputs]
    for n,e in result.items():
     t=e['declared'];o=e['observed'];lines += ['', '## '+n,'',t.get('description',''),'', '### Declared input schema','','```json',json.dumps(t.get('inputSchema'),indent=2,ensure_ascii=False),'```','','Output schema: **not declared**.']
     lines+=['','### Observed response evidence','',f"Standalone evidence records: **{o['unique_records']}**. Explicit error-marker records: **{o['error_records_by_explicit_markers']}**."]
     if not o['unique_records']:lines+=['','No standalone response captured. Its response model remains unobserved.']
     else:
      lines+=['','Root-key variants (counts are evidence records):','']
      for v in o['root_variants']:lines+=['- '+str(v['records'])+' × `'+v['root_type']+'` with keys: '+(', '.join('`'+x+'`' for x in v['top_level_keys']) or '(none)')+'. Example: `'+v['example_provenance']+'`.']
      lines+=['','Observed selector combinations: '+', '.join('`'+json.dumps(s['selectors'],sort_keys=True)+'` ('+str(s['records'])+')' for s in o['query_selector_variants'])+'.', '',f"All **{len(o['field_paths'])}** nested observed paths, type counts and provenance are in `inventory.json` → `tools.{n}.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness."]
    (OUT/'API-REFERENCE.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in meta.items() if k not in ['sources','catalog']},indent=2)); print('bytes',[(p.name,p.stat().st_size) for p in OUT.iterdir()])

    import pathlib,re,json,hashlib
    P=opts.source_root.resolve();O=OUT
    def mask(s):
     return re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|@"(?:""|[^"])*"|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',lambda m:''.join('\n' if x=='\n' else ' ' for x in m[0]),s)
    def balanced(m,a):
     level=0
     for i in range(a,len(m)):
      if m[i]=='{':level+=1
      elif m[i]=='}':
       level-=1
       if level==0:return i+1
     raise ValueError(a)
    def line(s,a):return s[:a].count('\n')+1
    entries={}; sourcefiles={};methods={}
    for p in sorted(P.glob('RimMolt.Tools/*.cs')):
     s=p.read_text();m=mask(s);rel=str(p.relative_to(P));sourcefiles[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
     for z in re.finditer(r'\b(?:public|private|internal)\s+(?:unsafe\s+)?static\s+[^\n=;]+?\s+(\w+)\s*\([^;]*?\)\s*\{',m):
      a=m.find('{',z.start());b=balanced(m,a);methods[(rel,z[1])]=(s[a:b],line(s,z.start()))
     for z in re.finditer(r'new\s+ToolRegistry\.ToolDef\s*\{',m):
      a=m.find('{',z.start());b=balanced(m,a);body=s[a:b];n=re.search(r'\bName\s*=\s*"([^"]+)"',body)
      if not n:continue
      h=re.search(r'\b(Collect|Background)\s*=\s*(?:\([^)]*\)\s*=>\s*)?(\w+)',body)
      aliases=re.search(r'Aliases\s*=\s*new List<string>\s*\{([^}]*)\}',body)
      entries[n[1]]={'registration_file':rel,'registration_line':line(s,z.start()),'handler_kind':h[1] if h else None,'handler':h[2] if h else None,'aliases':re.findall(r'"([^"]+)"',aliases[1]) if aliases else [],'explicit_large_output_guard':'LargeOutputGuard = true' in body,'provenance':'automated static extraction from ILSpy-decompiled installed DLL; not original authored source'}
    x=json.loads((O/'inventory.json').read_text())
    for n,t in x['tools'].items():
     e=entries.get(n)
     if e:
      body,ln=methods.get((e['registration_file'],e['handler']),('',None)); e['handler_line']=ln
      e['handler_body_literal_index_keys']=sorted(set(re.findall(r'\["([^"]+)"\]\s*=',body)))
      e['handler_body_call_names']=sorted(set(re.findall(r'\b([A-Za-z_]\w*(?:\.\w+)*)\s*\(',mask(body))))
      e['handler_body_dlc_identifiers']=sorted(set(re.findall(r'ModsConfig\.\w+',body)))
      e['shape_status']='Literal assignment keys are navigation leads, not an output contract: helper calls, anonymous objects, dynamic dictionary keys, nested state, and wrappers require further review.'
     t['source']=e or {'status':'not mapped'}
    x['metadata']['source_mapping']={'method':'static registration and same-file method extraction; not branch-complete response analysis','mapped_catalog_tools':sum(n in entries for n in x['tools']),'unmapped_catalog_tools':[n for n in x['tools'] if n not in entries],'source_only_registrations':[n for n in entries if n not in x['tools']],'source_file_sha256':sourcefiles}
    (O/'inventory.json').write_text(json.dumps(x,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    ref=(O/'API-REFERENCE.md').read_text()
    for n,t in x['tools'].items():
     e=t['source'];target='## '+n+'\n'
     if 'registration_file'in e:
      note='\nSource mapping (automatically extracted from decompiled DLL): ['+e['registration_file']+'](evidence/decompiled/'+e['registration_file']+') registration line '+str(e['registration_line'])+' → `'+str(e['handler_kind'])+' = '+str(e['handler'])+'` (method line '+str(e['handler_line'])+').'
      if e['aliases']:note+=' Registered aliases: '+', '.join('`'+a+'`' for a in e['aliases'])+'.'
      note+=' This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.\n'
      ref=ref.replace(target,target+note)
    for n in x['tools']:ref=ref.replace('](#'+n.replace('_','-')+')','](#'+n+')')
    (O/'API-REFERENCE.md').write_text(ref)
    print(json.dumps({k:v for k,v in x['metadata']['source_mapping'].items() if k!='source_file_sha256'},indent=2))

if __name__ == '__main__':
    main()
