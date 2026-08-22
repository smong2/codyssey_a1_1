import os
import json
import sys
import atexit

# ==========================================
# 색상 테마 및 초기화 설정 (macOS 최적화)
# ==========================================
THEME = "\033[1;97;44m"  # 굵고 밝은 흰색 텍스트 + 파란색 배경
RESET = "\033[0m"

# 프로그램 시작 시 터미널 전체에 색상 적용
sys.stdout.write(THEME)

# 프로그램 종료 시 터미널 잔상 방지용 초기화
atexit.register(lambda: sys.stdout.write(RESET))

DATA_DIR = "data"

prompts = [
    {"title": "이미지 생성", "content": "풍경화를 그려줘", "category": "Image", "is_favorite": False, "views": 0},
    {"title": "페르소나", "content": "너는 전문 개발자야", "category": "Persona", "is_favorite": True, "views": 5},
    {"title": "코드 자동화", "content": "파이썬으로 웹 크롤러를 짜줘", "category": "automation", "is_favorite": False, "views": 2}
]

# ==========================================
# 한글 백스페이스 잔상 방지 커스텀 입력 (macOS/Linux)
# ==========================================
def get_display_width(text):
    try:
        return len(str(text).encode('euc-kr'))
    except UnicodeEncodeError:
        return len(str(text)) * 2

def custom_input(prompt_msg=""):
    if prompt_msg:
        sys.stdout.write(prompt_msg)
        sys.stdout.flush()
        
    # 윈도우 환경이거나 터미널 세션이 아닐 경우 기본 input 사용
    if os.name == 'nt' or not sys.stdin.isatty():
        return __builtins__.input(prompt_msg)
        
    import termios
    import tty
    
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    chars = []
    
    try:
        tty.setraw(fd)
        while True:
            byte_data = bytearray()
            while True:
                b = os.read(fd, 1)
                if not b:
                    break
                byte_data.extend(b)
                try:
                    char = byte_data.decode('utf-8')
                    break
                except UnicodeDecodeError:
                    if len(byte_data) >= 4:
                        char = byte_data.decode('utf-8', errors='ignore')
                        break
                    continue
            
            if not char:
                continue
            
            # 엔터 입력 시 종료
            if char in ('\r', '\n'):
                sys.stdout.write('\r\n')
                sys.stdout.flush()
                return "".join(chars)
            
            # 백스페이스 입력 시 한글(2칸) 및 영문(1칸) 크기에 맞춰 깔끔하게 지우기
            elif char in ('\x7f', '\b'):
                if chars:
                    removed = chars.pop()
                    width = 2 if get_display_width(removed) > 1 else 1
                    sys.stdout.write('\b' * width + ' ' * width + '\b' * width)
                    sys.stdout.flush()
            
            # Ctrl+C 처리
            elif char == '\x03':
                raise KeyboardInterrupt
                
            # 일반 문자 입력
            else:
                chars.append(char)
                sys.stdout.write(char)
                sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# 기본 input 함수를 백스페이스 잔상이 해결된 커스텀 입력으로 대체
input = custom_input

# ==========================================
# 화면 제어 및 공통 유틸리티 함수
# ==========================================
def clear_screen():
    # \033[2J : 전체 화면 지우기 (파란 배경 유지)
    # \033[H  : 커서를 좌측 상단(1,1)으로 이동
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.write(THEME)

def pause_screen():
    input("\n[안내] 아무 키나 누르시면 이전 화면으로 돌아갑니다...")

def get_valid_input(prompt_msg):
    while True:
        val = input(prompt_msg).strip()
        if val: return val
        print("  [오류] 입력값이 없습니다. 다시 입력해 주십시오.")

def get_multiline_input(prompt_msg, is_edit_mode=False):
    print(f"{prompt_msg}")
    if is_edit_mode:
        print("  (입력 완료: 빈 줄에서 ':q' / 취소: ':c' / 내용유지: 첫 줄에서 엔터)")
    else:
        print("  (입력 완료: 빈 줄에서 ':q' / 취소: ':c')")
    print("-" * 65)
    
    lines = []
    is_first_line = True
    
    while True:
        line = input("  > ")
        
        if is_first_line and is_edit_mode and line == "":
            return None
            
        is_first_line = False
        
        if line.strip() == ":c":
            return ":c"
            
        if line.strip() == ":q":
            if not lines or all(not l.strip() for l in lines):
                print("  [오류] 내용이 비어있습니다. (취소하시려면 ':c'를 입력하세요)")
                lines = []
                is_first_line = True
                continue
            break
            
        lines.append(line)
        
    return "\n".join(lines)

def pad_string(text, total_width, align='<'):
    text = str(text)
    width = get_display_width(text)
    padding = total_width - width
    
    if padding <= 0:
        return text
    if align == '^':
        left = padding // 2
        right = padding - left
        return ' ' * left + text + ' ' * right
    elif align == '<':
        return text + ' ' * padding
    elif align == '>':
        return ' ' * padding + text


