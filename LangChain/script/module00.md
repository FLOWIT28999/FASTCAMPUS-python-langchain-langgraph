# 모듈 00: 환경 설정 — 강의 스크립트

> **강사 안내**: 이 스크립트를 순서대로 읽으면서 노트북 셀을 하나씩 실행하면 됩니다.
> 각 섹션은 노트북의 마크다운 셀과 코드 셀 순서에 맞춰져 있습니다.

---

## 도입부

안녕하세요, 여러분!

오늘부터 LangChain을 함께 배워볼 텐데요, 첫 번째 모듈인 **모듈 00: 환경 설정**을 시작하겠습니다.

이 모듈은 본격적인 AI 개발에 앞서 "내 컴퓨터가 제대로 준비되어 있는지" 확인하는 단계입니다. 마치 요리를 시작하기 전에 재료와 도구를 챙겨두는 것처럼, 환경 설정은 이후 모든 실습의 토대가 됩니다.

이 노트북을 끝까지 따라오시면 세 가지를 할 수 있게 됩니다.

**첫 번째**, UV라는 최신 패키지 매니저를 사용해서 필요한 라이브러리를 설치할 수 있게 됩니다.

**두 번째**, Google AI Studio에서 Gemini API 키를 발급받고 LangChain에 연결하는 방법을 알게 됩니다.

**세 번째**, API 키처럼 민감한 정보를 코드에 직접 쓰지 않고 `.env` 파일로 안전하게 관리하는 방법을 익히게 됩니다.

---

## 셀 1: 제목 + 전체 개요 (마크다운)

노트북 첫 번째 셀을 보시면, 이 모듈에서 진행할 단계가 표로 정리되어 있습니다.

총 다섯 단계인데요:

1. UV 패키지 매니저가 설치되어 있는지 확인
2. LangChain 관련 패키지 설치
3. Gemini API 키 발급 안내
4. `.env` 파일에 API 키를 안전하게 저장
5. 모든 설정이 잘 됐는지 최종 점검

예상 소요 시간은 약 30분입니다. Jupyter 노트북에서 셀을 실행할 때는 `Shift + Enter`를 누르시면 됩니다. 위에서부터 순서대로 실행해 주세요.

---

## 셀 2: 학습 목표 (마크다운)

두 번째 셀에는 학습 목표가 적혀 있습니다. 방금 제가 도입부에서 말씀드린 세 가지와 동일합니다. UV 이해, Gemini API 키 발급, `.env` 파일 관리. 이 세 가지를 오늘 모두 달성하게 됩니다.

---

## 셀 3: 전체 흐름도 (마크다운)

세 번째 셀은 ASCII 다이어그램으로 전체 흐름을 한눈에 보여줍니다.

```
[1] UV 설치 확인
     ↓
[2] 패키지 설치 (langchain, gemini, dotenv)
     ↓
[3] Gemini API 키 발급 (Google AI Studio)
     ↓
[4] API 키 입력 (getpass로 안전하게)
     ↓
[5] .env 파일 자동 생성
     ↓
[6] 최종 환경 검증
```

6단계를 순서대로 진행합니다. 오늘 노트북의 전체 지도라고 생각하시면 됩니다.

---

## 섹션 2: UV 패키지 매니저

### 셀 4: UV란? (마크다운)

이제 본격적으로 시작합니다. 네 번째 셀은 **UV 패키지 매니저**를 소개하는 설명입니다.

Python 패키지를 설치할 때 보통 `pip`을 쓰죠? UV는 그 `pip`의 업그레이드 버전이라고 보시면 됩니다.

노트북에는 **자전거 vs 스포츠카 비유**가 나와 있는데요, 정말 딱 맞는 비유입니다.

- `pip`은 자전거입니다. 느리지만 어디서나 있고, 모두가 알고 있죠.
- `UV`는 스포츠카입니다. Rust 언어로 만들어져서 pip보다 **10~100배 빠릅니다!**

비교표를 보시면:

| 항목 | pip | UV |
|------|-----|----|
| 속도 | 보통 | 10~100배 빠름 |
| 언어 | Python | Rust |
| 가상환경 관리 | 별도 venv 필요 | 자동 통합 |
| 프로젝트 관리 | requirements.txt | pyproject.toml |

