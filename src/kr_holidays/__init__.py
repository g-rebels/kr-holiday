"""한국 공휴일 패키지

한국의 공휴일, 대체공휴일, 주말 정보를 제공하는 Python 패키지입니다.
공공데이터포털의 공휴일 데이터를 기반으로 합니다.

Examples:
    >>> from kr_holidays import is_holiday, get_holidays
    >>> is_holiday('2024-01-01')
    True
    >>> holidays = get_holidays(2024)
    >>> len(holidays)
    19
"""

__version__ = "1.0.0"
__author__ = "basedocker"
__email__ = "oasisc1208@icloud.com"

# 메인 클래스 임포트
from .core import KoreanHolidays

# 편의 함수들 임포트
from .core import (
    is_holiday,
    is_weekend,
    is_working_day,
    get_holidays,
    get_holiday_name,
    get_next_holiday,
    count_working_days,
    add_working_days,
)

# 데이터 관련 함수들 임포트
from .data import (
    get_supported_years,
    is_supported_year,
    get_year_range,
    get_year_statistics,
)

# 유틸리티 함수들 임포트 (필요한 것만)
from .utils import (
    parse_date_input,
    get_weekday_korean,
    format_date_korean,
    get_weekday_korean_short,
    validate_year_range,
    format_date_korean,
    get_days_in_month,
    date_range,
    is_leap_year,
    get_month_range,
    parse_date_input,
)

# 공개 API 정의
__all__ = [
    # 버전 정보
    "__version__",
    # 메인 클래스
    "KoreanHolidays",
    # 편의 함수들 (가장 많이 사용됨)
    "is_holiday",
    "is_weekend",
    "is_working_day",
    "get_holidays",
    "get_holiday_name",
    "get_next_holiday",
    "count_working_days",
    "add_working_days",
    # 데이터 관련
    "get_supported_years",
    "is_supported_year",
    "get_year_range",
    "get_year_statistics",
    # 유틸리티
    "parse_date_input",
    "get_weekday_korean",
    "format_date_korean",
]