# ==========================================
# 데이터 가공 및 리스트 출력 로직
# ==========================================
def get_filtered_prompts(category=None, search_keyword=None, only_favorites=False, sort_by_views=False):
    filtered = prompts
    if category: 
        filtered = [p for p in filtered if p['category'] == category]
    if search_keyword: 
        filtered = [p for p in filtered if search_keyword.lower() in p['title'].lower() or search_keyword.lower() in p['content'].lower()]
    if only_favorites: 
        filtered = [p for p in filtered if p['is_favorite']]
    if sort_by_views: 
        filtered = sorted(filtered, key=lambda x: x['views'], reverse=True)
    return filtered

def print_prompt_list(target_list, title="프롬프트 목록"):
    clear_screen()
    print("=" * 70)
    print(pad_string(f"[[ {title} ]]", 70, '^'))
    print("=" * 70)
    if not target_list:
        print("\n  [알림] 등록된 프롬프트가 존재하지 않습니다.\n")
        return False
        
    print(f"  {'NO':^4} | {'카테고리':^14} | {'프롬프트 제목':^20} | {'조회':^4} | {'즐겨찾기'}")
    print("-" * 70)
    for i, p in enumerate(target_list, 1):
        fav = "⭐" if p["is_favorite"] else "[ ]"
        cat_str = pad_string(p['category'], 14, '^')
        title_str = pad_string(p['title'], 20, '<')
        views_str = pad_string(str(p['views']), 4, '^')
        print(f"  {i:>4} | {cat_str} | {title_str} | {views_str} |    {fav}")
    print("=" * 70)
    return True

def show_list_and_detail(fetch_func, title):
    while True:
        data = fetch_func()
        if not print_prompt_list(data, title):
            pause_screen()
            return
            
        print("\n  [명령] 상세히 볼 글 번호를 입력하십시오.")
        idx_str = get_valid_input("  (P: 이전 화면으로) 선택 > ").upper()
        
        if idx_str == 'P':
            return
            
        try:
            idx = int(idx_str) - 1
            if 0 <= idx < len(data):
                detail_prompt(data[idx])
            else:
                print("  [오류] 존재하지 않는 번호입니다.")
                pause_screen()
        except ValueError:
            print("  [오류] 숫자를 입력해 주십시오.")
            pause_screen()


# ==========================================
# 카테고리 선택 및 입력 공통 함수
# ==========================================
def select_category(is_edit_mode=False):
    print("\n  [카테고리 지정]")
    categories = list(set(p['category'] for p in prompts))
    
    print("-" * 65)
    for i, cat in enumerate(categories, 1):
        print(f"    {i}. {cat}")
    print(f"    0. 직접 입력하기 (새로운 카테고리)")
    print("-" * 65)
    
    prompt_str = "  목록 번호 선택 또는 직접 입력 (취소: :c, 내용유지: 엔터) > " if is_edit_mode else "  목록 번호 선택 또는 직접 입력 (취소: :c) > "
    
    while True:
        cat_choice = input(prompt_str).strip()
        
        if is_edit_mode and not cat_choice:
            return None 
            
        if not cat_choice:
            print("  [오류] 입력값이 없습니다. 다시 입력해 주십시오.")
            continue
            
        if cat_choice == ":c": 
            return ":c"
        
        if cat_choice == '0':
            while True:
                category = input("  새 카테고리명 입력 (취소: :c) > ").strip()
                if not category:
                    print("  [오류] 입력값이 없습니다.")
                    continue
                break
            if category == ":c": 
                return ":c"
            return category
            
        if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
            return categories[int(cat_choice) - 1]
            
        if not cat_choice.isdigit():
            return cat_choice
            
        print("  [오류] 올바른 번호나 카테고리명을 입력해 주십시오.")


# ==========================================
# 기능: 파일 저장, 불러오기, 내보내기
# ==========================================
def save_prompts():
    print("\n" + "="*50)
    print("  [[ 자료실: 데이터 저장 ]]")
    print("="*50)
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

    while True:
        filename = input("  저장할 파일명 입력 (예: data) (취소: :c) > ").strip()
        if filename == ":c": return
        if not filename:
            print("  [오류] 입력값이 없습니다.")
            continue
            
        # .json 확장자 자동 추가
        if not filename.lower().endswith(".json"):
            filename += ".json"
        break

    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        if get_valid_input("  [경고] 동일한 파일이 존재합니다. 덮어쓰시겠습니까? (Y/N): ").upper() != 'Y': return
            
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(prompts, f, ensure_ascii=False, indent=4)
        print(f"\n  [알림] '{filepath}' 에 성공적으로 기록되었습니다.")
    except Exception as e:
        print(f"  [시스템 오류] 저장 실패: {e}")