이 커리큘럼은 UV 기반으로 설계되어 있기 때문에, Jupyter 안에서도 `!uv pip install` 명령어를 사용합니다.

---

### 코드 셀 1: UV 설치 여부 확인

이제 첫 번째 코드 셀입니다. **이 코드는 여러분 컴퓨터에 UV가 설치되어 있는지 확인합니다.**

```python
import subprocess
import sys

result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
if result.returncode == 0:
    print(f'[OK] UV가 설치되어 있습니다: {result.stdout.strip()}')
else:
    print('[FAIL] UV가 설치되어 있지 않습니다.')
    print('아래 섹션의 설치 방법을 참고하세요.')
```

코드를 하나씩 뜯어볼게요.

`subprocess.run()`은 파이썬 코드 안에서 **외부 프로그램(터미널 명령어)을 실행**할 때 쓰는 함수입니다. `['uv', '--version']`은 터미널에서 `uv --version`을 입력하는 것과 같습니다.

`capture_output=True`는 그 명령어의 출력 결과를 캡처해서 파이썬으로 가져오겠다는 뜻이고, `text=True`는 결과를 텍스트 형태로 받겠다는 의미입니다.

`result.returncode`는 명령어가 성공했으면 `0`, 실패했으면 `0`이 아닌 숫자를 반환합니다. 컴퓨터 세계에서 `0`은 "성공"을 의미합니다.

**실행 결과:**

```
[OK] UV가 설치되어 있습니다: uv 0.8.2 (Homebrew 2025-07-22)
```

`uv 0.8.2`는 현재 설치된 UV의 버전 번호입니다. `(Homebrew ...)`는 macOS에서 Homebrew라는 패키지 관리자로 설치했다는 뜻입니다. 버전 숫자는 여러분 환경마다 다를 수 있습니다.

만약 `[FAIL]`이 뜬다면, 다음 셀의 설치 방법을 따라주세요.

---

### 셀 5: UV 설치 방법 안내 (마크다운)

이 셀은 UV가 설치되지 않은 경우를 위한 안내입니다.

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

설치 후 터미널을 재시작하고 앞의 셀을 다시 실행하시면 됩니다. UV가 이미 정상 설치되어 있다면 이 셀은 그냥 넘어가셔도 됩니다.

---

## 섹션 3: 패키지 설치

### 셀 6: 설치할 패키지 목록 (마크다운)

이제 실제 패키지를 설치할 차례입니다. 먼저 어떤 패키지를 왜 설치하는지 알아볼게요.

| 패키지 | 역할 |
|--------|------|
| `langchain` | LangChain의 핵심 엔진 — AI 체인을 만드는 뼈대 |
| `langchain-core` | LangChain 기본 빌딩 블록 — 내부 핵심 구성요소 |
| `langchain-community` | 커뮤니티가 만든 도구들 — 다양한 확장 기능 |
| `langchain-google-genai` | Gemini AI와 LangChain을 연결하는 통합 패키지 |
| `python-dotenv` | `.env` 파일의 환경변수를 코드에서 읽기 위한 도구 |

`langchain`이 엔진이라면, `langchain-google-genai`는 구글 Gemini와 그 엔진을 연결하는 어댑터입니다. 그리고 `python-dotenv`는 나중에 API 키를 안전하게 불러올 때 쓰입니다.

---

### 코드 셀 2: 패키지 설치

**이 코드는 방금 설명한 5개 패키지를 한 번에 설치합니다.**

```python
print('패키지 설치를 시작합니다...')
print()

!uv pip install langchain langchain-core langchain-community langchain-google-genai python-dotenv -q

print()
print('설치 완료! 다음 셀로 넘어가서 확인해보세요.')
```

코드 맨 앞의 **느낌표(`!`)** 에 주목해 주세요. Jupyter 노트북에서 `!`로 시작하는 줄은 파이썬 코드가 아니라 **터미널 명령어**입니다. `!uv pip install`은 "터미널에서 `uv pip install`을 실행해줘"라는 뜻입니다.

