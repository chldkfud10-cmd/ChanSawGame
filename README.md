# ChanSawGame

## 요구사항

- Python 3.7 이상
- tkinter (Python 표준 라이브러리, 대부분의 Python 설치에 포함됨)

## 설치 방법

1. 저장소 클론:
```bash
git clone <repository-url>
cd ChanSawGame
```

2. 가상 환경 생성 및 활성화:
```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

3. 의존성 설치:
```bash
pip install -r requirements.txt
```

## 실행 방법

가상 환경이 활성화된 상태에서:
```bash
python main.py
```

또는 가상 환경의 Python을 직접 사용:
```bash
# macOS/Linux
.venv/bin/python3 main.py

# Windows
.venv\Scripts\python main.py
```

## 문제 해결

### ModuleNotFoundError: No module named 'PIL'
Pillow가 설치되지 않았습니다. 다음 명령어로 설치하세요:
```bash
pip install -r requirements.txt
```

### tkinter를 찾을 수 없는 경우
- macOS: Python을 Homebrew로 설치했다면 `brew install python-tk` 실행
- Linux: `sudo apt-get install python3-tk` (Ubuntu/Debian) 또는 `sudo yum install python3-tk` (CentOS/RHEL)
- Windows: Python 설치 시 tkinter가 기본적으로 포함됨

