"""Core functionality for the Sorizava-based Korean stenography system."""

import sys
import os

# --- [추가] six 모듈 경로 및 에러 방지 ---
# 딕셔너리 파일과 같은 위치에 있는 six.py를 인식하도록 경로를 추가합니다.
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    import six
except ImportError:
    pass
# ---------------------------------------

from typing import Tuple, List
from plover.system import Stroke
import hgtk

LONGEST_KEY = 1
OPERATOR_ATTACH = "{^}"

# (INITIALS, VOWELS, FINALS 정의는 사용자께서 주신 기존 내용과 동일하게 유지)
INITIALS = {
    Stroke("ㄱ"): "ㄱ", Stroke("ㄱㅎ"): "ㄲ", Stroke("ㄴ"): "ㄴ", Stroke("ㄷ"): "ㄷ", 
    Stroke("ㄷㄹ"): "ㄸ", Stroke("ㄹ"): "ㄹ", Stroke("ㅁ"): "ㅁ", Stroke("ㅂ"): "ㅂ", 
    Stroke("ㅂㄱ"): "ㅃ", Stroke("ㅅ"): "ㅅ", Stroke("ㅅㅁ"): "ㅆ", Stroke(""): "ㅇ", 
    Stroke("ㅈ"): "ㅈ", Stroke("ㅈㄴ"): "ㅉ", Stroke("ㅊ"): "ㅊ", Stroke("ㅋ"): "ㅋ", 
    Stroke("ㅌ"): "ㅌ", Stroke("ㅍ"): "ㅍ", Stroke("ㅎ"): "ㅎ",
}

VOWELS = {
    Stroke("ㅏ"): "ㅏ", Stroke("ㅏㅣ"): "ㅐ", Stroke("ㅏㅡ"): "ㅑ", Stroke("ㅏㅓ"): "ㅒ", 
    Stroke("ㅓ"): "ㅓ", Stroke("ㅓㅣ"): "ㅔ", Stroke("ㅡㅓ"): "ㅕ", Stroke("ㅏㅓㅣ"): "ㅖ", 
    Stroke("ㅗ"): "ㅗ", Stroke("ㅗㅏ"): "ㅘ", Stroke("ㅗㅏㅣ"): "ㅙ", Stroke("ㅗㅣ"): "ㅚ", 
    Stroke("ㅗㅡ"): "ㅛ", Stroke("ㅜ"): "ㅜ", Stroke("ㅜㅓ"): "ㅝ", Stroke("ㅜㅓㅣ"): "ㅞ", 
    Stroke("ㅜㅣ"): "ㅟ", Stroke("ㅜㅡ"): "ㅠ", Stroke("ㅡ"): "ㅡ", Stroke("ㅢ"): "ㅢ", 
    Stroke("ㅣ"): "ㅣ",
}

FINALS = {
    Stroke(""): "", Stroke("-ㄱ"): "ㄱ", Stroke("-ㄲ"): "ㄲ", Stroke("-ㄱㅅ"): "ㄳ", 
    Stroke("-ㄴ"): "ㄴ", Stroke("-ㄴㅈ"): "ㄵ", Stroke("-ㅎㄴ"): "ㄶ", Stroke("-ㄷ"): "ㄷ", 
    Stroke("-ㄹ"): "ㄹ", Stroke("-ㄱㄹ"): "ㄺ", Stroke("-ㄹㅁ"): "ㄻ", Stroke("-ㄹㅂ"): "ㄼ", 
    Stroke("-ㄹㅅ"): "ㄽ", Stroke("-ㅌㄹ"): "ㄾ", Stroke("-ㅍㄹ"): "ㄿ", Stroke("-ㅎㄹ"): "ㅀ", 
    Stroke("-ㅁ"): "ㅁ", Stroke("-ㅂ"): "ㅂ", Stroke("-ㅅㅂ"): "ㅄ", Stroke("-ㅅ"): "ㅅ", 
    Stroke("-ㅆ"): "ㅆ", Stroke("-ㅇ"): "ㅇ", Stroke("-ㅈ"): "ㅈ", Stroke("-ㅊ"): "ㅊ", 
    Stroke("-ㅋ"): "ㅋ", Stroke("-ㅌ"): "ㅌ", Stroke("-ㅍ"): "ㅍ", Stroke("-ㅎ"): "ㅎ",
}

INITIAL_KEYS = Stroke("ㅊㅌㅋㅂㅍㅅㄷㅈㄱㅁㄹㄴㅎ")
VOWEL_KEYS = Stroke("ㅢㅗㅏㅜㅡㅓㅣ")
FINAL_KEYS = Stroke("-ㅋㄲㅎㅌㅊㅍㄱㄴㄹㅅㅂㅆㅇㅁㄷㅈ")

def lookup(strokes: Tuple[str]) -> str:
    if len(strokes) != LONGEST_KEY:
        raise KeyError

    stroke_str = strokes[0]

    # --- [추가] 숫자 출력 로직 ---
    # definition.py의 KEYS에서 '#' 대신 'S'나 'N'을 사용하기로 한 이름과 일치해야 합니다.
    num_map = {
        "S1": "1", "S2": "2", "S3": "3", "S4": "4", "S5": "5",
        "S6": "6", "S7": "7", "S8": "8", "S9": "9", "S0": "0"
    }

    if stroke_str in num_map:
        return num_map[stroke_str]
    # ----------------------------

    stroke = Stroke(stroke_str)
    initial_keys, vowel_keys, final_keys = (
        stroke & INITIAL_KEYS,
        stroke & VOWEL_KEYS,
        stroke & FINAL_KEYS,
    )
    
    initial = INITIALS.get(initial_keys, "")
    vowel = VOWELS.get(vowel_keys)
    final = FINALS.get(final_keys, "")

    if not vowel:
        raise KeyError

    try:
        hangul = hgtk.letter.compose(initial, vowel, final)
        return f"{OPERATOR_ATTACH}{hangul}{OPERATOR_ATTACH}"
    except:
        raise KeyError

def reverse_lookup(text: str) -> List[Tuple[str]]:
    return []
