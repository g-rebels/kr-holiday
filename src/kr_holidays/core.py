"""한국 공휴일 메인 API (비즈니스 로직 레이어)

사용자가 주로 사용할 고수준 API와 복잡한 비즈니스 로직을 제공합니다.
data.py의 원시 데이터를 활용하여 실용적인 기능들을 구현합니다.
"""

from datetime import date, timedelta
from typing import List, Optional, Union, Tuple

from .data import get_day_info, get_year_days_data, get_supported_years, is_supported_year, get_year_statistics
from .utils import (
    parse_date_input,
    get_weekday_korean,
    is_weekend_by_weekday,
    get_month_range,
    date_range,
    validate_year_range,
)


class KoreanHolidays:
    """한국 공휴일 메인 클래스

    한국의 공휴일, 대체공휴일, 주말 정보를 조회하고
    업무일 계산 등의 고급 기능을 제공합니다.

    Examples:
        >>> kh = KoreanHolidays()
        >>> kh.is_holiday('2024-01-01')
        True
        >>> kh.get_next_holiday('2024-01-02')
        date(2024, 2, 9)
    """

    def is_holiday(self, target_date: Union[str, date]) -> bool:
        """특정 날짜가 공휴일인지 확인

        Args:
            target_date: 확인할 날짜 (문자열 또는 date 객체)

        Returns:
            공휴일 여부

        Examples:
            >>> kh = KoreanHolidays()
            >>> kh.is_holiday('2024-01-01')
            True
            >>> kh.is_holiday('2024-01-02')
            False
        """
        parsed_date = parse_date_input(target_date)
        day_info = get_day_info(parsed_date)
        return day_info.get("is_holiday", False) if day_info else False

    def is_weekend(self, target_date: Union[str, date]) -> bool:
        """특정 날짜가 주말인지 확인

        Args:
            target_date: 확인할 날짜

        Returns:
            주말 여부 (토요일, 일요일)
        """
        parsed_date = parse_date_input(target_date)
        day_info = get_day_info(parsed_date)

        if day_info:
            return day_info.get("is_weekend", False)

        # 데이터가 없으면 요일로 계산
        return is_weekend_by_weekday(parsed_date)

    def is_substitute_holiday(self, target_date: Union[str, date]) -> bool:
        """특정 날짜가 대체공휴일인지 확인

        Args:
            target_date: 확인할 날짜

        Returns:
            대체공휴일 여부
        """
        parsed_date = parse_date_input(target_date)
        day_info = get_day_info(parsed_date)
        return day_info.get("is_substitute_holiday", False) if day_info else False

    def is_working_day(self, target_date: Union[str, date]) -> bool:
        """특정 날짜가 근무일(평일이면서 공휴일이 아님)인지 확인

        Args:
            target_date: 확인할 날짜

        Returns:
            근무일 여부
        """
        parsed_date = parse_date_input(target_date)
        return not self.is_weekend(parsed_date) and not self.is_holiday(parsed_date)

    def get_holiday_name(self, target_date: Union[str, date]) -> Optional[str]:
        """특정 날짜의 공휴일 이름 반환

        Args:
            target_date: 조회할 날짜

        Returns:
            공휴일 이름 또는 None (공휴일이 아닌 경우)
        """
        parsed_date = parse_date_input(target_date)
        day_info = get_day_info(parsed_date)

        if day_info and day_info.get("is_holiday", False):
            return day_info.get("holiday_name")

        return None

    def get_holidays(self, year: int) -> List[date]:
        """특정 연도의 모든 공휴일 목록 반환

        Args:
            year: 조회할 연도

        Returns:
            해당 연도의 공휴일 날짜 리스트 (날짜순 정렬)

        Raises:
            FileNotFoundError: 해당 연도의 데이터가 없는 경우
            ValueError: 잘못된 연도인 경우
        """
        validate_year_range(year)

        try:
            year_days = get_year_days_data(year)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"{year}년 공휴일 데이터를 찾을 수 없습니다. " f"지원 연도: {get_supported_years()}"
            )

        holidays = []
        for day_info in year_days:
            if day_info.get("is_holiday", False):
                holiday_date = date(day_info["year"], day_info["month"], day_info["date"])
                holidays.append(holiday_date)

        return holidays

    def get_holidays_in_month(self, year: int, month: int) -> List[date]:
        """특정 연월의 공휴일 목록 반환

        Args:
            year: 연도
            month: 월 (1-12)

        Returns:
            해당 월의 공휴일 날짜 리스트
        """
        validate_year_range(year)
        get_month_range(year, month)  # 월 유효성 검사

        try:
            year_days = get_year_days_data(year)
        except FileNotFoundError:
            return []

        holidays = []
        for day_info in year_days:
            if day_info["month"] == month and day_info.get("is_holiday", False):
                holiday_date = date(day_info["year"], day_info["month"], day_info["date"])
                holidays.append(holiday_date)

        return holidays

    def get_working_days_in_month(self, year: int, month: int) -> List[date]:
        """특정 연월의 근무일 목록 반환

        Args:
            year: 연도
            month: 월 (1-12)

        Returns:
            해당 월의 근무일 날짜 리스트
        """
        validate_year_range(year)
        get_month_range(year, month)  # 월 유효성 검사

        try:
            year_days = get_year_days_data(year)
        except FileNotFoundError:
            return []

        working_days = []
        for day_info in year_days:
            if (
                day_info["month"] == month
                and not day_info.get("is_holiday", False)
                and not day_info.get("is_weekend", False)
            ):
                working_date = date(day_info["year"], day_info["month"], day_info["date"])
                working_days.append(working_date)

        return working_days

    def get_next_holiday(self, from_date: Union[str, date]) -> Optional[date]:
        """특정 날짜 이후의 다음 공휴일 반환

        Args:
            from_date: 기준 날짜

        Returns:
            다음 공휴일 날짜 또는 None (해당 연도에 더 이상 공휴일이 없는 경우)
        """
        start_date = parse_date_input(from_date)

        try:
            holidays = self.get_holidays(start_date.year)
        except FileNotFoundError:
            return None

        # 기준 날짜보다 나중인 공휴일 찾기
        for holiday in holidays:
            if holiday > start_date:
                return holiday

        return None

    def get_previous_holiday(self, from_date: Union[str, date]) -> Optional[date]:
        """특정 날짜 이전의 직전 공휴일 반환

        Args:
            from_date: 기준 날짜

        Returns:
            직전 공휴일 날짜 또는 None (해당 연도에 이전 공휴일이 없는 경우)
        """
        end_date = parse_date_input(from_date)

        try:
            holidays = self.get_holidays(end_date.year)
        except FileNotFoundError:
            return None

        # 기준 날짜보다 이전인 공휴일 중 가장 최근 것 찾기
        previous_holidays = [h for h in holidays if h < end_date]
        return max(previous_holidays) if previous_holidays else None

    def count_working_days(self, start_date: Union[str, date], end_date: Union[str, date]) -> int:
        """두 날짜 사이의 근무일 수 계산 (시작일, 종료일 포함)

        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜

        Returns:
            근무일 수

        Examples:
            >>> kh = KoreanHolidays()
            >>> kh.count_working_days('2024-01-01', '2024-01-07')
            5  # 1/1(공휴일), 1/6(토), 1/7(일) 제외
        """
        start = parse_date_input(start_date)
        end = parse_date_input(end_date)

        if start > end:
            return 0

        working_days = 0
        dates = date_range(start, end)

        for current_date in dates:
            if self.is_working_day(current_date):
                working_days += 1

        return working_days

    def count_holidays(self, start_date: Union[str, date], end_date: Union[str, date]) -> int:
        """두 날짜 사이의 공휴일 수 계산 (시작일, 종료일 포함)

        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜

        Returns:
            공휴일 수
        """
        start = parse_date_input(start_date)
        end = parse_date_input(end_date)

        if start > end:
            return 0

        holiday_count = 0
        dates = date_range(start, end)

        for current_date in dates:
            if self.is_holiday(current_date):
                holiday_count += 1

        return holiday_count

    def add_working_days(self, start_date: Union[str, date], working_days: int) -> date:
        """시작 날짜에 근무일 수를 더한 날짜 계산 (공휴일과 주말 모두 제외)

        Args:
            start_date: 시작 날짜
            working_days: 더할 근무일 수 (양수만 지원)

        Returns:
            계산된 날짜

        Raises:
            ValueError: 음수 근무일이 입력된 경우

        Examples:
            >>> kh = KoreanHolidays()
            >>> kh.add_working_days('2024-01-01', 5)  # 1/1은 공휴일
            date(2024, 1, 8)  # 공휴일과 주말을 건너뛰고 5 근무일 후
        """
        if working_days < 0:
            raise ValueError("근무일 수는 0 이상이어야 합니다.")

        if working_days == 0:
            return parse_date_input(start_date)

        current_date = parse_date_input(start_date)
        remaining_days = working_days

        while remaining_days > 0:
            current_date += timedelta(days=1)

            # 근무일인 경우에만 카운트 감소
            if self.is_working_day(current_date):
                remaining_days -= 1

        return current_date

    def get_year_summary(self, year: int) -> dict:
        """특정 연도의 공휴일 요약 정보 반환

        Args:
            year: 조회할 연도

        Returns:
            연도별 요약 정보 딕셔너리
        """
        validate_year_range(year)

        if not is_supported_year(year):
            return {
                "year": year,
                "supported": False,
                "message": f"지원하지 않는 연도입니다. 지원 연도: {get_supported_years()}",
            }

        try:
            holidays = self.get_holidays(year)
            statistics = get_year_statistics(year)

            # 대체공휴일 개수 계산
            substitute_count = 0
            for holiday_date in holidays:
                if self.is_substitute_holiday(holiday_date):
                    substitute_count += 1

            return {
                "year": year,
                "supported": True,
                "statistics": statistics,
                "substitute_holidays": substitute_count,
                "holidays": [
                    {
                        "date": holiday_date.isoformat(),
                        "name": self.get_holiday_name(holiday_date),
                        "weekday": get_weekday_korean(holiday_date),
                        "is_substitute": self.is_substitute_holiday(holiday_date),
                    }
                    for holiday_date in holidays
                ],
            }
        except FileNotFoundError:
            return {"year": year, "supported": False, "message": "데이터 파일을 찾을 수 없습니다."}


