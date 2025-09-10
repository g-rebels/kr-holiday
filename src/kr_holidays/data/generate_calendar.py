#!/usr/bin/env python3
"""공공데이터포털 API를 사용한 공휴일 데이터 JSON 생성 스크립트

기존 Django 스크립트를 기반으로 JSON 파일 형태로 데이터를 생성합니다.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import requests

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# API 설정
API_URL = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo"
ACCESS_KEY = "VT35/KzRq57NWAlp7eeUzNIFcTcH851/2D8vDFKqn53POgFDWf2DwcQIBLbOcve/4+nSYVxD/38SGuu6nr90gw=="  # 여기에 실제 API 키를 입력하세요

# 요일 이름
WEEKDAYS = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]


def get_holidays_from_api(year: int) -> List[Dict]:
    """공공데이터포털 API로 공휴일 데이터 가져오기

    Args:
        year: 조회할 연도

    Returns:
        공휴일 데이터 리스트

    Raises:
        Exception: API 요청 실패 시
    """
    print(f"📡 {year}년 공휴일 데이터 API 요청 중...")

    params = {"ServiceKey": ACCESS_KEY, "solYear": str(year), "numOfRows": "100", "_type": "json"}

    try:
        response = requests.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"API 요청 실패: {e}")

    try:
        json_data = response.json()
    except json.JSONDecodeError as e:
        raise Exception(f"JSON 파싱 실패: {e}")

    # API 응답 구조 확인
    if "response" not in json_data:
        raise Exception("API 응답 형식 오류: response 키 없음")

    response_body = json_data["response"]["body"]
    if "items" not in response_body:
        print(f"⚠️ {year}년 공휴일 데이터 없음")
        return []

    items = response_body["items"]
    if not items or "item" not in items:
        print(f"⚠️ {year}년 공휴일 아이템 없음")
        return []

    # item이 단일 객체인 경우 리스트로 변환
    api_items = items["item"]
    if isinstance(api_items, dict):
        api_items = [api_items]

    holidays = []
    for item in api_items:
        try:
            date_num = int(item["locdate"])
            date_obj = datetime.strptime(str(date_num), "%Y%m%d")
            date_str = date_obj.strftime("%Y-%m-%d")

            holiday_name = item["dateName"]
            is_holiday = item["isHoliday"] == "Y"

            holidays.append(
                {
                    "date": date_str,
                    "holiday_name": holiday_name if is_holiday else "",
                    "is_holiday": is_holiday,
                }
            )
        except (ValueError, KeyError) as e:
            print(f"⚠️ 공휴일 데이터 파싱 오류: {item} - {e}")
            continue

    print(f"✅ {year}년 공휴일 {len(holidays)}개 수신")
    return holidays


def generate_all_dates_for_year(year: int) -> List[Dict]:
    """해당 연도의 모든 날짜 생성

    Args:
        year: 생성할 연도

    Returns:
        전체 날짜 정보 리스트
    """
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    delta = timedelta(days=1)

    all_dates = []
    current_date = start_date

    while current_date <= end_date:
        weekday_num = current_date.weekday()  # 0=월요일, 6=일요일

        date_info = {
            "year": year,
            "month": current_date.month,
            "date": current_date.day,
            "iso_date": current_date.strftime("%Y-%m-%d"),
            "weekday": WEEKDAYS[weekday_num],
            "weekday_num": weekday_num,
            "is_weekend": weekday_num >= 5,  # 토요일(5), 일요일(6)
            "is_holiday": False,
            "holiday_name": None,
            "is_substitute_holiday": False,
        }

        all_dates.append(date_info)
        current_date += delta

    return all_dates


def merge_holiday_data(all_dates: List[Dict], holidays: List[Dict]) -> List[Dict]:
    """전체 날짜 데이터에 공휴일 정보 병합

    Args:
        all_dates: 전체 날짜 데이터
        holidays: 공휴일 데이터

    Returns:
        공휴일 정보가 병합된 날짜 데이터
    """
    # 공휴일 데이터를 딕셔너리로 변환 (빠른 조회용)
    holiday_dict = {h["date"]: h for h in holidays}

    for date_info in all_dates:
        iso_date = date_info["iso_date"]

        if iso_date in holiday_dict:
            holiday_data = holiday_dict[iso_date]

            date_info["is_holiday"] = holiday_data["is_holiday"]
            date_info["holiday_name"] = holiday_data["holiday_name"]

            # 대체공휴일 체크
            if holiday_data["holiday_name"] == "대체공휴일":
                date_info["is_substitute_holiday"] = True

    return all_dates


def generate_json_file(year: int, use_api: bool = True) -> None:
    """특정 연도의 JSON 파일 생성

    Args:
        year: 생성할 연도
        use_api: API 사용 여부 (False면 임시 데이터)
    """
    print(f"\n📅 {year}년 데이터 생성 시작...")

    # 전체 날짜 생성
    all_dates = generate_all_dates_for_year(year)
    print(f"📋 {year}년 전체 날짜 {len(all_dates)}일 생성")

    # 공휴일 데이터 가져오기
    if use_api and ACCESS_KEY:
        try:
            holidays = get_holidays_from_api(year)

            print(holidays)
        except Exception as e:
            print(f"❌ API 오류: {e}")
            print("🔄 임시 데이터로 대체합니다.")
            holidays = []
    else:
        print("⚠️ API 키가 없어 임시 데이터 사용")
        holidays = []

    # 공휴일 정보 병합
    final_data = merge_holiday_data(all_dates, holidays)

    # 통계 계산
    total_days = len(final_data)
    holiday_days = sum(1 for d in final_data if d["is_holiday"])
    weekend_days = sum(1 for d in final_data if d["is_weekend"])
    substitute_holidays = sum(1 for d in final_data if d["is_substitute_holiday"])
    working_days = total_days - holiday_days - weekend_days

    # JSON 구조 생성
    json_data = {
        "year": year,
        "generated_at": datetime.now().isoformat(),
        "source": "공공데이터포털 API" if (use_api and ACCESS_KEY) else "임시 데이터",
        "api_url": API_URL if (use_api and ACCESS_KEY) else None,
        "statistics": {
            "total_days": total_days,
            "holiday_days": holiday_days,
            "weekend_days": weekend_days,
            "working_days": working_days,
            "substitute_holidays": substitute_holidays,
        },
        "days": final_data,
    }

    # 데이터 디렉토리 생성
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # JSON 파일 저장
    json_file = DATA_DIR / f"holidays_{year}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    # 결과 출력
    size_kb = json_file.stat().st_size / 1024
    print(f"✅ {json_file.name} 저장 완료 ({size_kb:.1f}KB)")
    print(f"   📊 전체: {total_days}일 | 공휴일: {holiday_days}일 | 주말: {weekend_days}일 | 평일: {working_days}일")
    if substitute_holidays > 0:
        print(f"   🔄 대체공휴일: {substitute_holidays}일")


def main():
    """메인 함수"""
    print("🚀 공휴일 데이터 JSON 생성 시작...\n")

    # API 키 확인
    if not ACCESS_KEY:
        print("⚠️  경고: ACCESS_KEY가 설정되지 않았습니다.")
        print("   스크립트 상단의 ACCESS_KEY 변수에 공공데이터포털 API 키를 입력하세요.")
        print("   현재는 임시 데이터로 진행합니다.\n")
        use_api = False
    else:
        use_api = True
        print(f"✅ API 키 설정 완료\n")

    # 생성할 연도 목록
    year_list = [
        2010,
        2011,
        2012,
        2013,
        2014,
        2015,
        2016,
        2017,
        2018,
        2019,
        2020,
        2021,
        2022,
        2023,
        2024,
        2025,
        2026,
        2027,
        2028,
        2029,
        2030,
        2031,
        2032,
        2033,
        2034,
        2035,
        2036,
        2037,
        2038,
        2039,
        2040,
    ]

    success_count = 0

    for year in year_list:
        try:
            generate_json_file(year, use_api)
            success_count += 1
        except Exception as e:
            print(f"❌ {year}년 데이터 생성 실패: {e}")

    print(f"\n✨ 데이터 생성 완료!")
    print(f"📈 성공: {success_count}/{len(year_list)}개 연도")
    print(f"📁 저장 위치: {DATA_DIR}")

    # 생성된 파일 목록
    if DATA_DIR.exists():
        print("\n📋 생성된 파일들:")
        for json_file in sorted(DATA_DIR.glob("holidays_*.json")):
            size_kb = json_file.stat().st_size / 1024
            print(f"  - {json_file.name} ({size_kb:.1f}KB)")


if __name__ == "__main__":
    main()