def load_prompts():
    print("\n" + "="*50)
    print("  [[ 자료실: 데이터 불러오기 ]]")
    print("="*50)
    if not os.path.exists(DATA_DIR):
        print("  [알림] 데이터 폴더가 존재하지 않습니다.")
        return

    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    if not files:
        print("  [알림] 불러올 JSON 파일이 없습니다.")
        return

    for i, file in enumerate(files, 1): 
        print(f"    {i}. {file}")
    print("-" * 50)
    choice = get_valid_input("  불러올 파일 번호 선택 (P: 취소) > ").upper()
    if choice == 'P': return

    try:
        choice_idx = int(choice) - 1
        if choice_idx < 0 or choice_idx >= len(files): raise ValueError()
        filepath = os.path.join(DATA_DIR, files[choice_idx])
        with open(filepath, 'r', encoding='utf-8') as f:
            global prompts
            prompts = json.load(f)
        print(f"\n  [알림] '{files[choice_idx]}' 파일이 로드되었습니다.")
    except ValueError: print("  [오류] 잘못된 선택입니다.")
    except Exception as e: print(f"  [시스템 오류] {e}")

def export_to_markdown():
    print("\n" + "="*50)
    print("  [[ 자료실: 외부 내보내기 (Markdown) ]]")
    print("="*50)
    if not prompts:
        print("  [알림] 내보낼 데이터가 없습니다.")
        return

    EXPORT_DIR = "export"
    if not os.path.exists(EXPORT_DIR): os.makedirs(EXPORT_DIR)

    while True:
        filename = input("  내보낼 파일명 입력 (취소: :c) > ").strip()
        if not filename:
            print("  [오류] 입력값이 없습니다.")
            continue
        if filename.lower() == ":c": return

        if not filename.lower().endswith(".md"):
            filename += ".md"

        filepath = os.path.join(EXPORT_DIR, filename)
        if os.path.exists(filepath):
            print("  [오류] 이미 존재하는 파일명입니다. 다른 이름을 사용하십시오.")
            continue
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("# 📋 통합 프롬프트 목록\n\n")
                categories = sorted(list(set(p['category'] for p in prompts)))
                
                for cat in categories:
                    f.write(f"## 📂 카테고리: {cat}\n\n")
                    cat_prompts = [p for p in prompts if p['category'] == cat]
                    
                    for p in cat_prompts:
                        fav = "⭐" if p["is_favorite"] else "☆"
                        f.write(f"### {p['title']} {fav}\n")
                        f.write(f"- **조회수**: {p['views']}\n\n")
                        f.write(f"**[프롬프트 내용]**\n```text\n{p['content']}\n```\n\n")
                    f.write("---\n\n")
                    
            print(f"\n  [알림] '{filepath}' 로 생성 완료되었습니다.")
            break
        except Exception as e:
            print(f"  [시스템 오류] {e}")
            break


# ==========================================
# 기능: 프롬프트 추가 및 상세/수정
# ==========================================
def add_prompt():
    clear_screen()
    print("=" * 65)
    print(pad_string("[[ 신규 프롬프트 등록 ]]", 65, '^'))
    print("=" * 65)
    
    title = input("  [입력] 제목 (취소: :c) > ").strip()
    if title == ":c" or not title: return
    
    content = get_multiline_input("\n  [입력] 내용")
    if content == ":c" or content is None: return
    
    category = select_category(is_edit_mode=False)
    if category == ":c" or category is None: return
    
    prompts.append({"title": title, "content": content, "category": category, "is_favorite": False, "views": 0})
    print("\n  [알림] 프롬프트 등록이 완료되었습니다.")
    pause_screen()

