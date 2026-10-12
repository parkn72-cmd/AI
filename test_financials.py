import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from main import extract, ratios, parse_report, number
class TestFinancials(unittest.TestCase):
    def test_ytd(self):
        rows=[{'sj_div':'IS','account_id':'ifrs-full_Revenue','account_nm':'매출액','thstrm_amount':'30','thstrm_add_amount':'100'}, {'sj_div':'IS','account_id':'dart_OperatingIncomeLoss','thstrm_amount':'3','thstrm_add_amount':'10'}]
        m,p=extract(rows,'half_year'); self.assertEqual(m['revenue'],100); self.assertEqual(ratios(m)['operating_margin'],10)
        self.assertEqual(p['revenue']['field'],'thstrm_add_amount')
    def test_no_guessed_cumulative(self):
        rows=[{'sj_div':'IS','account_id':'ifrs-full_Revenue','thstrm_amount':'30'}]
        self.assertIsNone(extract(rows,'quarterly_q3')[0]['revenue'])
    def test_ratios(self):
        m={'assets':200,'liabilities':100,'equity':100,'current_assets':60,'current_liabilities':30,'revenue':100,'operating_income':-10,'net_income':5}
        self.assertEqual(ratios(m),{'debt_ratio':100,'equity_ratio':50,'current_ratio':200,'operating_margin':-10,'net_margin':5})
        m['equity']=0; self.assertIsNone(ratios(m)['debt_ratio'])
    def test_correction_fiscal_year(self):
        d=parse_report({'report_nm':'[기재정정]사업보고서 (2010.12)','rcept_no':'20120401000001'})
        self.assertEqual(d['year'],2010); self.assertEqual(d['category'],'annual')
    def test_ambiguity(self):
        rows=[{'sj_div':'BS','account_id':'ifrs-full_Assets','thstrm_amount':str(x)} for x in (100,200)]
        self.assertIsNone(extract(rows,'annual')[0]['assets'])
    def test_number(self):
        self.assertEqual(number('(1,234)'),-1234); self.assertIsNone(number('-'))
if __name__=='__main__': unittest.main()
