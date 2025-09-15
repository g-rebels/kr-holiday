"""kr_holidays 패키지 기본 테스트"""

import pytest
from datetime import date, datetime
from kr_holidays import (
    is_holiday,
    is_weekend,
    is_working_day,
    get_holidays,
    get_holiday_name,
    get_next_holiday,
    count_working_days,
    KoreanHolidays,
    get_weekday_korean,
    get_weekday_korean_short,
    validate_year_range,
    format_date_korean,
    get_days_in_month,
    date_range,
    is_leap_year,
    get_month_range,
    parse_date_input,
)


class TestBasicFunctions:
    """기본 함수들 테스트"""

    def test_is_holiday_basic(self):
        """기본 공휴일 테스트"""
        # 신정
        assert is_holiday("2024-01-01") == True
        assert is_holiday(date(2024, 1, 1)) == True

        # 평일
        assert is_holiday("2024-01-02") == False
        assert is_holiday(date(2024, 1, 2)) == False

    def test_is_holiday_substitute(self):
        """대체공휴일 테스트"""
        # 어린이날 대체공휴일 (2024-05-06)
        assert is_holiday("2024-05-06") == True
        assert get_holiday_name("2024-05-06") == "대체공휴일(어린이날)"

    def test_is_weekend(self):
        """주말 테스트"""
        # 토요일
        assert is_weekend("2024-01-06") == True
        # 일요일
        assert is_weekend("2024-01-07") == True
        # 월요일
        assert is_weekend("2024-01-08") == False

    def test_is_working_day(self):
        """근무일 테스트"""
        # 평일 (근무일)
        assert is_working_day("2024-01-02") == True

        # 공휴일 (근무일 아님)
        assert is_working_day("2024-01-01") == False

        # 주말 (근무일 아님)
        assert is_working_day("2024-01-06") == False

    def test_get_holidays(self):
        """연도별 공휴일 조회 테스트"""
        holidays_2024 = get_holidays(2024)

        # 공휴일 개수 확인 (대략적)
        assert len(holidays_2024) >= 15  # 최소 15개 이상

        # 신정 포함 여부
        assert date(2024, 1, 1) in holidays_2024

        # 정렬 확인
        assert holidays_2024 == sorted(holidays_2024)

    def test_get_holiday_name(self):
        """공휴일 이름 조회 테스트"""
        # 신정
        assert get_holiday_name("2024-01-01") == "1월1일"

        # 평일 (공휴일 아님)
        assert get_holiday_name("2024-01-02") is None

    def test_get_next_holiday(self):
        """다음 공휴일 조회 테스트"""
        # 1월 2일 다음 공휴일
        next_holiday = get_next_holiday("2024-01-02")
        assert next_holiday is not None
        assert next_holiday > date(2024, 1, 2)

    def test_count_working_days(self):
        """근무일 계산 테스트"""
        # 1월 1일~7일 (월요일~일요일)
        # 1일(공휴일), 6일(토), 7일(일) 제외 = 4일
        working_days = count_working_days("2024-01-01", "2024-01-07")
        assert working_days == 4

    def test_date_string_formats(self):
        """다양한 날짜 형식 테스트"""
        # 다양한 문자열 형식
        assert is_holiday("2024-01-01") == True
        assert is_holiday("2024/01/01") == True
        assert is_holiday("20240101") == True

        # date 객체
        assert is_holiday(date(2024, 1, 1)) == True


class TestKoreanHolidaysClass:
    """KoreanHolidays 클래스 테스트"""

    def setup_method(self):
        """각 테스트 전 실행"""
        self.kh = KoreanHolidays()

    def test_class_methods(self):
        """클래스 메서드 테스트"""
        # 기본 기능들
        assert self.kh.is_holiday("2024-01-01") == True
        assert self.kh.is_working_day("2024-01-02") == True

        holidays = self.kh.get_holidays(2024)
        assert len(holidays) > 0

    def test_month_specific_methods(self):
        """월별 조회 메서드 테스트"""
        # 1월 공휴일 (신정만 있을 것)
        jan_holidays = self.kh.get_holidays_in_month(2024, 1)
        assert date(2024, 1, 1) in jan_holidays

        # 1월 근무일
        jan_workdays = self.kh.get_working_days_in_month(2024, 1)
        assert len(jan_workdays) > 0

    def test_working_days_calculation(self):
        """근무일 계산 관련 테스트"""
        # 근무일 더하기
        start_date = date(2024, 1, 2)  # 화요일
        result_date = self.kh.add_working_days(start_date, 5)

        # 5 근무일 후 날짜 확인
        assert result_date > start_date
        assert self.kh.is_working_day(result_date)

    def test_year_summary(self):
        """연도 요약 정보 테스트"""
        summary = self.kh.get_year_summary(2024)

        assert summary["year"] == 2024
        assert summary["supported"] == True
        assert "statistics" in summary
        assert "holidays" in summary


