#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
쮸래기 밸런스게임 기계 린터 (토큰 0 · 무한 반복)
- 사용: python tools/balance_linter.py [index.html 경로]   (기본 index.html)
- 코드로 판정 가능한 기준만 검사한다:
    간결(길이) / 조건 과다 / A·B 대칭 / 각주 개수 / 모호어 / 중복
- ★밸런스 감각(비등·쏠림·프레임·정답없음)은 기계가 못 한다 → 사람 검수 + 투표 데이터 몫.
  (제작원칙 정본: Brain-Vault/쮸래기-뇌/2026-08-11_밸런스게임_제작원칙.md 의 심판 루브릭 v2 참고)
"""
import re, sys, io
from difflib import SequenceMatcher

# 윈도우 콘솔(cp949) 등에서 한글/이모지 출력 깨짐 방지
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# ================= 임계값 (여기 숫자만 조절) =================
MAX_LEN       = 42     # 선택지 최대 글자수(초과 = 길다)
MAX_ASTERISK  = 1      # 각주 '*' 최대 개수
SYM_DIFF      = 22     # A·B 글자수 차이 허용(초과 = 비대칭)
DUP_RATIO     = 0.72   # 두 문항 유사도 임계(이상 = 중복 의심)
CLAUSE_MAX    = 3      # 조건 접속(지만/는데/…)+쉼표 개수 이상이면 '복잡'
CLAUSE_MARKERS= ['지만', '는데', '면서', '하고', '인데', '이며']
VAGUE_WORDS   = ['등등', '뭐랄까', '그런 거', '약간', '같은 거']
# ===========================================================

def load_questions(path):
    html = io.open(path, 'r', encoding='utf-8').read()
    html = re.sub(r'/\*.*?\*/', '', html, flags=re.DOTALL)  # 주석(편집가이드 예시 등) 제거
    out = []
    # 테마 블록: {name:"...", ... q:[ ... ]},  → 통째로 잡고 그 안에서 [A,B] 추출
    for m in re.finditer(r'\{name:"([^"]+)".*?\]\},', html, re.DOTALL):
        theme = m.group(1); block = m.group(0)
        pairs = re.findall(r'\["((?:[^"\\]|\\.)*)","((?:[^"\\]|\\.)*)"\]', block)
        for i, (a, b) in enumerate(pairs):
            out.append((theme, i + 1, a, b))
    return out

def clause_count(s):
    return sum(s.count(k) for k in CLAUSE_MARKERS) + s.count(',') + s.count('，')

def lint(qs):
    issues = []
    for (theme, idx, a, b) in qs:
        tag = f"[{theme} #{idx}]"
        for side, s in (('A', a), ('B', b)):
            if len(s) > MAX_LEN:
                issues.append(f"{tag} {side} 길다({len(s)}자): {s}")
            if s.count('*') > MAX_ASTERISK:
                issues.append(f"{tag} {side} 각주 과다")
            if clause_count(s) >= CLAUSE_MAX:
                issues.append(f"{tag} {side} 조건 과다(복잡): {s}")
            for v in VAGUE_WORDS:
                if v in s:
                    issues.append(f"{tag} {side} 모호어 '{v}'")
        if abs(len(a) - len(b)) > SYM_DIFF:
            issues.append(f"{tag} A·B 비대칭 길이({len(a)} vs {len(b)})")
    # 중복(전체 쌍 비교)
    for i in range(len(qs)):
        for j in range(i + 1, len(qs)):
            t1 = qs[i][2] + " / " + qs[i][3]
            t2 = qs[j][2] + " / " + qs[j][3]
            r = SequenceMatcher(None, t1, t2).ratio()
            if r >= DUP_RATIO:
                issues.append(f"[중복 {r:.2f}] {qs[i][0]}#{qs[i][1]} ≈ {qs[j][0]}#{qs[j][1]}")
    return issues

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
    qs = load_questions(path)
    issues = lint(qs)
    print(f"■ 문항 {len(qs)}개 검사")
    if not issues:
        print("✅ 기계 검사 통과(간결·대칭·각주·중복·모호어).")
    else:
        print(f"⚠️ 지적 {len(issues)}건:")
        for x in issues:
            print("   -", x)
    print(f"\n[임계값] 길이≤{MAX_LEN} · 비대칭≤{SYM_DIFF} · 중복<{DUP_RATIO} · 조건<{CLAUSE_MAX}")
    print("※ 밸런스 감각(비등/쏠림/프레임/정답없음)은 사람 검수 + 투표 데이터 몫.")

if __name__ == '__main__':
    main()
