import os
import json

DATA_DIR = "data"

prompts = [
    {"title": "이미지 생성", "content": "풍경화를 그려줘", "category": "Image", "is_favorite": False, "views": 0},
    {"title": "페르소나", "content": "너는 전문 개발자야", "category": "Persona", "is_favorite": True, "views": 5},
    {"title": "코드 자동화", "content": "파이썬으로 웹 크롤러를 짜줘", "category": "automation", "is_favorite": False, "views": 2}
]

# ==========================================
# 화면 제어 및 공통 유틸리티 함수 (PC통신 감성)
# ==========================================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause_screen():
    input("\n[안내] 아무 키나 누르시면 이전 화면으로 돌아갑니다...")

def get_valid_input(prompt_msg):
    while True:
        val = input(prompt_msg).strip()
        if val: return val
        print("  [오류] 입력값이 없습니다. 다시 입력해 주십시오.")

def get_multiline_input(prompt_msg):
    print(f"{prompt_msg}")
    print("  (입력 완료: 빈 줄에서 ':q' 입력 / 입력 취소: ':c' 입력)")
    print("-" * 65)
    lines = []
    while True:
        line = input("  > ")
        if line.strip() == ":c":
            return None
        if line.strip() == ":q":
            if not lines or all(not l.strip() for l in lines):
                print("  [오류] 내용이 비어있습니다. (취소하시려면 ':c'를 입력하세요)")
                lines = []
                continue
            break
        lines.append(line)
    return "\n".join(lines)


# ==========================================
# [개선] 한글/영문 혼용 시 터미널 정렬 (EUC-KR 방식)
# ==========================================
def get_display_width(text):
    """문자열을 EUC-KR로 인코딩했을 때의 바이트 길이(한글 2, 영문 1)를 반환합니다."""
    try:
        return len(str(text).encode('euc-kr'))
    except UnicodeEncodeError:
        # EUC-KR로 표현 불가능한 특수문자(이모지 등)는 기본 2칸으로 계산
        return len(str(text)) * 2

def pad_string(text, total_width, align='<'):
    """터미널 출력 너비에 맞춰 공백을 채웁니다."""
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
# 데이터 가공 및 리스트 출력 로직 (BBS 스타일)
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
        fav = "★" if p["is_favorite"] else "☆"
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
# 기능: 파일 저장, 불러오기, 내보내기
# ==========================================
def save_prompts():
    print("\n" + "="*50)
    print("  [[ 자료실: 데이터 저장 ]]")
    print("="*50)
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

    while True:
        filename = input("  저장할 파일명 입력 (예: data.json) : ").strip()
        if not filename:
            if input("  [확인] 입력을 취소하시겠습니까? (Y/N): ").strip().upper() == 'Y': return
            continue
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

    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    if not files:
        print("  [알림] 불러올 파일이 없습니다.")
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
        filename = get_valid_input("  내보낼 파일명 입력 (.md 포함 권장 / :c 취소) > ")
        if filename.lower() == ":c": return

        filepath = os.path.join(EXPORT_DIR, filename)
        if os.path.exists(filepath):
            print("  [오류] 이미 존재하는 파일명입니다. 다른 이름을 사용하십시오.")
            continue
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("# 📋 통합 프롬프트 목록\n\n")
                
                # 카테고리별로 그룹핑하여 출력
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
                    
            print(f"\n  [알림] '{filepath}' 카테고리별 분류 생성 완료.")
            break
        except Exception as e:
            print(f"  [시스템 오류] {e}")
            break


# ==========================================
# 기능: 프롬프트 추가 (카테고리 선택 기능 포함) 및 상세
# ==========================================
def add_prompt():
    clear_screen()
    print("=" * 65)
    print(pad_string("[[ 신규 프롬프트 등록 ]]", 65, '^'))
    print("=" * 65)
    
    title = get_valid_input("  [입력] 제목 (:c 취소) > ")
    if title == ":c": return
    
    content = get_multiline_input("\n  [입력] 내용")
    if content is None: return
    
    # 카테고리 선택 또는 직접 입력
    print("\n  [입력] 카테고리 지정")
    categories = list(set(p['category'] for p in prompts))
    
    print("-" * 65)
    for i, cat in enumerate(categories, 1):
        print(f"    {i}. {cat}")
    print(f"    0. 직접 입력하기 (새로운 카테고리)")
    print("-" * 65)
    
    while True:
        cat_choice = get_valid_input("  목록 번호 선택 또는 직접 입력 (:c 취소) > ")
        if cat_choice == ":c": return
        
        # 1. 0번 선택 시: 직접 입력 모드
        if cat_choice == '0':
            category = get_valid_input("  새 카테고리명 입력 > ")
            if category == ":c": return
            break
            
        # 2. 리스트의 번호를 선택한 경우
        if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
            category = categories[int(cat_choice) - 1]
            break
            
        # 3. 숫자가 아닌 문자열을 바로 입력한 경우 (빠른 직접 입력 허용)
        if not cat_choice.isdigit():
            category = cat_choice
            break
            
        print("  [오류] 올바른 번호나 카테고리명을 입력해 주십시오.")
    
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
        print(f" [조회] {prompt_obj['views']}   [즐겨찾기] {'★ 등록됨' if prompt_obj['is_favorite'] else '☆ 미등록'}")
        print("-" * 70)
        print(" [본문]")
        print(f"{prompt_obj['content']}")
        print("=" * 70)
        
        print("\n  [명령어] 1:수정  2:삭제  3:즐겨찾기 변경  P:목록으로")
        choice = get_valid_input("  선택 > ").upper()
        
        if choice == '1':
            print("\n  --- 글 수정 ---")
            new_title = get_valid_input("  새 제목 (유지하려면 :c) > ")
            if new_title != ":c": prompt_obj['title'] = new_title
            
            new_content = get_multiline_input("\n  새 내용 (유지하려면 :c)")
            if new_content is not None: prompt_obj['content'] = new_content
            print("  [알림] 수정되었습니다.")
            
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
            print("  [오류] 잘못된 명령어입니다.")


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
            print("  [오류] 알 수 없는 명령어입니다.")
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
    print(pad_string("★ 프롬프트 관리 시스템 v1.0 ★", 50, '^'))
    print("=" * 50)
    print("  [ 게시판 관리 ]")
    print("    1. 프롬프트 게시판")
    print("    2. 카테고리 분류함")
    print("    3. 즐겨찾기 보관함")
    print("  [ 자료실 ]")
    print("    S. 데이터 저장")
    print("    L. 데이터 불러오기")
    print("    E. 외부로 내보내기 (Markdown)")
    print("-" * 50)
    print("    0. 통신 종료")
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
                print("  [오류] 알 수 없는 명령어입니다.")
                pause_screen()

if __name__ == "__main__":
    main()