class TestErrorHandling:
    """에러 처리 테스트"""

    def test_unsupported_year(self):
        """지원하지 않는 연도 테스트"""
        with pytest.raises(ValueError):
            get_holidays(2000)  # 지원하지 않는 연도

    def test_invalid_date_format(self):
        """잘못된 날짜 형식 테스트"""
        with pytest.raises(ValueError):
            is_holiday("invalid-date")

    def test_invalid_month(self):
        """잘못된 월 테스트"""
        kh = KoreanHolidays()
        with pytest.raises(ValueError):
            kh.get_holidays_in_month(2024, 13)  # 13월은 없음


class TestSpecificHolidays:
    """특정 공휴일 테스트"""

    def test_lunar_holidays(self):
        """음력 공휴일 테스트"""
        # 설날 연휴 (2024년 기준)
        assert is_holiday("2024-02-10")  # 설날
        assert get_holiday_name("2024-02-10") == "설날"

    def test_substitute_holidays(self):
        """대체공휴일 존재 여부 테스트"""
        # 알려진 대체공휴일들
        substitute_dates = [
            "2024-05-06",  # 어린이날 대체공휴일
        ]

        kh = KoreanHolidays()
        for date_str in substitute_dates:
            # 공휴일이면서 대체공휴일이어야 함
            assert is_holiday(date_str) == True
            assert kh.is_substitute_holiday(date_str) == True

            # 이름 존재 여부
            holiday_name = get_holiday_name(date_str)
            assert holiday_name is not None
            assert len(holiday_name) > 0

    def test_temporary_holidays(self):
        """임시공휴일 테스트"""
        # 2024년 10월 1일 임시공휴일
        assert is_holiday("2024-10-01") == True
        # 실제 API 데이터에 따라 이름이 달라질 수 있음


class TestUtils:

    def test_get_weekday_korean(self):
        assert get_weekday_korean(date(2025, 1, 1)) == "수요일"

    def test_get_weekday_korean_short(self):
        assert get_weekday_korean_short(date(2025, 1, 3)) == "금"

    def test_validate_year_range(self):
        with pytest.raises(ValueError):
            validate_year_range(year="2024")  # 타입 오류

        with pytest.raises(ValueError):
            validate_year_range(year=2000)  # 범위 오류 (2000 < 2010)

        with pytest.raises(ValueError):
            validate_year_range(year=2050)  # 범위 오류 (2050 > 2040)

        # 정상 케이스
        validate_year_range(year=2025) == None  # 예외 발생하지 않음

    def test_format_date_korean(self):
        assert format_date_korean(date(2025, 1, 2)) == "2025년 1월 2일 (목요일)"

        assert format_date_korean(date(2025, 1, 2), include_weekday=False) == "2025년 1월 2일"

    def test_get_days_in_month(self):
        assert get_days_in_month(year=2025, month=2) == 28

    def test_date_range(self):

        assert date_range(date(2024, 2, 1), date(2024, 2, 4)) == [
            date(2024, 2, 1),
            date(2024, 2, 2),
            date(2024, 2, 3),
            date(2024, 2, 4),
        ]

    def test_is_leap_year(self):

        assert is_leap_year(year=2024) == True
        assert is_leap_year(year=2032) == True
        assert is_leap_year(year=2025) == False
        assert is_leap_year(year=2030) == False

    def test_get_month_range(self):

        with pytest.raises(ValueError):
            get_month_range(year=2025, month=13)

        assert get_month_range(year=2025, month=7) == (date(2025, 7, 1), date(2025, 7, 31))

    def test_parse_date_input(self):

        assert parse_date_input(date(2025, 7, 31)) == date(2025, 7, 31)
        assert parse_date_input(datetime(2025, 7, 31, 14, 30, 45)) == date(2025, 7, 31)

        assert parse_date_input("2025-07-31") == date(2025, 7, 31)
        assert parse_date_input("2025/07/31") == date(2025, 7, 31)
        assert parse_date_input("20250731") == date(2025, 7, 31)
        assert parse_date_input("2025.07.31") == date(2025, 7, 31)

        with pytest.raises(ValueError):
            parse_date_input("2025.07/31")

        with pytest.raises(TypeError):
            parse_date_input(20250201)


if __name__ == "__main__":
    # 직접 실행 시 테스트 수행
    pytest.main([__file__, "-v"])
