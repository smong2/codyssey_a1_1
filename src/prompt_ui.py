import os
import json

DATA_DIR = "data"

prompts = [
    {"title": "이미지 생성", "content": "풍경화를 그려줘", "category": "Image", "is_favorite": False, "views": 0},
    {"title": "페르소나", "content": "너는 전문 개발자야", "category": "Persona", "is_favorite": True, "views": 5},
    {"title": "코드 자동화", "content": "파이썬으로 웹 크롤러를 짜줘", "category": "automation", "is_favorite": False, "views": 2}
]

# ==========================================
# 화면 제어 및 공통 유틸리티 함수
# ==========================================
def clear_screen():
    """운영체제에 맞게 터미널 화면을 지웁니다."""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause_screen():
    """사용자가 결과를 확인할 수 있도록 엔터 키 입력을 대기합니다."""
    input("\n엔터 키를 누르면 계속합니다...")

def get_valid_input(prompt_msg):
    """사용자가 빈 값이나 공백만 입력하는 것을 방지하고 좌우 공백을 제거하여 반환합니다."""
    while True:
        val = input(prompt_msg).strip()
        if val: return val
        print("입력값이 없습니다. 공백 외의 값을 입력해주세요.")

def get_multiline_input(prompt_msg):
    """여러 줄의 입력을 받고, ':q'로 완료, ':c'로 취소를 처리합니다."""
    print(f"{prompt_msg} (여러 줄 입력 가능. 완료: ':q', 취소: ':c' 입력 후 엔터)")
    lines = []
    while True:
        line = input()
        if line.strip() == ":c":
            return None
        if line.strip() == ":q":
            if not lines or all(not l.strip() for l in lines):
                print("입력값이 없습니다. 최소 한 줄 이상의 내용을 입력해주세요. (취소하려면 ':c' 입력)")
                lines = []
                continue
            break
        lines.append(line)
    return "\n".join(lines)


# ==========================================
# [통합] 데이터 가공 및 화면 출력 로직
# ==========================================
def get_filtered_prompts(category=None, search_keyword=None, only_favorites=False, sort_by_views=False):
    """조건에 맞는 데이터를 추려 정렬한 후 리스트로 반환합니다."""
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
    """넘겨받은 리스트를 일관된 형식으로 출력합니다."""
    clear_screen()
    print(f"\n--- {title} ---")
    if not target_list:
        print("조건에 맞는 프롬프트가 없습니다.")
        return False
    print("==========================================================")
    for i, p in enumerate(target_list, 1):
        fav = "⭐" if p["is_favorite"] else "☆"
        print(f"{i:>2}. [{p['category']:^8}] {p['title']} {fav} (조회수: {p['views']})")
    print("==========================================================")
    return True

def show_list_and_detail(data, title):
    """리스트를 출력하고, 번호를 선택해 상세 조회를 할 수 있도록 연결합니다."""
    if print_prompt_list(data, title):
        idx_str = get_valid_input("상세조회할 번호 입력 (P: 돌아가기): ").upper()
        if idx_str != 'P':
            try:
                idx = int(idx_str) - 1
                if 0 <= idx < len(data):
                    detail_prompt(data[idx])
                else:
                    print("잘못된 번호입니다.")
            except ValueError:
                print("숫자를 입력해주세요.")


# ==========================================
# 기능: 파일 저장, 불러오기, 내보내기
# ==========================================
def save_prompts():
    print("\n--- 프롬프트 저장 ---")
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"'{DATA_DIR}' 디렉토리를 생성했습니다.")

    while True:
        filename = input("저장할 파일명을 입력하세요 (예: data.json): ").strip()
        if not filename:
            cancel = input("파일명이 입력되지 않았습니다. 저장을 취소하시겠습니까? (y/n): ").strip().upper()
            if cancel == 'Y':
                print("저장을 취소합니다.")
                return
            else:
                print("다시 파일명을 입력해주세요.\n")
                continue
        break

    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        overwrite = get_valid_input("파일이 이미 존재합니다. 덮어쓰시겠습니까? (y/n): ").upper()
        if overwrite != 'Y':
            print("저장을 취소합니다.")
            return
            
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(prompts, f, ensure_ascii=False, indent=4)
        print(f"성공적으로 {filepath}에 저장되었습니다.")
    except Exception as e:
        print(f"저장 중 오류가 발생했습니다: {e}")

