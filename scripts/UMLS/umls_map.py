#!/usr/bin/env python3
"""BanglaMed: map drug and condition names to UMLS concepts and source codes.
Usage:  set UMLS_API_KEY=<your key>   (Windows: set UMLS_API_KEY=... ; Mac/Linux: export UMLS_API_KEY=...)
        python umls_map.py umls_inputs.csv
Resumes automatically (cache in umls_cache.json). Needs: pip install requests"""
import csv,json,os,re,sys,time
import requests
KEY=os.environ.get('UMLS_API_KEY')
if not KEY: sys.exit('Set the UMLS_API_KEY environment variable first.')
BASE='https://uts-ws.nlm.nih.gov/rest'
CACHE='umls_cache.json'
cache=json.load(open(CACHE,encoding='utf-8')) if os.path.exists(CACHE) else {}
S=requests.Session()
def get(url,params):
    key=url+'?'+'&'.join(f'{k}={params[k]}' for k in sorted(params))
    if key in cache: return cache[key]
    params=dict(params,apiKey=KEY)
    for attempt in range(4):
        try:
            r=S.get(url,params=params,timeout=30)
            if r.status_code==404: cache[key]=None; return None
            if r.status_code in(429,500,502,503): time.sleep(2+attempt*3); continue
            if r.status_code in(401,403): sys.exit(f'API key rejected ({r.status_code}). Check UMLS_API_KEY and that your licence is active.')
            r.raise_for_status(); cache[key]=r.json(); time.sleep(0.06); return cache[key]
        except requests.RequestException as e:
            time.sleep(2+attempt*3)
    cache[key]='ERROR'; return 'ERROR'
def search(term,sabs):
    j=get(BASE+'/search/current',{'string':term,'sabs':sabs,'returnIdType':'concept','searchType':'normalizedString','pageSize':5})
    if not j or j=='ERROR': return []
    res=j.get('result',{}).get('results',[])
    return [x for x in res if x.get('ui') and x['ui']!='NONE']
def codes(cui,sab,ttys):
    j=get(f'{BASE}/content/current/CUI/{cui}/atoms',{'sabs':sab,'ttys':ttys,'pageSize':25})
    if not j or j=='ERROR': return []
    out=[]
    for a in j.get('result',[]):
        code=(a.get('code') or '').rstrip('/').split('/')[-1]
        if code and code not in out: out.append(code)
    return out
def semtypes(cui):
    j=get(f'{BASE}/content/current/CUI/{cui}',{})
    if not j or j=='ERROR': return ''
    return '; '.join(s['name'] for s in j.get('result',{}).get('semanticTypes',[]))
SALTS=r'\b(hydrochloride|hcl|sodium|potassium|calcium|sulfate|sulphate|acetate|maleate|tartrate|citrate|phosphate|succinate|besylate|mesylate|dihydrate|trihydrate|monohydrate|oral|micronised|capsule|vaginal|gel|pessary|tablet|injection|\d+|mg|g)\b'
def drug_terms(slug):
    full=slug.replace('-',' ')
    stripped=re.sub(r'\s+',' ',re.sub(SALTS,' ',full)).strip()
    t=[full]
    if stripped and stripped!=full: t.append(stripped)
    return t
def best(terms,sabs):
    for i,t in enumerate(terms):
        r=search(t,sabs)
        if r:
            top=r[0]; exact=top['name'].lower()==t.lower()
            return top,('exact' if exact else 'close'),t
    return None,'none',terms[0]
rows=list(csv.DictReader(open(sys.argv[1],encoding='utf-8-sig')))
outD=[];outC=[]
for n,r in enumerate(rows,1):
    kind,name=r['kind'],r['name']
    if kind in('drug','drug_or_class'):
        terms=drug_terms(name) if kind=='drug' else [name]
        top,mt,used=best(terms,'RXNORM,ATC')
        d=dict(kind=kind,input=name,n_claims=r['n_claims'],query_used=used,match=mt,cui='',umls_name='',rxnorm='',atc='',semtype='',needs_review='')
        if top:
            cui=top['ui']; d.update(cui=cui,umls_name=top['name'],rxnorm=';'.join(codes(cui,'RXNORM','IN,PIN,MIN,BN')),atc=';'.join(codes(cui,'ATC','PT,IN')),semtype=semtypes(cui))
        if kind=='drug' and ('-' in name and len(name.split('-'))>3 or mt!='exact'): d['needs_review']='combination or inexact'
        if mt=='none': d['needs_review']='no match'
        outD.append(d)
    else:
        top,mt,used=best([name],'MSH,SNOMEDCT_US,MTH')
        d=dict(kind=kind,input=name,n_claims=r['n_claims'],query_used=used,match=mt,cui='',umls_name='',mesh='',snomed='',semtype='',needs_review='')
        if top:
            cui=top['ui']; d.update(cui=cui,umls_name=top['name'],mesh=';'.join(codes(cui,'MSH','MH,PEP,NM')),snomed=';'.join(codes(cui,'SNOMEDCT_US','PT')[:3]),semtype=semtypes(cui))
        if mt!='exact': d['needs_review']='inexact' if mt=='close' else 'no match'
        outC.append(d)
    if n%25==0:
        print(f'{n}/{len(rows)}',flush=True); json.dump(cache,open(CACHE,'w',encoding='utf-8'),ensure_ascii=False)
json.dump(cache,open(CACHE,'w',encoding='utf-8'),ensure_ascii=False)
def dump(fn,L,cols):
    with open(fn,'w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(L)
dump('umls_drugs.csv',outD,['kind','input','n_claims','query_used','match','cui','umls_name','rxnorm','atc','semtype','needs_review'])
dump('umls_conditions.csv',outC,['kind','input','n_claims','query_used','match','cui','umls_name','mesh','snomed','semtype','needs_review'])
allr=outD+outC; rev=[x for x in allr if x['needs_review']]
dump('umls_review.csv',rev,['kind','input','n_claims','query_used','match','cui','umls_name','needs_review'])
print('DONE:',len(allr),'names;',sum(1 for x in allr if x['match']=='exact'),'exact;',sum(1 for x in allr if x['match']=='close'),'close;',sum(1 for x in allr if x['match']=='none'),'none')
