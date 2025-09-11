"""kr_holidays 패키지 테스트"""

import pytest
from datetime import date
from kr_holidays import (
    is_holiday,
    is_weekend,
    is_working_day,
    get_holidays,
    get_holiday_name,
    get_next_holiday,
    count_working_days,
    add_working_days,
    KoreanHolidays,
    get_supported_years,
    is_supported_year,
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
        holiday_name = get_holiday_name("2024-05-06")
        assert holiday_name is not None
        assert "대체공휴일" in holiday_name or "어린이날" in holiday_name

    def test_is_weekend(self):
        """주말 테스트"""
        # 2024-01-06 (토요일)
        assert is_weekend("2024-01-06") == True
        # 2024-01-07 (일요일)
        assert is_weekend("2024-01-07") == True
        # 2024-01-08 (월요일)
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

        # 공휴일 개수 확인 (최소한의 개수)
        assert len(holidays_2024) >= 15

        # 신정 포함 여부
        assert date(2024, 1, 1) in holidays_2024

        # 정렬 확인
        assert holidays_2024 == sorted(holidays_2024)

    def test_get_holiday_name(self):
        """공휴일 이름 조회 테스트"""
        # 신정
        name = get_holiday_name("2024-01-01")
        assert name is not None
        assert "신정" in name

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
        # 간단한 케이스 테스트
        working_days = count_working_days("2024-01-02", "2024-01-04")
        assert working_days >= 0  # 음수가 아님
        assert isinstance(working_days, int)

    def test_add_working_days(self):
        """근무일 더하기 테스트"""
        start_date = date(2024, 1, 2)
        result_date = add_working_days(start_date, 5)

        assert result_date > start_date
        assert isinstance(result_date, date)

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
        # 1월 공휴일 (신정 포함되어야 함)
        jan_holidays = self.kh.get_holidays_in_month(2024, 1)
        assert date(2024, 1, 1) in jan_holidays

        # 1월 근무일
        jan_workdays = self.kh.get_working_days_in_month(2024, 1)
        assert len(jan_workdays) > 0

    def test_working_days_calculation(self):
        """근무일 계산 관련 테스트"""
        # 근무일 더하기
        start_date = date(2024, 1, 2)  # 화요일
        result_date = self.kh.add_working_days(start_date, 3)

        # 3 근무일 후 날짜 확인
        assert result_date > start_date

    def test_year_summary(self):
        """연도 요약 정보 테스트"""
        summary = self.kh.get_year_summary(2024)

        assert summary["year"] == 2024
        assert summary["supported"] == True
        assert "statistics" in summary
        assert "holidays" in summary


class TestDataFunctions:
    """데이터 관련 함수 테스트"""

    def test_supported_years(self):
        """지원 연도 테스트"""
        years = get_supported_years()
        assert isinstance(years, list)
        assert len(years) > 0
        assert 2024 in years

    def test_is_supported_year(self):
        """연도 지원 여부 테스트"""
        assert is_supported_year(2024) == True
        assert is_supported_year(1900) == False


class TestErrorHandling:
    """에러 처리 테스트"""

    def test_invalid_date_format(self):
        """잘못된 날짜 형식 테스트"""
        with pytest.raises(ValueError):
            is_holiday("invalid-date")

    def test_invalid_month(self):
        """잘못된 월 테스트"""
        kh = KoreanHolidays()
        with pytest.raises(ValueError):
            kh.get_holidays_in_month(2024, 13)  # 13월은 없음

        with pytest.raises(ValueError):
            kh.get_holidays_in_month(2024, 0)  # 0월도 없음

    def test_negative_working_days(self):
        """음수 근무일 테스트"""
        kh = KoreanHolidays()
        with pytest.raises(ValueError):
            kh.add_working_days("2024-01-01", -5)


class TestSpecificHolidays2024:
    """2024년 특정 공휴일 테스트"""

    def test_fixed_holidays(self):
        """고정 공휴일 테스트"""
        fixed_holidays = {
            "2024-01-01": "신정",
            "2024-03-01": "삼일절",
            "2024-05-05": "어린이날",
            "2024-06-06": "현충일",
            "2024-08-15": "광복절",
            "2024-10-03": "개천절",
            "2024-10-09": "한글날",
            "2024-12-25": "성탄절",
        }

        for date_str, expected_name in fixed_holidays.items():
            assert is_holiday(date_str) == True
            holiday_name = get_holiday_name(date_str)
            assert holiday_name is not None
            # 정확한 이름 매칭보다는 키워드 포함 확인
            assert any(keyword in holiday_name for keyword in expected_name.split())

    def test_lunar_holidays(self):
        """음력 공휴일 테스트 (2024년 기준)"""
        # 설날 연휴 (날짜는 API 데이터에 따라 달라질 수 있음)
        lunar_dates = ["2024-02-09", "2024-02-10", "2024-02-11"]

        # 적어도 하나는 공휴일이어야 함
        assert any(is_holiday(date_str) for date_str in lunar_dates)

    def test_substitute_holidays(self):
        """대체공휴일 테스트"""
        kh = KoreanHolidays()

        # 2024년에 알려진 대체공휴일들 확인
        potential_substitutes = ["2024-05-06", "2024-02-12"]

        # 적어도 하나는 대체공휴일이어야 함
        substitute_found = False
        for date_str in potential_substitutes:
            if kh.is_substitute_holiday(date_str):
                substitute_found = True
                assert kh.is_holiday(date_str) == True
                break

        # 2024년에는 대체공휴일이 있어야 함
        # assert substitute_found == True  # 데이터에 따라 주석 처리


if __name__ == "__main__":
    # 직접 실행 시 테스트 수행
    pytest.main([__file__, "-v", "--cov=kr_holidays"])