def load_prompts():
    print("\n--- 프롬프트 불러오기 ---")
    if not os.path.exists(DATA_DIR):
        print("데이터 디렉토리가 존재하지 않습니다.")
        return

    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    if not files:
        print("저장된 json 파일이 없습니다.")
        return

    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    print("P. 취소하고 돌아가기")
        
    choice = get_valid_input("\n번호를 선택하세요: ").upper()
    if choice == 'P':
        print("불러오기를 취소합니다.")
        return

    try:
        choice_idx = int(choice) - 1
        if choice_idx < 0 or choice_idx >= len(files):
            raise ValueError()
        
        filename = files[choice_idx]
        filepath = os.path.join(DATA_DIR, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            global prompts
            prompts = json.load(f)
        print(f"\n{filename}을(를) 성공적으로 불러왔습니다.")
        
    except ValueError:
        print("잘못된 선택입니다.")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

def export_to_markdown():
    print("\n--- 마크다운으로 내보내기 ---")
    if not prompts:
        print("내보낼 데이터가 없습니다.")
        return

    EXPORT_DIR = "export"
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    while True:
        filename = get_valid_input("내보낼 파일명을 입력하세요 (확장자 .md 포함 권장): ")
        if filename.lower() == ":c":
            print("내보내기를 취소합니다.")
            return

        filepath = os.path.join(EXPORT_DIR, filename)

        if os.path.exists(filepath):
            print(f"오류: '{filename}' 파일이 이미 존재합니다. 다른 이름을 입력해주세요.")
            continue
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("# 프롬프트 목록\n\n")
                for p in prompts:
                    fav = "⭐" if p["is_favorite"] else "☆"
                    f.write(f"## {p['title']} {fav}\n")
                    f.write(f"- **카테고리**: {p['category']}\n")
                    f.write(f"- **조회수**: {p['views']}\n\n")
                    f.write(f"### 내용\n{p['content']}\n\n")
                    f.write("---\n")
            print(f"성공적으로 {filepath} 파일로 내보냈습니다.")
            break
        except Exception as e:
            print(f"내보내기 중 오류가 발생했습니다: {e}")
            break


# ==========================================
# 기능: 프롬프트 추가 및 상세 조회
# ==========================================
def add_prompt():
    print("\n--- 프롬프트 추가하기 ---")
    title = get_valid_input("제목: ")
    if title == ":c": return
    content = get_multiline_input("\n내용:")
    if content is None: return
    category = get_valid_input("\n카테고리: ")
    if category == ":c": return
    
    prompts.append({"title": title, "content": content, "category": category, "is_favorite": False, "views": 0})
    print("\n프롬프트가 추가되었습니다.")

def detail_prompt(prompt_obj):
    prompt_obj['views'] += 1
    print(f"\n--- {prompt_obj['title']} ---")
    print(f"카테고리: {prompt_obj['category']}\n내용:\n{prompt_obj['content']}")
    print("-" * 20)
    choice = get_valid_input("1. 수정 | 2. 삭제 | 3. 즐겨찾기 토글 | P. 돌아가기: ").upper()
    if choice == '1':
        prompt_obj['title'] = get_valid_input("새 제목: ")
        prompt_obj['content'] = get_multiline_input("새 내용:")
    elif choice == '2':
        prompts.remove(prompt_obj)
        print("삭제되었습니다.")
    elif choice == '3':
        prompt_obj['is_favorite'] = not prompt_obj['is_favorite']
        print(f"즐겨찾기 상태가 변경되었습니다. (현재: {'⭐ ON' if prompt_obj['is_favorite'] else '☆ OFF'})")
    return


# ==========================================
# 서브 메뉴 핸들러 및 메뉴 구성
# ==========================================
def run_submenu(title, options, actions):
    while True:
        clear_screen()
        print(f"\n --- {title} ---")
        for key, desc in options.items(): print(f"{key}. {desc}")
        print("P. 이전 메뉴로 돌아가기")
        choice = get_valid_input("번호를 입력하세요: ").upper()
        if choice == 'P': return
        if choice in actions:
            actions[choice]()
            pause_screen()
        else:
            print("잘못된 입력입니다. 정확한 번호를 선택해주세요.")
            pause_screen()

def manage_prompt_menu():
    options = {
        "1": "추가하기", 
        "2": "리스트 보기", 
        "3": "조회수 순위 보기",
        "4": "프롬프트 검색"
    }
    actions = {
        "1": add_prompt, 
        "2": lambda: show_list_and_detail(get_filtered_prompts(), "전체 프롬프트 리스트"), 
        "3": lambda: show_list_and_detail(get_filtered_prompts(sort_by_views=True), "인기순 프롬프트 리스트"),
        "4": lambda: show_list_and_detail(get_filtered_prompts(search_keyword=get_valid_input("검색어: ")), "검색 결과")
    }
    run_submenu("1. 프롬프트 관리하기", options, actions)

def manage_category_menu():
    # 현재 데이터에 존재하는 카테고리만 중복 없이 추출하여 동적 메뉴 생성
    categories = list(set(p['category'] for p in prompts))
    options = {str(i+1): cat for i, cat in enumerate(categories)}
    actions = {str(i+1): lambda c=cat: show_list_and_detail(get_filtered_prompts(category=c), f"카테고리: {c}") 
               for i, cat in enumerate(categories)}
    run_submenu("2. 카테고리별 보기", options, actions)

def manage_favorite_menu():
    options = {"1": "즐겨찾기 목록 보기"}
    actions = {"1": lambda: show_list_and_detail(get_filtered_prompts(only_favorites=True), "즐겨찾기 목록")}
    run_submenu("3. 즐겨찾기 관리", options, actions)


# ==========================================
# 메인 메뉴
# ==========================================
def show_main_menu():
    print("\n--- 프롬프트 관리 프로그램 ---")
    print("==============")
    print("1. 프롬프트 관리하기")
    print("2. 카테고리별 보기")
    print("3. 즐겨찾기 관리")
    print("==============")
    print("S. 저장하기")
    print("L. 불러오기")
    print("E. markdown 으로 내보내기")
    print("==============")
    print("0. 종료")

def main():
    while True:
        clear_screen()
        show_main_menu()
        choice = get_valid_input("번호를 입력하세요: ").upper()
        
        match choice:
            case "1": manage_prompt_menu()
            case "2": manage_category_menu()
            case "3": show_list_and_detail(get_filtered_prompts(only_favorites=True), "즐겨찾기 목록")
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
                print("프로그램을 종료합니다.")
                break
            case _: 
                print("잘못된 입력입니다. 다시 선택해주세요.")
                pause_screen()

if __name__ == "__main__":
    main()