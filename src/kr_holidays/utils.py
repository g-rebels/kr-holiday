"""한국 공휴일 유틸리티 함수들 (유틸리티 레이어)

날짜 파싱, 변환, 계산 등의 범용 유틸리티 함수들을 제공합니다.
비즈니스 로직과 데이터 로직에서 공통으로 사용되는 헬퍼 함수들입니다.
"""

from datetime import date, datetime, timedelta
from typing import Union, Tuple


def parse_date_input(date_input: Union[str, date, datetime]) -> date:
    """다양한 형태의 날짜 입력을 date 객체로 변환

    Args:
        date_input: 날짜 문자열, date 객체, 또는 datetime 객체

    Returns:
        변환된 date 객체

    Raises:
        ValueError: 날짜 형식이 올바르지 않은 경우
        TypeError: 지원하지 않는 타입인 경우

    Examples:
        >>> parse_date_input("2024-01-01")
        date(2024, 1, 1)
        >>> parse_date_input("2024/01/01")
        date(2024, 1, 1)
        >>> parse_date_input("20240101")
        date(2024, 1, 1)
    """
    if isinstance(date_input, date):
        return date_input

    if isinstance(date_input, datetime):
        return date_input.date()

    if isinstance(date_input, str):
        # 다양한 날짜 형식 지원
        date_formats = [
            "%Y-%m-%d",  # 2024-01-01
            "%Y/%m/%d",  # 2024/01/01
            "%Y%m%d",  # 20240101
            "%Y.%m.%d",  # 2024.01.01
        ]

        for date_format in date_formats:
            try:
                return datetime.strptime(date_input, date_format).date()
            except ValueError:
                continue

        raise ValueError(f"지원하지 않는 날짜 형식입니다: {date_input}")

    raise TypeError(f"지원하지 않는 날짜 타입입니다: {type(date_input)}")


def get_weekday_korean(target_date: date) -> str:
    """날짜의 한국어 요일명 반환

    Args:
        target_date: 조회할 날짜

    Returns:
        한국어 요일명 (예: "월요일", "화요일")
    """
    weekdays = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    return weekdays[target_date.weekday()]


def get_weekday_korean_short(target_date: date) -> str:
    """날짜의 한국어 요일명 반환 (축약형)

    Args:
        target_date: 조회할 날짜

    Returns:
        한국어 요일명 축약형 (예: "월", "화")
    """
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    return weekdays[target_date.weekday()]


def is_weekend_by_weekday(target_date: date) -> bool:
    """요일을 기준으로 주말 여부 확인 (토, 일)

    Args:
        target_date: 확인할 날짜

    Returns:
        주말 여부 (토요일, 일요일)
    """
    return target_date.weekday() >= 5


def add_business_days(start_date: date, business_days: int) -> date:
    """시작 날짜에 영업일 수를 더한 날짜 계산 (주말만 제외, 공휴일 미고려)

    Args:
        start_date: 시작 날짜
        business_days: 더할 영업일 수 (양수/음수 모두 가능)

    Returns:
        계산된 날짜

    Note:
        이 함수는 주말만 제외하고, 공휴일은 고려하지 않습니다.
        공휴일을 고려한 계산은 core.py의 함수들을 사용하세요.
    """
    if business_days == 0:
        return start_date

    current_date = start_date
    remaining_days = abs(business_days)
    direction = 1 if business_days > 0 else -1

    while remaining_days > 0:
        current_date += timedelta(days=direction)

        # 평일인 경우에만 카운트 감소
        if not is_weekend_by_weekday(current_date):
            remaining_days -= 1

    return current_date


def get_month_range(year: int, month: int) -> Tuple[date, date]:
    """특정 연월의 시작일과 마지막일 반환

    Args:
        year: 연도
        month: 월 (1-12)

    Returns:
        (월 시작일, 월 마지막일) 튜플

    Raises:
        ValueError: 잘못된 연도나 월인 경우
    """
    if not (1 <= month <= 12):
        raise ValueError(f"월은 1-12 사이여야 합니다: {month}")

    try:
        start_date = date(year, month, 1)

        # 다음 달의 1일에서 하루를 빼서 이번 달 마지막일 구하기
        if month == 12:
            next_month_start = date(year + 1, 1, 1)
        else:
            next_month_start = date(year, month + 1, 1)

        end_date = next_month_start - timedelta(days=1)

        return (start_date, end_date)

    except ValueError as e:
        raise ValueError(f"잘못된 연도 또는 월입니다: {year}-{month}") from e


def is_leap_year(year: int) -> bool:
    """윤년 여부 확인

    Args:
        year: 확인할 연도

    Returns:
        윤년 여부
    """
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def get_days_in_month(year: int, month: int) -> int:
    """특정 연월의 일수 반환

    Args:
        year: 연도
        month: 월 (1-12)

    Returns:
        해당 월의 일수
    """
    start_date, end_date = get_month_range(year, month)
    return end_date.day


def date_range(start_date: date, end_date: date, step: int = 1) -> list[date]:
    """두 날짜 사이의 모든 날짜를 생성

    Args:
        start_date: 시작 날짜 (포함)
        end_date: 종료 날짜 (포함)
        step: 날짜 간격 (기본값: 1일)

    Returns:
        날짜 리스트

    Examples:
        >>> date_range(date(2024, 1, 1), date(2024, 1, 3))
        [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)]
    """
    if start_date > end_date:
        return []

    dates = []
    current_date = start_date

    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=step)

    return dates


def format_date_korean(target_date: date, include_weekday: bool = True) -> str:
    """날짜를 한국어 형식으로 포맷팅

    Args:
        target_date: 포맷할 날짜
        include_weekday: 요일 포함 여부

    Returns:
        한국어 형식의 날짜 문자열

    Examples:
        >>> format_date_korean(date(2024, 1, 1))
        "2024년 1월 1일 (월요일)"
        >>> format_date_korean(date(2024, 1, 1), include_weekday=False)
        "2024년 1월 1일"
    """
    formatted = f"{target_date.year}년 {target_date.month}월 {target_date.day}일"

    if include_weekday:
        weekday = get_weekday_korean(target_date)
        formatted += f" ({weekday})"

    return formatted


def validate_year_range(year: int, min_year: int = 1900, max_year: int = 2100) -> None:
    """연도 유효성 검사

    Args:
        year: 검사할 연도
        min_year: 최소 연도 (기본값: 1900)
        max_year: 최대 연도 (기본값: 2100)

    Raises:
        ValueError: 연도가 유효 범위를 벗어난 경우
    """
    if not isinstance(year, int):
        raise ValueError(f"연도는 정수여야 합니다: {type(year)}")

    if not (min_year <= year <= max_year):
        raise ValueError(f"연도는 {min_year}~{max_year} 범위 내여야 합니다: {year}")