`-q` 옵션은 "quiet(조용히)"의 약자로, 설치 과정의 장황한 로그를 줄여줍니다. 없으면 수십 줄의 로그가 쏟아집니다.

**실행 결과:**

```
패키지 설치를 시작합니다...

설치 완료! 다음 셀로 넘어가서 확인해보세요.
```

설치에 1~2분 정도 걸릴 수 있으니 잠시 기다려 주세요. 셀 왼쪽에 `[*]`가 표시되는 동안은 실행 중입니다.

---

### 코드 셀 3: 패키지 버전 확인

**이 코드는 설치한 5개 패키지가 정상적으로 설치됐는지 버전을 확인합니다.**

```python
import importlib.metadata

packages = [
    ("langchain", "langchain"),
    ("langchain_core", "langchain-core"),
    ("langchain_community", "langchain-community"),
    ("langchain_google_genai", "langchain-google-genai"),
    ("dotenv", "python-dotenv")
]

for module_name, package_name in packages:
    try:
        __import__(module_name)
        version = importlib.metadata.version(package_name)
        print(f'[OK] {package_name}: {version}')
    except ImportError:
        print(f'[FAIL] {package_name}: 설치 실패 (모듈을 가져올 수 없습니다)')
    except importlib.metadata.PackageNotFoundError:
        print(f'[FAIL] {package_name}: 패키지를 찾을 수 없습니다')
```

여기서 중요한 개념이 하나 있습니다. **모듈 이름과 패키지 이름이 다를 수 있습니다.**

예를 들어, 설치할 때는 `pip install python-dotenv`라고 쓰지만, 코드에서 `import`할 때는 `import dotenv`라고 씁니다. 하이픈(`-`)이 언더스코어(`_`)로 바뀌기도 합니다. 이 차이를 잡아주기 위해 `packages` 리스트에 `(모듈명, 패키지명)` 쌍을 저장해둔 것입니다.

`importlib.metadata`는 파이썬 표준 라이브러리로, **설치된 패키지의 버전 정보를 읽어오는** 도구입니다. `importlib.metadata.version("langchain")`은 "langchain 패키지의 버전이 뭐야?"라고 물어보는 것입니다.

`for` 루프는 5개 패키지를 하나씩 돌면서 확인합니다. `try/except`는 에러가 발생해도 프로그램이 멈추지 않고 `[FAIL]` 메시지를 출력하도록 보호해줍니다.

**실행 결과:**

```
=== 패키지 설치 확인 ===

[OK] langchain: 1.2.10
[OK] langchain-core: 1.2.17
[OK] langchain-community: 0.4.1
[OK] langchain-google-genai: 4.2.1
[OK] python-dotenv: 1.2.2

모두 [OK]라면 패키지 설치 완료!
```

버전 숫자는 `1.2.10`처럼 점으로 구분된 세 자리입니다. `주버전.부버전.패치버전` 형태로, 뒤로 갈수록 작은 변경입니다. 여러분 환경에서 버전 숫자가 다를 수 있는데, 이는 더 최신 버전이 설치된 것이므로 정상입니다.

모두 `[OK]`가 나왔다면 다음 섹션으로 넘어가세요!

---

## 섹션 4: Gemini API 키

### 셀 7: Gemini API 개념 설명 (마크다운)

이번 섹션에서는 Gemini API 키를 발급받겠습니다. 그 전에 API가 무엇인지 이해하고 넘어갈게요.

노트북에 **레스토랑 비유**가 나와 있는데, 정말 명쾌한 설명입니다.

```
우리 코드  →  [API 키]  →  Gemini API  →  구글 AI 서버
   손님    →  회원권   →     웨이터    →       주방
```

- **구글 AI 서버**는 주방입니다. 실제 AI 연산이 일어나는 곳이죠.
- **Gemini API**는 웨이터입니다. 우리의 요청을 받아서 주방에 전달하고, 결과를 우리에게 가져다 줍니다.
- **API 키**는 회원권입니다. 이게 없으면 주문 자체가 불가능합니다.
- **우리 코드**는 손님입니다.

