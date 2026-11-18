#!/usr/bin/env python3
"""BanglaMed round 2: retry the names that found no match, using cleaned queries.
Usage: set UMLS_API_KEY (same as before), keep umls_cache.json in the folder, then:
       python umls_map2.py umls_round2_inputs.csv
Writes umls_round2.csv (and prints a summary). Needs: pip install requests"""
import csv,json,os,sys,time
import requests
KEY=os.environ.get('UMLS_API_KEY')
if not KEY: sys.exit('Set the UMLS_API_KEY environment variable first.')
BASE='https://uts-ws.nlm.nih.gov/rest'; CACHE='umls_cache.json'
cache=json.load(open(CACHE,encoding='utf-8')) if os.path.exists(CACHE) else {}
S=requests.Session()
def get(url,params):
    key=url+'?'+'&'.join(f'{k}={params[k]}' for k in sorted(params))
    if key in cache and cache[key]!='ERROR': return cache[key]
    p=dict(params,apiKey=KEY)
    for a in range(4):
        try:
            r=S.get(url,params=p,timeout=30)
            if r.status_code==404: cache[key]=None; return None
            if r.status_code in(429,500,502,503): time.sleep(2+a*3); continue
            if r.status_code in(401,403): sys.exit(f'API key rejected ({r.status_code}).')
            r.raise_for_status(); cache[key]=r.json(); time.sleep(0.06); return cache[key]
        except requests.RequestException: time.sleep(2+a*3)
    return None
def search(term,sabs,stype):
    j=get(BASE+'/search/current',{'string':term,'sabs':sabs,'returnIdType':'concept','searchType':stype,'pageSize':5})
    if not j: return []
    return [x for x in j.get('result',{}).get('results',[]) if x.get('ui') and x['ui']!='NONE']
def codes(cui,sab,ttys):
    j=get(f'{BASE}/content/current/CUI/{cui}/atoms',{'sabs':sab,'ttys':ttys,'pageSize':25})
    out=[]
    for a in (j or {}).get('result',[]) if j else []:
        c=(a.get('code') or '').rstrip('/').split('/')[-1]
        if c and c not in out: out.append(c)
    return out
def concept(cui):
    j=get(f'{BASE}/content/current/CUI/{cui}',{})
    res=(j or {}).get('result',{}) if j else {}
    return res.get('name',''),'; '.join(s['name'] for s in res.get('semanticTypes',[]))
SABS={'drug':'RXNORM,ATC','drug_or_class':'MSH,ATC,MTH,NCI,SNOMEDCT_US','condition':'MSH,SNOMEDCT_US,MTH'}
CODES={'drug':(('RXNORM','IN,PIN,MIN,BN'),('ATC','PT,IN')),'drug_or_class':(('MSH','MH,PEP,NM'),('ATC','PT,IN')),'condition':(('MSH','MH,PEP,NM'),('SNOMEDCT_US','PT'))}
def find(qs,kind):
    for stype in('normalizedString','words'):
        for q in qs:
            if stype=='words' and q!=qs[0]: continue
            r=search(q,SABS[kind],stype)
            if r:
                top=r[0]; m='exact' if top['name'].lower()==q.lower() else 'close'
                return top,m,q,stype
    return None,'none',qs[0] if qs else '',''
rows=list(csv.DictReader(open(sys.argv[1],encoding='utf-8-sig'))); out=[]
for n,r in enumerate(rows,1):
    kind=r['kind']; d=dict(kind=kind,input=r['name'],n_claims=r['n_claims'],query_used='',match='none',cui='',umls_name='',code1='',code2='',semtype='',needs_review='')
    (s1,t1),(s2,t2)=CODES[kind]
    if r['force_cui']:
        nm,st=concept(r['force_cui'])
        if nm: d.update(match='forced',cui=r['force_cui'],umls_name=nm,semtype=st,code1=';'.join(codes(r['force_cui'],s1,t1)),code2=';'.join(codes(r['force_cui'],s2,t2)),needs_review='check forced name')
        else: d['needs_review']='forced CUI not found'
    elif r['queries']:
        parts=r['queries'].split('|')
        if kind=='drug' and '+' in parts[0]:   # combination: map each component
            comps=parts[0].split('+'); hits=[]
            for c in comps:
                top,m,q,st=find([c.strip()],'drug')
                if top: hits.append((top,m))
            if hits:
                d.update(match='components' if len(hits)==len(comps) else 'partial',query_used=parts[0],cui=';'.join(h[0]['ui'] for h in hits),umls_name=';'.join(h[0]['name'] for h in hits),needs_review='combination: check components')
                d['code1']=';'.join(c for h in hits for c in codes(h[0]['ui'],s1,t1)[:1])
        else:
            top,m,q,st=find(parts,kind)
            if top:
                cui=top['ui']; nm,stt=concept(cui)
                d.update(match=m,query_used=q+(' [words]' if st=='words' else ''),cui=cui,umls_name=top['name'],semtype=stt,code1=';'.join(codes(cui,s1,t1)),code2=';'.join(codes(cui,s2,t2)))
                if m!='exact' or st=='words': d['needs_review']='inexact'
            else: d['query_used']=parts[0]; d['needs_review']='no match'
    else: d['needs_review']='no query'
    out.append(d)
    if n%25==0:
        print(f'{n}/{len(rows)}',flush=True); json.dump(cache,open(CACHE,'w',encoding='utf-8'),ensure_ascii=False)
json.dump(cache,open(CACHE,'w',encoding='utf-8'),ensure_ascii=False)
cols=['kind','input','n_claims','query_used','match','cui','umls_name','code1','code2','semtype','needs_review']
with open('umls_round2.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(out)
import collections
print('DONE:',len(out),dict(collections.Counter(x['match'] for x in out)))
