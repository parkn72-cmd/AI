import csv, io, json, re, os, zipfile
from pathlib import Path
from datetime import datetime, timezone
from dart_client import DartClient
ROOT=Path(__file__).resolve().parents[1]
PERIODS={'annual':('11011','Annual',12),'half_year':('11012','Half-year',6),'quarterly_q1':('11013','Quarterly Q1',3),'quarterly_q3':('11014','Quarterly Q3',9)}
# Only exact IDs / normalized names within the appropriate statement; ambiguous names stay null.
SPECS={
 'assets':('BS',['ifrs-full_Assets'],['자산총계']),
 'liabilities':('BS',['ifrs-full_Liabilities'],['부채총계']),
 'equity':('BS',['ifrs-full_Equity'],['자본총계']),
 'current_assets':('BS',['ifrs-full_CurrentAssets'],['유동자산']),
 'current_liabilities':('BS',['ifrs-full_CurrentLiabilities'],['유동부채']),
 'cash':('BS',['ifrs-full_CashAndCashEquivalents'],['현금및현금성자산']),
 'revenue':('IS',['ifrs-full_Revenue','dart_Revenue'],['매출액','수익(매출액)','영업수익']),
 'operating_income':('IS',['dart_OperatingIncomeLoss'],['영업이익','영업이익(손실)']),
 'net_income':('IS',['ifrs-full_ProfitLoss'],['당기순이익','당기순이익(손실)','반기순이익','분기순이익','반기순이익(손실)','분기순이익(손실)']),
 'operating_cash_flow':('CF',['ifrs-full_CashFlowsFromUsedInOperatingActivities'],['영업활동현금흐름','영업활동으로인한현금흐름'])}
def number(v):
    if v is None or str(v).strip() in ('','-'): return None
    try: return int(str(v).replace(',','').replace(' ','').replace('(','-').replace(')','').replace('−','-'))
    except ValueError: return None

def norm(v): return re.sub(r'\s+','',v or '')
def extract(rows,category):
    m={}; provenance={}
    for key,(sj,ids,names) in SPECS.items():
        eligible=[r for r in rows if r.get('sj_div') in ([sj,'CIS'] if sj=='IS' else [sj])]
        cand=[r for r in eligible if r.get('account_id') in ids]
        if not cand: cand=[r for r in eligible if norm(r.get('account_nm')) in names]
        # IS precedes CIS when both have the exact same concept.
        if sj=='IS' and any(r.get('sj_div')=='IS' for r in cand): cand=[r for r in cand if r.get('sj_div')=='IS']
        values=set(); selected=[]
        for r in cand:
            currency=r.get('currency','KRW')
            if currency and currency!='KRW': raise RuntimeError('Non-KRW statement requires explicit currency handling')
            field='thstrm_add_amount' if sj in ('IS','CF') and category!='annual' else 'thstrm_amount'
            # Q1 has identical quarter and YTD; CF thstrm_amount is typically YTD.
            if number(r.get(field)) is None and (sj=='CF' or category=='quarterly_q1'): field='thstrm_amount'
            val=number(r.get(field))
            if val is not None: values.add(val); selected.append((r,field,val))
        m[key]=next(iter(values)) if len(values)==1 else None
        if m[key] is not None:
            r,field,val=selected[0]; provenance[key]={'account_id':r.get('account_id'),'account_nm':r.get('account_nm'),'field':field,'rcept_no':r.get('rcept_no')}
    return m,provenance

def ratios(m):
    def ratio(a,b):
        x,y=m.get(a),m.get(b)
        return round(x/y*100,2) if x is not None and y is not None and y>0 else None
    return {'debt_ratio':ratio('liabilities','equity'),'equity_ratio':ratio('equity','assets'),'current_ratio':ratio('current_assets','current_liabilities'),'operating_margin':ratio('operating_income','revenue'),'net_margin':ratio('net_income','revenue')}
def parse_report(d):
    name=d.get('report_nm',''); match=re.search(r'(사업보고서|반기보고서|분기보고서).*?\((\d{4})\.(\d{2})\)',name)
    if not match: return None
    kind,y,month=match.groups(); month=int(month)
    category='annual' if kind=='사업보고서' else 'half_year' if kind=='반기보고서' else {3:'quarterly_q1',9:'quarterly_q3'}.get(month)
    if not category: return None
    return {**d,'year':int(y),'category':category,'url':'https://dart.fss.or.kr/dsaf001/main.do?rcpNo='+d['rcept_no']}
def write_json(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True); tmp=p.with_suffix('.tmp'); tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8'); tmp.replace(p)

def main():
    cfg=json.loads((ROOT/'config.json').read_text(encoding='utf8')); client=DartClient(); corp=client.corp(cfg['stock_code'])
    raw=ROOT/'data/raw'; raw.mkdir(parents=True,exist_ok=True)
    now=datetime.now(timezone.utc); end=now.year
    reports=[]
    # A current filing/correction can refer to a much earlier fiscal year.
    for year in range(cfg['start_year'],end+1):
        reports.extend(x for d in client.disclosures(corp['corp_code'],year) if (x:=parse_report(d)) and x['year']>=cfg['start_year'])
    write_json(raw/'disclosure_index.json',reports)
    for d in reports:
        file=raw/'documents'/(d['rcept_no']+'.zip'); file.parent.mkdir(parents=True,exist_ok=True)
        if not file.exists(): file.write_bytes(client.document(d['rcept_no']))
    latest={}
    for d in reports:
        k=(d['year'],d['category'])
        if k not in latest or d['rcept_no']>latest[k]['rcept_no']: latest[k]=d
    records=[]
    for (year,cat),d in sorted(latest.items()):
        code,label,_=PERIODS[cat]; m={k:None for k in SPECS}; source={}; fs='CFS'; status='API_NOT_AVAILABLE_BEFORE_2015'
        if year>=2015:
            rows=client.statement(corp['corp_code'],year,code,fs)
            if not rows: fs='OFS'; rows=client.statement(corp['corp_code'],year,code,fs)
            write_json(raw/'statements'/f'{year}_{cat}.json',rows)
            m,source=extract(rows,cat); status='OK' if any(v is not None for v in m.values()) else 'NO_FINANCIAL_DATA'
        records.append({'year':year,'category':cat,'report_label':label,'fs_div':fs if year>=2015 else None,'rcept_no':d['rcept_no'],'source_url':d['url'],'status':status,'basis':'YTD; BS period-end','provenance':source,**m,**ratios(m)})
    if not reports: raise RuntimeError('No filings found; refusing to replace existing data')
    payload={'company':corp,'updated_at_utc':now.isoformat(),'records':records,'reports':reports,'peers':cfg['peer_firms'],'notes':['2010–2014: 원문 ZIP 보관; 구조화 재무 API 미제공으로 수치는 미추출.','손익·현금흐름은 누적(YTD), 재무상태표는 기말. 연결 우선·미제공 시 별도.','분모가 0 이하인 비율 및 계정이 모호한 수치는 표시하지 않음.']}
    write_json(ROOT/'site/data/dashboard_data.json',payload)
    csvpath=ROOT/'site/data/financials.csv'
    with csvpath.open('w',newline='',encoding='utf-8-sig') as f:
        keys=['year','category','fs_div','status',*SPECS,*ratios({}), 'source_url']; writer=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore'); writer.writeheader(); writer.writerows(records)
    print(f'{corp["corp_name"]}: {len(reports)} filings, {len(records)} periods')
if __name__=='__main__': main()
