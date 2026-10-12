[![🔗 대시보드 바로가기](site/assets/dashboard-badge.svg)](https://parkn72-cmd.github.io/AI/)

# SM엔터테인먼트 OpenDART 재무분석 에이전트

대상 저장소: https://github.com/parkn72-cmd/AI

상단 링크는 GitHub Pages 기본 예상 주소입니다. **현재 배포 완료를 의미하지 않습니다.** 첫 배포 후 실제 주소가 다른 경우 링크를 수정하세요. 사용자 배지 이미지 및 재무항목 첨부파일이 제공되지 않아 기본 항목과 자체 제작 SVG 배지를 사용했습니다.

## 설치 및 최초 실행

1. ZIP을 풀고 README.md, config.json, requirements.txt, src, tests, site, github-workflows를 저장소 루트에 업로드합니다. ZIP 파일 자체를 업로드하는 것이 아닙니다.
2. GitHub의 Add file → Create new file에서 파일명을 `.github/workflows/monthly-dart-update.yml`로 입력하세요. ZIP의 `github-workflows/monthly-dart-update.yml` 내용을 전부 복사해서 저장합니다. 일반 폴더에 있는 워크플로우는 자동 실행되지 않습니다. ZIP에는 숨김 파일/폴더를 포함하지 않았으나 GitHub 자동 실행에는 이 경로가 필수입니다.
3. OpenDART https://opendart.fss.or.kr/ 에서 인증키를 신청합니다.
4. 저장소 Settings → Secrets and variables → Actions → New repository secret에서 이름 `DART_API_KEY`, 값에 인증키를 저장합니다. 키를 코드, config.json, README에 입력하지 마세요.
5. Settings → Actions → General → Workflow permissions에서 Read and write permissions를 허용합니다. 조직 정책이나 브랜치 보호 정책이 데이터 커밋을 막으면 관리자 설정 조정이 필요합니다.
6. Settings → Pages → Build and deployment → Source를 GitHub Actions로 선택합니다. 공개 저장소를 권장하며, 비공개 저장소는 요금제·Pages 제공 조건을 확인하세요.
7. Actions → SM DART update and Pages → Run workflow를 실행합니다. 워크플로우 파일은 기본 브랜치에 있어야 자동 스케줄이 활성화됩니다.
8. 성공 후 Pages가 알려주는 실제 주소를 위 배지 링크에 반영합니다. 저장소 우측 About의 톱니바퀴 → Website에도 같은 주소를 입력하세요.

## 실행 주기

매월 1일 오전 9시 17분 한국시간 (UTC 00:17) 실행합니다. GitHub 스케줄은 지연될 수 있어 정각 실행을 보장하지 않습니다. 수동 실행도 가능합니다. 장기간 활동이 없는 공개 저장소는 스케줄이 비활성화될 수 있으므로 Actions 상태를 확인하세요.

매 실행 시 공시 목록과 지원되는 재무 API를 다시 조회하여 신규·정정공시를 반영합니다. 이미 저장한 접수번호의 원문 ZIP은 재다운로드하지 않습니다. API 또는 네트워크 실패 시 기존 대시보드 데이터의 교체와 배포를 중단합니다. 실수집/API 인증/Pages 배포는 아직 수행하지 않았습니다.

## 데이터 범위와 중요한 제한

- 종목코드 041510으로 대상 법인을 확인합니다.
- 2010년 이후 사업·반기·분기보고서 원문을 `data/raw/documents/접수번호.zip`에 보관합니다. 정정공시를 포함하고, 보고서명에서 사업연도를 분리합니다.
- **단일회사 전체 재무제표 API는 2015년 이후만 제공합니다. 2010~2014년은 원문 보관만 구현되어 있고 재무수치 자동 추출은 미구현입니다.** 전체 기간 수치 분석이 완료된 프로젝트가 아닙니다.
- 공식 근거: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020
- 2015년 이후 연결(CFS) 우선, 연결 미제공 시 별도(OFS)를 사용합니다. 연결/별도 혼합 시 추이 비교에 유의하세요.
- 손익·현금흐름은 누적(YTD), 재무상태표는 기말입니다. Quarterly는 Q1과 Q3 누적값이며 순수 3개월 분기값이나 Q4 별도 추출은 구현하지 않았습니다.
- 반기·3분기 손익 누적금액이 없을 때 3개월 금액을 대신 사용하지 않습니다. 누락·모호한 계정은 빈칸으로 표시합니다.
- 국내 피어 표는 참고 비교군이며 피어의 재무수치 수집은 포함하지 않습니다.
- 실제 재무수치 첨부파일이 없어 다음 기본 항목을 제공합니다.

## 기본 재무항목

자산총계, 부채총계, 자본총계, 유동자산, 유동부채, 현금및현금성자산, 매출액, 영업이익, 순이익, 영업활동현금흐름.

비율은 부채비율(부채/자본), 자기자본비율(자본/자산), 유동비율(유동자산/유동부채), 영업이익률(영업이익/매출액), 순이익률(순이익/매출액) ×100입니다. 분모가 0 이하인 경우 표시하지 않습니다. ROA/ROE는 평균자산·평균자본과 기간 조정이 필요하므로 현재 포함하지 않았습니다.

대시보드 상단: 최근 유효한 연간 KPI 및 매출액·영업이익률 그래프. 하단: Annual, Half-year, Quarterly 세 개 별도 표, 전체 데이터 CSV, 국내 피어 표. 대시보드는 억 원, CSV는 원 기준입니다. 최초 수집 전에는 빈 상태를 보여주며 샘플 수치를 생성하지 않습니다.

## 국내 peer firms

| 회사 | 종목코드 | 선정 이유 | 유의점 |
|---|---|---|---|
| JYP Ent. | 035900 | 아티스트 매니지먼트·음반·공연 | 아티스트 구성과 사업 포트폴리오 차이 |
| 와이지엔터테인먼트 | 122870 | 아티스트 IP·음악·공연 | 활동 일정과 연결 종속기업 차이 |
| 하이브 | 352820 | 음악·멀티레이블·플랫폼 | 플랫폼·해외사업 비중 차이 |
| 큐브엔터 | 182360 | 아티스트 매니지먼트·음반 | 규모와 비음악 사업 비중 차이 |

## 파일 구조

- src/dart_client.py: API 인증·법인 식별·공시목록 페이지 처리·원문 다운로드
- src/main.py: 수집·정확 매칭·비율 계산·JSON/CSV 생성
- config.json: 대상 종목코드·시작연도·피어 목록 (인증키 없음)
- site/index.html: Pages 대시보드
- site/data/dashboard_data.json: 초기 빈 데이터; 수집 시 갱신
- site/assets/dashboard-badge.svg: 기본 배지
- github-workflows/monthly-dart-update.yml: GitHub 필수 경로에 복사할 워크플로우
- tests/test_financials.py: 오프라인 테스트

배포 아티팩트는 site 폴더만 포함하므로 소스코드와 원문 ZIP을 불필요하게 Pages로 배포하지 않습니다. 원문 ZIP은 저장소에 커밋되므로 저장소 용량 제한을 확인하세요.

## 로컬 실행 (Python 3.11 이상)

```bash
python -m pip install -r requirements.txt
# macOS/Linux: 실제 키를 본인 환경에서 입력
export DART_API_KEY='본인의 인증키'
python -m unittest discover -s tests -v
python src/main.py
```

Windows PowerShell 환경변수 설정: `$env:DART_API_KEY = '본인의 인증키'`

## 검증 상태 및 오류 대응

Python/JSON/YAML 구문 검사와 오프라인 테스트 6개 통과. 실제 API 응답·계정 매핑·수집·GitHub Actions/Pages 실행은 키와 저장소 권한 연결 후 검증해야 합니다. 워크플로우 무오류를 보장하지 않습니다.

- DART_API_KEY required: Secret 이름 및 저장소 설정 확인.
- OpenDART status 오류: 키 유효성·접근 IP·요청 제한 확인. API 키가 포함된 요청 URL을 공개하지 마세요.
- git push 거부: Actions 쓰기 권한, 브랜치 보호·조직 정책 확인.
- Pages 오류: Source를 GitHub Actions로 선택, github-pages 환경의 배포 허용 브랜치 확인.
- Actions 항목이 보이지 않음: `.github/workflows/monthly-dart-update.yml` 경로와 기본 브랜치 확인.
