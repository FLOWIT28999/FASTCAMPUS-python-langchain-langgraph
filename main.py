from src.graph import app


def main():
    company_url = input("분석할 기업 URL을 입력하세요: ").strip()

    if not company_url:
        print("URL을 입력해주세요.")
        return

    try:
        result = app.invoke({
            "company_url": company_url,
            "competitors": [],
            "current_index": 0,
            "analyses": [],
            "final_report": "",
            "pdf_path": "",
        })

        print(f"\n{'='*50}")
        print(f"분석된 경쟁사 수: {len(result['analyses'])}개")
        print(f"PDF 보고서: {result['pdf_path']}")
        print(f"{'='*50}")

    except Exception as e:
        print(f"\n오류 발생: {e}")


if __name__ == "__main__":
    main()
