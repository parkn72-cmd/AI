import io, os, time, zipfile
from xml.etree import ElementTree as ET
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE='https://opendart.fss.or.kr/api/'
class DartClient:
    def __init__(self):
        self.key=os.environ.get('DART_API_KEY','').strip()
        if not self.key: raise RuntimeError('DART_API_KEY secret is required')
        self.session=requests.Session()
        self.session.mount('https://',HTTPAdapter(max_retries=Retry(total=3,backoff_factor=2,status_forcelist=[429,500,502,503,504])))
    def request(self,endpoint,**params):
        time.sleep(.25)
        try:
            r=self.session.get(BASE+endpoint,params={'crtfc_key':self.key,**params},timeout=90)
            r.raise_for_status()
        except requests.RequestException:
            # Never print request URL (contains API key).
            raise RuntimeError('OpenDART network/HTTP failure: '+endpoint) from None
        return r
    def get(self,endpoint,**params):
        d=self.request(endpoint,**params).json()
        if d.get('status') not in ('000','013'): raise RuntimeError('OpenDART status '+str(d.get('status'))+' at '+endpoint)
        return d
    def corp(self,stock_code):
        r=self.request('corpCode.xml')
        if not zipfile.is_zipfile(io.BytesIO(r.content)): raise RuntimeError('Invalid corpCode response; check API key')
        with zipfile.ZipFile(io.BytesIO(r.content)) as z: root=ET.fromstring(z.read(z.namelist()[0]))
        matches=[{'corp_code':x.findtext('corp_code'),'corp_name':x.findtext('corp_name'),'stock_code':stock_code} for x in root.findall('list') if (x.findtext('stock_code') or '').strip()==stock_code]
        if len(matches)!=1: raise RuntimeError('Stock code must identify exactly one company')
        return matches[0]
    def disclosures(self,corp,year):
        rows=[]
        for page in range(1,1000):
            d=self.get('list.json',corp_code=corp,bgn_de=f'{year}0101',end_de=f'{year}1231',pblntf_ty='A',page_count=100,page_no=page)
            rows.extend(d.get('list',[]))
            if page>=int(d.get('total_page',0)): break
        return rows
    def statement(self,corp,year,code,fs):
        return self.get('fnlttSinglAcntAll.json',corp_code=corp,bsns_year=year,reprt_code=code,fs_div=fs).get('list',[])
    def document(self,receipt):
        r=self.request('document.xml',rcept_no=receipt)
        if not zipfile.is_zipfile(io.BytesIO(r.content)): raise RuntimeError('Document ZIP unavailable for '+receipt)
        return r.content