def detail_prompt(prompt_obj):
    prompt_obj['views'] += 1
    
    while True:
        clear_screen()
        print("=" * 70)
        print(f" [제목] {prompt_obj['title']}")
        print("-" * 70)
        print(f" [분류] {prompt_obj['category']}")
        print(f" [조회] {prompt_obj['views']}   [즐겨찾기] {'⭐ 등록됨' if prompt_obj['is_favorite'] else '[ ] 미등록'}")
        print("-" * 70)
        print(" [본문]")
        print(f"{prompt_obj['content']}")
        print("=" * 70)
        
        print("\n  [명령어] 1:수정  2:삭제  3:즐겨찾기 변경  P:목록으로")
        choice = get_valid_input("  선택 > ").upper()
        
        if choice == '1':
            print("\n  --- 글 수정 ---")
            
            new_title = input(f"  새 제목 [{prompt_obj['title']}] (내용유지: 엔터, 취소: :c) > ").strip()
            if new_title == ":c":
                print("  [알림] 수정이 취소되었습니다.")
                pause_screen()
                continue
                
            new_content = get_multiline_input("\n  새 내용", is_edit_mode=True)
            if new_content == ":c":
                print("  [알림] 수정이 취소되었습니다.")
                pause_screen()
                continue
                
            print(f"\n  현재 카테고리: {prompt_obj['category']}")
            new_category = select_category(is_edit_mode=True)
            if new_category == ":c":
                print("  [알림] 수정이 취소되었습니다.")
                pause_screen()
                continue
            
            if new_title: prompt_obj['title'] = new_title
            if new_content: prompt_obj['content'] = new_content
            if new_category: prompt_obj['category'] = new_category
            
            print("  [알림] 수정되었습니다.")
            pause_screen()
            
        elif choice == '2':
            if get_valid_input("  [경고] 정말 삭제하시겠습니까? (Y/N) > ").upper() == 'Y':
                prompts.remove(prompt_obj)
                print("  [알림] 삭제되었습니다.")
                pause_screen()
                return 
                
        elif choice == '3':
            prompt_obj['is_favorite'] = not prompt_obj['is_favorite']
            
        elif choice == 'P':
            return 
        else:
            print("  [오류] 올바른 번호를 입력해주세요")
            pause_screen()


# ==========================================
# 서브 메뉴 핸들러
# ==========================================
def run_submenu(title, options, actions):
    while True:
        clear_screen()
        print("=" * 50)
        print(pad_string(f"[[ {title} ]]", 50, '^'))
        print("=" * 50)
        for key, desc in options.items(): 
            print(f"    {key}. {desc}")
        print("-" * 50)
        choice = get_valid_input("  명령어 선택 (P: 메인으로) > ").upper()
        
        if choice == 'P': return
        if choice in actions:
            actions[choice]()
        else:
            print("  [오류] 올바른 번호를 입력해주세요")
            pause_screen()

def manage_prompt_menu():
    def handle_search():
        keyword = get_valid_input("\n  [검색] 검색어를 입력하십시오 : ")
        show_list_and_detail(lambda: get_filtered_prompts(search_keyword=keyword), f"검색 결과: {keyword}")

    options = {
        "1": "새 프롬프트 등록", 
        "2": "전체 프롬프트 목록", 
        "3": "인기순(조회수) 목록",
        "4": "프롬프트 검색"
    }
    actions = {
        "1": add_prompt, 
        "2": lambda: show_list_and_detail(lambda: get_filtered_prompts(), "전체 프롬프트"), 
        "3": lambda: show_list_and_detail(lambda: get_filtered_prompts(sort_by_views=True), "인기 프롬프트"),
        "4": handle_search
    }
    run_submenu("프롬프트 게시판", options, actions)

def manage_category_menu():
    categories = list(set(p['category'] for p in prompts))
    options = {str(i+1): f"[{cat}] 카테고리 보기" for i, cat in enumerate(categories)}
    actions = {str(i+1): lambda c=cat: show_list_and_detail(lambda: get_filtered_prompts(category=c), f"카테고리: {c}") 
               for i, cat in enumerate(categories)}
    run_submenu("카테고리 분류함", options, actions)

def manage_favorite_menu():
    options = {"1": "내 즐겨찾기 목록 확인"}
    actions = {"1": lambda: show_list_and_detail(lambda: get_filtered_prompts(only_favorites=True), "내 즐겨찾기")}
    run_submenu("즐겨찾기 보관함", options, actions)


# ==========================================
# 메인 메뉴
# ==========================================
def show_main_menu():
    print("=" * 50)
    print(pad_string("⭐ 프롬프트 관리 시스템 v1.1 ⭐", 50, '^'))
    print("=" * 50)
    print("  [ 게시판 관리 ]")
    print("    1. 프롬프트 게시판")
    print("    2. 카테고리 분류함")
    print("    3. 즐겨찾기 보관함")
    print("  [ 자료실 ]")
    print("    S. 데이터 저장 (JSON)")
    print("    L. 데이터 불러오기 (JSON)")
    print("    E. 외부로 내보내기 (Markdown)")
    print("-" * 50)
    print("    0. 종료")
    print("=" * 50)

def main():
    while True:
        clear_screen()
        show_main_menu()
        choice = get_valid_input("  명령어 선택 > ").upper()
        
        match choice:
            case "1": manage_prompt_menu()
            case "2": manage_category_menu()
            case "3": manage_favorite_menu()
            case "S": 
                save_prompts()
                pause_screen()
            case "L": 
                load_prompts()
                pause_screen()
            case "E": 
                export_to_markdown()
                pause_screen()
            case "0": 
                clear_screen()
                print("\n  [시스템] 통신을 종료합니다. 안녕히 가십시오.\n")
                break
            case _: 
                print("  [오류] 올바른 번호를 입력해주세요.")
                pause_screen()

if __name__ == "__main__":
    main()