# 편의 함수들 (전역 KoreanHolidays 인스턴스 사용)
_default_instance = KoreanHolidays()


def is_holiday(target_date: Union[str, date]) -> bool:
    """특정 날짜가 공휴일인지 확인 (편의 함수)

    Args:
        target_date: 확인할 날짜

    Returns:
        공휴일 여부
    """
    return _default_instance.is_holiday(target_date)


def is_weekend(target_date: Union[str, date]) -> bool:
    """특정 날짜가 주말인지 확인 (편의 함수)

    Args:
        target_date: 확인할 날짜

    Returns:
        주말 여부
    """
    return _default_instance.is_weekend(target_date)


def is_working_day(target_date: Union[str, date]) -> bool:
    """특정 날짜가 근무일인지 확인 (편의 함수)

    Args:
        target_date: 확인할 날짜

    Returns:
        근무일 여부
    """
    return _default_instance.is_working_day(target_date)


def get_holidays(year: int) -> List[date]:
    """특정 연도의 모든 공휴일 목록 반환 (편의 함수)

    Args:
        year: 조회할 연도

    Returns:
        해당 연도의 공휴일 날짜 리스트
    """
    return _default_instance.get_holidays(year)


def get_holiday_name(target_date: Union[str, date]) -> Optional[str]:
    """특정 날짜의 공휴일 이름 반환 (편의 함수)

    Args:
        target_date: 조회할 날짜

    Returns:
        공휴일 이름 또는 None
    """
    return _default_instance.get_holiday_name(target_date)


def get_next_holiday(from_date: Union[str, date]) -> Optional[date]:
    """특정 날짜 이후의 다음 공휴일 반환 (편의 함수)

    Args:
        from_date: 기준 날짜

    Returns:
        다음 공휴일 날짜 또는 None
    """
    return _default_instance.get_next_holiday(from_date)


def count_working_days(start_date: Union[str, date], end_date: Union[str, date]) -> int:
    """두 날짜 사이의 근무일 수 계산 (편의 함수)

    Args:
        start_date: 시작 날짜
        end_date: 종료 날짜

    Returns:
        근무일 수
    """
    return _default_instance.count_working_days(start_date, end_date)


def add_working_days(start_date: Union[str, date], working_days: int) -> date:
    """시작 날짜에 근무일 수를 더한 날짜 계산 (편의 함수)

    Args:
        start_date: 시작 날짜
        working_days: 더할 근무일 수

    Returns:
        계산된 날짜
    """
    return _default_instance.add_working_days(start_date, working_days)
