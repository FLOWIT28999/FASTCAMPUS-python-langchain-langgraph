from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser


# --- CompanyAnalysis 하위 모델 ---

class AnalysisTarget(BaseModel):
    name: str = Field(default="", description="기업명")
    domain: str = Field(default="", description="공식 홈페이지 주소")
    region: str = Field(default="", description="KR 또는 Global")


class CorporateIdentity(BaseModel):
    year_founded: str = Field(default="", description="설립 연도")
    hq_location: str = Field(default="", description="본사 소재지")
    current_ceo: dict = Field(default_factory=dict, description="CEO 정보 (name, title 등)")


class FinancialPerformance(BaseModel):
    total_funding_amount: str = Field(default="", description="총 투자 유치 금액")
    annual_revenue_latest: str = Field(default="", description="최근 연 매출액")
    valuation: str = Field(default="", description="기업 가치")


# --- 메인 스키마 3개 ---

class CompanyAnalysis(BaseModel):
    """기업 분석 에이전트의 출력 스키마"""
    analysis_target: AnalysisTarget = Field(default_factory=AnalysisTarget, description="분석 대상 기업 정보")
    corporate_identity: CorporateIdentity = Field(default_factory=CorporateIdentity, description="기업 기본 정보")
    financial_performance: FinancialPerformance = Field(default_factory=FinancialPerformance, description="재무 성과")
    operational_metrics: dict = Field(default_factory=dict, description="운영 지표 (직원 수, MAU 등)")
    market_intelligence: dict = Field(default_factory=dict, description="시장 정보 (최신 뉴스, 고객사 등)")


class ProductOffering(BaseModel):
    """제품 오퍼링 에이전트의 출력 스키마"""
    features: list = Field(default_factory=list, description="주요 기능 목록")
    pricing_plans: list = Field(default_factory=list, description="요금제 플랜 목록")
    technology_stack: list = Field(default_factory=list, description="기술 스택 목록")
    sources: list = Field(default_factory=list, description="출처 URL 목록")


class ProductReview(BaseModel):
    """제품 평가 에이전트의 출력 스키마"""
    review_summary: dict = Field(default_factory=dict, description="리뷰 요약 (평점, 리뷰 수 등)")
    top_pros: list = Field(default_factory=list, description="주요 장점 목록")
    top_cons: list = Field(default_factory=list, description="주요 단점 목록")
    notable_feedbacks: list = Field(default_factory=list, description="주목할 피드백 목록")
    sources: list = Field(default_factory=list, description="출처 URL 목록")


# --- PydanticOutputParser ---

company_parser = PydanticOutputParser(pydantic_object=CompanyAnalysis)
product_parser = PydanticOutputParser(pydantic_object=ProductOffering)
review_parser = PydanticOutputParser(pydantic_object=ProductReview)
