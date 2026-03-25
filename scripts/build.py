#!/usr/bin/env python3
"""
빌드 스크립트: JSON 데이터 + HTML 템플릿 → 최종 index.html 생성

사용법:
  python build.py                    # 기본 경로로 빌드
  python build.py --data-dir ../data --template ../templates/dashboard.html --output ../배포/index.html

구조:
  data/announcements.json  →  공고 데이터
  data/sources.json        →  소스 목록
  templates/dashboard.html →  HTML 템플릿 (플레이스홀더 포함)
  배포/index.html          →  최종 빌드 결과
"""

import json
import os
import sys
import argparse


def build(data_dir, template_path, output_path):
    """JSON 데이터를 템플릿에 주입하여 최종 HTML 생성"""

    # 1. 데이터 로드
    ann_path = os.path.join(data_dir, 'announcements.json')
    src_path = os.path.join(data_dir, 'sources.json')

    if not os.path.exists(ann_path):
        print(f"[ERROR] announcements.json not found: {ann_path}")
        sys.exit(1)
    if not os.path.exists(src_path):
        print(f"[ERROR] sources.json not found: {src_path}")
        sys.exit(1)
    if not os.path.exists(template_path):
        print(f"[ERROR] template not found: {template_path}")
        sys.exit(1)

    with open(ann_path, 'r', encoding='utf-8') as f:
        announcements = json.load(f)
    with open(src_path, 'r', encoding='utf-8') as f:
        sources = json.load(f)

    print(f"[INFO] 공고 데이터: {len(announcements)}건 로드")
    print(f"[INFO] 소스 데이터: {len(sources)}건 로드")

    # 2. 데이터 → JS 문자열 변환
    ann_js = json.dumps(announcements, ensure_ascii=False, indent=2)
    src_js = json.dumps(sources, ensure_ascii=False, indent=2)

    # 3. 템플릿 로드
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # 4. 플레이스홀더 치환
    #    템플릿에는 다음과 같은 플레이스홀더가 있음:
    #    const announcements = /*__ANNOUNCEMENTS_DATA__*/[];
    #    const sources = /*__SOURCES_DATA__*/[];
    result = template.replace('/*__ANNOUNCEMENTS_DATA__*/[]', ann_js)
    result = result.replace('/*__SOURCES_DATA__*/[]', src_js)

    # 치환 확인
    if '/*__ANNOUNCEMENTS_DATA__*/' in result:
        print("[WARN] ANNOUNCEMENTS_DATA 플레이스홀더가 치환되지 않았습니다!")
    if '/*__SOURCES_DATA__*/' in result:
        print("[WARN] SOURCES_DATA 플레이스홀더가 치환되지 않았습니다!")

    # 5. 출력
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result)

    file_size = os.path.getsize(output_path)
    active_count = len([a for a in announcements if not a.get('closed', False)])
    closed_count = len([a for a in announcements if a.get('closed', False)])

    print(f"[OK] 빌드 완료: {output_path}")
    print(f"     파일 크기: {file_size:,} bytes")
    print(f"     접수중: {active_count}건 / 마감: {closed_count}건 / 소스: {len(sources)}개")
    return output_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='공고 대시보드 빌드')

    # 기본 경로: 스크립트 위치 기준
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)  # 01_공고모니터링/

    parser.add_argument('--data-dir', default=os.path.join(base_dir, 'data'),
                        help='데이터 디렉토리 (default: ../data)')
    parser.add_argument('--template', default=os.path.join(base_dir, 'templates', 'dashboard.html'),
                        help='템플릿 HTML (default: ../templates/dashboard.html)')
    parser.add_argument('--output', default=os.path.join(base_dir, '배포', 'index.html'),
                        help='출력 파일 (default: ../배포/index.html)')

    args = parser.parse_args()
    build(args.data_dir, args.template, args.output)
