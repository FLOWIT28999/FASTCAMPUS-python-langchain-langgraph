import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# weasyprint가 Homebrew 라이브러리를 찾을 수 있도록 경로 설정 (macOS)
for lib_path in ["/opt/homebrew/lib", "/usr/local/lib"]:
    if os.path.isdir(lib_path):
        os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = lib_path
        break

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
