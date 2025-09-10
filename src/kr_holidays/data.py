"""한국 공휴일 데이터 로더 (데이터 레이어)

JSON 파일에서 데이터를 로드하고 캐싱하는 순수 데이터 접근 모듈입니다.
비즈니스 로직은 포함하지 않고, 오직 데이터 I/O와 캐싱만 담당합니다.
"""

import json
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 데이터 디렉토리 경로
DATA_DIR = Path(__file__).parent / "data"

# 캐시된 데이터
_year_data_cache: Dict[int, Dict] = {}
_supported_years_cache: Optional[List[int]] = None


def load_year_data(year: int) -> Dict:
    """JSON 파일에서 특정 연도의 전체 데이터 로드

    Args:
        year: 로드할 연도

    Returns:
        연도 전체 데이터 딕셔너리

    Raises:
        FileNotFoundError: 해당 연도의 데이터 파일이 없는 경우
        ValueError: JSON 파일 파싱 오류
    """
    # 캐시에서 확인
    if year in _year_data_cache:
        return _year_data_cache[year]

    # JSON 파일 경로
    json_file = DATA_DIR / f"holidays_{year}.json"

    if not json_file.exists():
        raise FileNotFoundError(
            f"공휴일 데이터 파일을 찾을 수 없습니다: {json_file}\n"
            f"scripts/generate_temp_data.py를 실행해서 데이터를 생성하세요."
        )

    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 캐시 저장
        _year_data_cache[year] = data
        return data

    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파일 파싱 오류 ({json_file}): {e}")


def get_day_info(target_date: date) -> Optional[Dict]:
    """특정 날짜의 상세 정보 반환 (원시 데이터)

    Args:
        target_date: 조회할 날짜

    Returns:
        날짜 상세 정보 딕셔너리 또는 None (데이터가 없는 경우)
    """
    try:
        year_data = load_year_data(target_date.year)
    except (FileNotFoundError, ValueError):
        return None

    # 해당 날짜 찾기
    for day_info in year_data.get("days", []):
        if (
            day_info["year"] == target_date.year
            and day_info["month"] == target_date.month
            and day_info["date"] == target_date.day
        ):
            return day_info.copy()

    return None


def get_year_days_data(year: int) -> List[Dict]:
    """특정 연도의 모든 일별 데이터 반환

    Args:
        year: 조회할 연도

    Returns:
        해당 연도의 모든 일별 데이터 리스트

    Raises:
        FileNotFoundError: 해당 연도의 데이터 파일이 없는 경우
        ValueError: JSON 파일 파싱 오류
    """
    year_data = load_year_data(year)
    return year_data.get("days", [])


def get_year_statistics(year: int) -> Optional[Dict]:
    """특정 연도의 통계 정보 반환

    Args:
        year: 조회할 연도

    Returns:
        통계 정보 딕셔너리 또는 None
    """
    try:
        year_data = load_year_data(year)
        return year_data.get("statistics", {})
    except (FileNotFoundError, ValueError):
        return None


def get_supported_years() -> List[int]:
    """지원하는 모든 연도 반환

    Returns:
        지원하는 연도 리스트 (오름차순)
    """
    global _supported_years_cache

    if _supported_years_cache is not None:
        return _supported_years_cache.copy()

    # data 디렉토리에서 JSON 파일들 스캔
    if not DATA_DIR.exists():
        _supported_years_cache = []
        return []

    years = []
    for json_file in DATA_DIR.glob("holidays_*.json"):
        try:
            # 파일명에서 연도 추출: holidays_2024.json -> 2024
            year_str = json_file.stem.split("_")[1]
            year = int(year_str)
            years.append(year)
        except (IndexError, ValueError):
            continue  # 파일명 형식이 맞지 않으면 무시

    years.sort()
    _supported_years_cache = years
    return years.copy()


def is_supported_year(year: int) -> bool:
    """지원하는 연도인지 확인

    Args:
        year: 확인할 연도

    Returns:
        지원 여부
    """
    return year in get_supported_years()


def get_year_range() -> Tuple[int, int]:
    """지원하는 연도 범위 반환

    Returns:
        (최소 연도, 최대 연도) 튜플. 지원하는 연도가 없으면 (0, 0)
    """
    years = get_supported_years()
    if not years:
        return (0, 0)
    return (min(years), max(years))


def clear_cache() -> None:
    """캐시된 데이터 모두 삭제"""
    global _year_data_cache, _supported_years_cache
    _year_data_cache.clear()
    _supported_years_cache = None


def get_data_dir() -> Path:
    """데이터 디렉토리 경로 반환"""
    return DATA_DIR


def get_data_source_info(year: int) -> Optional[Dict]:
    """데이터 소스 정보 반환 (언제, 어디서 생성되었는지)

    Args:
        year: 조회할 연도

    Returns:
        소스 정보 딕셔너리 (generated_at, source, api_url 등)
    """
    try:
        year_data = load_year_data(year)
        return {
            "year": year_data.get("year"),
            "generated_at": year_data.get("generated_at"),
            "source": year_data.get("source"),
            "api_url": year_data.get("api_url"),
        }
    except (FileNotFoundError, ValueError):
        return None