왜 이런 방식으로 작동할까요? GPT나 Gemini 같은 대형 AI 모델은 수백 GB에 달합니다. 제 노트북이나 여러분 컴퓨터에서 직접 실행하는 건 불가능하죠. 그래서 구글이 강력한 서버에서 모델을 실행하고, 우리는 API를 통해 결과만 받아오는 방식을 사용합니다.

좋은 소식은, **Gemini는 무료 티어를 제공**합니다. Google AI Studio에서 API 키를 발급받으면 학습 목적으로 사용하기에 충분한 양을 무료로 쓸 수 있습니다.

---

### 셀 8: API 키 발급 방법 (마크다운)

발급 방법은 여섯 단계입니다.

**Step 1** 브라우저를 열고 [https://aistudio.google.com/](https://aistudio.google.com/) 접속

**Step 2** 구글 계정으로 로그인

**Step 3** 왼쪽 사이드바에서 **"Get API key"** 클릭

**Step 4** **"Create API key"** 버튼 클릭

**Step 5** 생성된 API 키를 **복사** — `AIzaSy...` 형태의 긴 문자열입니다

**Step 6** 아래 코드 셀로 이동해서 API 키 입력

> **주의**: API 키는 절대로 다른 사람에게 공유하지 마세요! 악용되면 요금이 발생할 수 있습니다.

발급을 완료하셨나요? 그러면 다음 코드 셀을 실행하겠습니다.

---

### 코드 셀 4: API 키 입력

**이 코드는 화면에 아무것도 표시되지 않는 안전한 방식으로 API 키를 입력받습니다.**

```python
import getpass

print('Gemini API 키를 입력하세요:')
print('(입력 중에는 화면에 아무것도 표시되지 않습니다 - 정상입니다!)')
print()

api_key = getpass.getpass('API 키 입력: ')

if api_key:
    masked = api_key[:8] + '*' * (len(api_key) - 8)
    print(f'\n[OK] API 키 입력 완료! ({masked})')
    print('다음 셀로 이동해서 .env 파일을 생성하세요.')
else:
    print('\n[FAIL] API 키가 입력되지 않았습니다. 다시 실행해주세요.')
```

`getpass.getpass()`는 **비밀번호 입력창처럼 작동**합니다. 이 함수는 내부적으로 터미널의 에코(echo) 기능을 일시적으로 차단합니다. 보통 키보드를 누르면 화면에 글자가 나타나는데(이것이 에코입니다), `getpass`는 이 에코를 막아서 타이핑하는 내용이 화면에 보이지 않게 합니다.

마스킹 부분도 살펴볼게요:
```python
masked = api_key[:8] + '*' * (len(api_key) - 8)
```
`api_key[:8]`은 앞에서 8글자만 가져오고, 나머지 길이만큼 `*`로 채웁니다. 확인용으로 일부만 보여주는 것입니다.

**실행 결과:**

```
Gemini API 키를 입력하세요:
(입력 중에는 화면에 아무것도 표시되지 않습니다 - 정상입니다!)

API 키 입력:

[OK] API 키 입력 완료! (AIzaSyAl*******************************)
다음 셀로 이동해서 .env 파일을 생성하세요.
```

`AIzaSyAl*******`처럼 앞 8자만 보이고 나머지는 `*`로 대체됩니다. 이것이 정상 동작입니다. 실제로 잘 입력됐는지 확인만 해주는 거죠.

---

## 섹션 5: .env 파일 설정

### 셀 9: .env 파일 개념 설명 (마크다운)

방금 API 키를 입력했는데, 이걸 어딘가에 저장해야 합니다. 그 저장소가 바로 `.env` 파일입니다.

노트북에 **일기장 비유**가 나와 있습니다. 일기에 비밀을 적어두듯, `.env` 파일에 비밀 정보를 저장한다는 거죠.

왜 코드에 직접 쓰면 안 될까요? 노트북에 이렇게 나와 있습니다:

```python
# 이렇게 하면 절대 안 됩니다!
api_key = "AIzaSyABCDEF12345678"  # GitHub에 올리면 전 세계가 봅니다
```

코드 파일을 GitHub에 올리는 순간, API 키가 전 세계에 공개됩니다. 구글 봇들이 GitHub을 실시간으로 스캔해서 노출된 API 키를 찾아내고 악용합니다. 실제로 이런 실수로 요금 폭탄을 맞는 사례가 많습니다.

올바른 방법은 이렇습니다:

```python
# 이렇게 해야 합니다!
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")  # .env 파일에서 안전하게 읽기
```

그리고 `.gitignore` 파일에 `.env`를 추가해두면, Git이 이 파일을 자동으로 무시합니다. 이 프로젝트의 `.gitignore`에는 이미 `.env`가 포함되어 있어서 자동으로 보호됩니다.

---

### 코드 셀 5: .env 파일 생성

**이 코드는 방금 입력한 API 키를 `.env` 파일에 저장합니다.**

```python
import os

notebook_dir = os.path.dirname(os.path.abspath('__file__'))
project_root = os.path.dirname(notebook_dir)
env_path = os.path.join(project_root, '.env')

env_content = f"""# Google Gemini API 키
GOOGLE_API_KEY={api_key}
"""

with open(env_path, 'w', encoding='utf-8') as f:
    f.write(env_content)

print(f'[OK] .env 파일 생성 완료!')
print(f'저장 위치: {env_path}')
```

경로 계산 부분이 조금 복잡해 보일 수 있는데요, 차근차근 설명드리겠습니다.

현재 이 노트북은 `00_setup/` 폴더 안에 있습니다. 그런데 `.env` 파일은 프로젝트 루트(최상위 폴더)에 저장해야 합니다. 왜냐하면 나중에 `01_hello/`, `02_prompts/` 등 다른 모듈에서도 같은 `.env` 파일을 공유해야 하기 때문입니다.

- `os.path.abspath('__file__')`은 이 노트북 파일의 절대 경로를 가져옵니다
- `os.path.dirname()`을 **한 번** 쓰면 → `00_setup/` 폴더 경로
- `os.path.dirname()`을 **두 번** 쓰면 → 프로젝트 루트 경로

`os.path.dirname`을 두 번 쓰는 이유가 바로 이것입니다. 한 단계 위로 올라가야 하기 때문입니다.

**실행 결과:**

```
[OK] .env 파일 생성 완료!
저장 위치: /Users/sonny/Desktop/Dev/.../LangChain/.env

주의: 이 파일은 절대 GitHub에 올리지 마세요!
      (.gitignore에 이미 추가되어 있어서 자동으로 보호됩니다)
```

절대 경로가 출력되는 이유는 `os.path.abspath()`를 사용했기 때문입니다. 파일이 정확히 어디 저장됐는지 한눈에 확인할 수 있도록 전체 경로를 보여주는 것입니다.

---

### 코드 셀 6: .env 파일 로드 및 확인

**이 코드는 방금 저장한 `.env` 파일을 다시 읽어서 API 키가 제대로 저장됐는지 검증합니다.**

```python
import os
from dotenv import load_dotenv

notebook_dir = os.path.dirname(os.path.abspath('__file__'))
project_root = os.path.dirname(notebook_dir)
env_path = os.path.join(project_root, '.env')

loaded = load_dotenv(env_path)

loaded_key = os.getenv('GOOGLE_API_KEY')
```

`load_dotenv()`는 `.env` 파일을 읽어서 그 안의 값들을 **운영체제의 환경변수**로 등록합니다. 환경변수란 운영체제가 관리하는 전역 변수 같은 것으로, 어떤 프로그램에서든 `os.getenv()`로 읽을 수 있습니다.

앞의 셀 5에서 이미 `api_key` 변수에 값이 있는데 왜 다시 로드할까요? 이렇게 하는 이유는 "`.env` 파일에 제대로 쓰였는가?"를 독립적으로 검증하기 위해서입니다. 파일 저장 후 파일 읽기까지 성공해야 완전한 검증이 됩니다.

**실행 결과:**

```
=== .env 파일 로드 결과 ===
[OK] .env 파일 로드 성공!

=== API 키 확인 ===
[OK] GOOGLE_API_KEY: AIzaSyAlrJ...dAEI
API 키가 정상적으로 로드되었습니다!
```

이번에는 앞 10자와 뒤 4자를 보여줍니다. 마스킹 방식이 앞 셀과 살짝 다르죠? `loaded_key[:10] + '...' + loaded_key[-4:]` 형식입니다. 어쨌든 키가 정상적으로 로드됐다는 것이 중요합니다.

---

## 섹션 6: 환경 검증

### 셀 10: 환경 검증 설명 (마크다운)

이제 마지막 섹션입니다. 모든 설정이 끝났으니 전체 환경을 한 번에 점검합니다.

아래 두 개의 코드 셀을 실행하면:

1. **종합 체크** — 각 항목별로 `[OK]` 또는 `[FAIL]`로 상태를 보여줍니다
2. **모델 import 테스트** — LangChain에서 Gemini 모델을 불러올 수 있는지 확인합니다

모든 항목이 `[OK]`라면 **모듈 01로 넘어갈 준비가 완료**된 것입니다!

---

### 코드 셀 7: 종합 환경 체크

**이 코드는 환경 설정의 6개 핵심 항목을 한 번에 점검하는 `check_all()` 함수를 실행합니다.**

```python
def check_all():
    results = []

    # 1. Python 버전 확인
    # 2. langchain 확인
    # 3. langchain-google-genai 확인
    # 4. python-dotenv 확인
    # 5. .env 파일 확인
    # 6. API 키 확인

    ...
    check_all()
```

6개 체크 항목 각각의 의미를 설명드리겠습니다.

**항목 1 — Python 버전**: `v >= (3, 10)` 조건으로 파이썬 3.10 이상인지 확인합니다. LangChain 최신 버전들이 3.10 이상의 문법(특히 타입 힌트)을 사용하기 때문입니다. 3.9 이하라면 일부 기능이 동작하지 않을 수 있습니다.

**항목 2~4 — 패키지 확인**: 이전 코드 셀 3과 동일한 방식으로 세 가지 핵심 패키지의 설치 여부를 확인합니다.

**항목 5 — .env 파일 확인**: `os.path.exists(env_path)`로 파일이 실제로 존재하는지 검사합니다.

**항목 6 — API 키 확인**: 세 가지 조건을 동시에 만족해야 `[OK]`입니다.
```python
if api_key and api_key != 'your_api_key_here' and len(api_key) > 10:
```
- `api_key`: 값이 비어있지 않아야 함
- `api_key != 'your_api_key_here'`: 예시 값이 그대로 남아있지 않아야 함 (`.env.example` 파일을 그대로 복사한 경우 방지)
- `len(api_key) > 10`: 아주 짧은 값이 아니어야 함

**실행 결과:**

```
==================================================
       환경 설정 종합 체크 결과
==================================================
[OK]   Python 버전                 3.12.11
[OK]   langchain                 1.2.10
[OK]   langchain-google-genai    4.2.1
[OK]   python-dotenv             1.2.2
[OK]   .env 파일                   존재 (/Users/.../LangChain/.env)
[OK]   GOOGLE_API_KEY            AIzaSyAlrJ...
==================================================
모든 항목 통과! 모듈 01로 넘어갈 준비가 됐습니다!
```

6개 항목이 모두 `[OK]`로 나왔습니다. Python 3.12.11이 설치되어 있고, 필요한 패키지들이 모두 있으며, `.env` 파일과 API 키도 정상입니다.

혹시 `[FAIL]`이 나오는 항목이 있다면, 해당 섹션으로 돌아가서 관련 셀을 다시 실행하시면 됩니다.

---

### 코드 셀 8: Gemini 모델 Import 테스트

**이 코드는 LangChain에서 Gemini 모델 클래스를 불러올 수 있는지 확인합니다. 실제 API를 호출하지는 않습니다.**

```python
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print('[OK] ChatGoogleGenerativeAI import 성공!')
    print()
    print('다음 모듈에서 이 클래스로 실제 AI와 대화합니다:')
    print()
    print('  from langchain_google_genai import ChatGoogleGenerativeAI')
    print('  llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")')
    print('  response = llm.invoke("안녕하세요!")')
except ImportError as e:
    print(f'[FAIL] Import 실패: {e}')
```

`from langchain_google_genai import ChatGoogleGenerativeAI`는 LangChain의 Gemini 연동 패키지에서 `ChatGoogleGenerativeAI` 클래스를 가져오는 것입니다.

중요한 점: 이 코드는 **클래스를 불러오는 것만** 합니다. 실제로 `ChatGoogleGenerativeAI(...)` 인스턴스를 만들거나 API를 호출하지는 않습니다. 클래스를 불러오는 것만으로는 인터넷 연결이나 API 키가 필요 없습니다.

**실행 결과:**

```
=== Gemini 모델 Import 테스트 ===

[OK] ChatGoogleGenerativeAI import 성공!

다음 모듈에서 이 클래스로 실제 AI와 대화합니다:

  from langchain_google_genai import ChatGoogleGenerativeAI
  llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
  response = llm.invoke("안녕하세요!")

모듈 00 환경 설정이 완료되었습니다!
```

출력 결과에 미리보기 코드가 나옵니다. 다음 모듈에서는 바로 이 세 줄로 Gemini AI와 실제 대화를 하게 됩니다.

- 첫 줄: 클래스를 불러오기
- 둘째 줄: `gemini-2.0-flash` 모델에 연결하는 LLM 객체 생성
- 셋째 줄: `invoke()`로 질문을 보내고 응답 받기

이걸 보면서 "아, 다음 모듈에서 이렇게 쓰는구나"라는 기대감을 가져가시면 됩니다.

---

## 마무리

### 셀 11~12: 요약 + 다음 모듈 예고 (마크다운)

수고하셨습니다! 오늘 배운 내용을 정리해볼게요.

---

**1. UV 패키지 매니저**

UV는 pip보다 10~100배 빠른 Python 패키지 매니저입니다. Rust 언어로 만들어졌고, Jupyter 노트북에서는 `!uv pip install` 명령어로 사용합니다. 앞으로 모든 패키지 설치에 이 방식을 씁니다.

**2. 필수 패키지 설치**

LangChain 개발에 필요한 다섯 가지 패키지를 설치했습니다. `langchain`이 핵심 엔진이고, `langchain-google-genai`가 Gemini와의 연결고리, `python-dotenv`가 비밀 관리 도구입니다.

**3. Gemini API 키 발급**

Google AI Studio에서 무료로 발급받았고, `getpass.getpass()`를 사용해서 화면에 노출 없이 안전하게 입력받았습니다. API는 레스토랑의 웨이터처럼, 우리 코드와 구글 AI 서버 사이에서 요청을 중계합니다.

**4. .env 파일 관리**

API 키는 코드에 직접 쓰지 않고 `.env` 파일에 저장합니다. 일기장에 비밀을 적어두는 것처럼요. `.gitignore`에 `.env`를 추가해 GitHub 업로드를 방지합니다. 코드에서는 `load_dotenv()` + `os.getenv()` 패턴으로 읽어옵니다.

이 패턴은 앞으로 모든 모듈에서 계속 반복됩니다:

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
```

---

**다음 모듈 예고: 모듈 01 — Hello LangChain!**

모듈 01에서는 드디어 **실제 AI와 첫 대화**를 나눕니다. 방금 import 테스트에서 미리보기로 봤던 그 코드를 직접 실행하게 됩니다.

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
response = llm.invoke("안녕하세요! LangChain이 뭔가요?")
print(response.content)
```

모듈 01에서는 `invoke()`, `stream()`, 다양한 메시지 타입까지 다룹니다. 오늘 환경 설정을 완료했으니, 다음 시간부터는 본격적인 LangChain 여정이 시작됩니다.

다음 시간에 뵙겠습니다!

---

> **참고**: 다음 모듈로 넘어가기 전에 종합 체크 셀에서 모든 항목이 `[OK]`인지, `.env` 파일에 실제 API 키가 저장됐는지, `ChatGoogleGenerativeAI` import가 성공했는지 확인해 주세요.
