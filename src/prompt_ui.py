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
        if val:
            return val
        print("입력값이 없습니다. 공백 외의 값을 입력해주세요.")

def run_submenu(title, options, actions):
    """서브 메뉴의 반복되는 출력, 입력 처리 로직을 담당합니다."""
    while True:
        clear_screen() # 서브 메뉴를 그리기 전에 화면을 지웁니다
        print(f"\n --- {title} ---")
        print("==============")
        for key, desc in options.items():
            print(f"{key}. {desc}")
        print("==============")
        print("P. 이전 메뉴로 돌아가기")
        
        choice = get_valid_input("번호를 입력하세요: ").upper()
        
        if choice == 'P':
            return # 메인 메뉴로 돌아감
            
        if choice in actions:
            actions[choice]() # 연결된 함수 실행
            pause_screen()    # 실행 결과를 볼 수 있게 대기
        else:
            print("잘못된 입력입니다. 정확한 번호를 선택해주세요.")
            pause_screen()

def get_multiline_input(prompt_msg):
    """엔터 사용 가능합니다. 마지막 줄에  :q 를 누르세요"""
    print(f"{prompt_msg} (엔터 사용 가능합니다. 마지막 줄에 ':q'를 입력하고 엔터를 누르세요)")
    
    lines = []
    while True:
        line = input()

        if line.strip() == ":c":
            return None # 입력을 취소했다는 신호로 None을 반환 

        # 종료 조건 확인
        if line.strip() == ":q":
            if not lines or all(not l.strip() for l in lines):
                print("입력값이 없습니다. 최소 한 줄 이상의 내용을 입력해주세요.")
                lines = [] # 저장된 빈 줄 초기화
                continue
            break
            
        lines.append(line)
        
    return "\n".join(lines)

# ==========================================
# 기능: 파일 저장 및 불러오기
# ==========================================
def save_prompts():
    print("\n--- 프롬프트 저장 ---")
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"'{DATA_DIR}' 디렉토리를 생성했습니다.")

    # 파일명 입력을 위한 전용 루프
    while True:
        filename = input("저장할 파일명을 입력하세요 (예: data.json): ").strip()
        
        # 엔터나 공백만 입력했을 경우
        if not filename:
            cancel = input("파일명이 입력되지 않았습니다. 저장을 취소하시겠습니까? (y/n): ").strip().upper()
            if cancel == 'Y':
                print("저장을 취소합니다.")
                return # 함수를 종료하여 상위 메뉴로 돌아감
            else:
                print("다시 파일명을 입력해주세요.\n")
                continue # 루프의 처음(파일명 입력)으로 돌아감
                
        # 정상적으로 파일명이 입력되었을 경우 루프 탈출
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

# ============================================
# 마크다운 형식으로 파일 내보내기
# ============================================
def export_to_markdown():
    print("\n--- 마크다운으로 내보내기 ---")
    if not prompts:
        print("내보낼 데이터가 없습니다.")
        return

    # 1. 디렉토리 준비
    EXPORT_DIR = "export"
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    # 2. 파일명 입력 루프
    while True:
        filename = get_valid_input("내보낼 파일명을 입력하세요 (확장자 .md 포함 권장): ")
        
        # 파일명 입력 취소 처리 (get_valid_input은 빈값을 허용 안하므로 
        # 취소하려면 별도 로직이 필요하거나 위에서 만든 :c 로직 활용)
        if filename.lower() == ":c":
            print("내보내기를 취소합니다.")
            return

        filepath = os.path.join(EXPORT_DIR, filename)

        # 3. 중복 확인
        if os.path.exists(filepath):
            print(f"오류: '{filename}' 파일이 이미 존재합니다. 다른 이름을 입력해주세요.")
            continue # 다시 파일명 입력 루프로
        
        # 4. 파일 생성 (Markdown 형식으로 작성)
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
# 기능: 프롬프트 추가 및 목록 보기
# ==========================================
def add_prompt():
    print("\n--- 프롬프트 추가하기 ---")
    title = get_valid_input("제목: ")
    if title == ":c":
        print("프롬프트 추가를 취소합니다")
        return

    content = get_multiline_input("\n내용:")
    if content is None:
        print("프롬프트 추가를 취소합니다")
        return
    
    category = get_valid_input("\n카테고리: ")
    if category == ":c":
        print("프롬프트 추가를 취소합니다")
        return
    
    new_prompt = {
        "title": title,
        "content": content,
        "category": category,
        "is_favorite": False,
        "views": 0
    }
    prompts.append(new_prompt)
    print("\n프롬프트가 성공적으로 추가되었습니다.")

def list_prompts(sort_by_views=False):
    """
    sort_by_views가 True이면 조회수 내림차순(desc)으로 정렬하여 출력합니다.
    """
    clear_screen()
    print("\n--- 프롬프트 리스트 ---")
    
    # 데이터가 없을 때 처리
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return

    # 정렬 로직: 조회수(views) 기준으로 내림차순 정렬
    display_list = prompts
    if sort_by_views:
        display_list = sorted(prompts, key=lambda x: x['views'], reverse=True)
        print("(조회수 순위 정렬 적용)")
    
    print("==========================================================")
    for i, p in enumerate(display_list, 1):
        fav = "⭐" if p["is_favorite"] else "☆"
        print(f"{i:>2}. [{p['category']:^8}] {p['title']}  {fav} (조회수: {p['views']})")
    
    print("==========================================================")
    print("\nP. 메인 메뉴로 돌아가기")
# ==========================================
# 서브 메뉴 모음
# ==========================================
def manage_prompt_menu():
    options = {
        "1": "추가하기",
        "2": "리스트 보기",
        "3": "조회 수 순위로 리스트 보기"
    }
    actions = {
        "1": add_prompt,
        "2": list_prompts,
        "3": lambda: list_prompts(sort_by_views=True)
    }
    run_submenu("1. 프롬프트 관리하기", options, actions)

def manage_category_menu():
    options = {"1": "리스트 보기"}
    actions = {"1": lambda: print("카테고리 리스트 (추후 구현 예정)")}
    run_submenu("2. 카테고리별 보기", options, actions)

def manage_favorite_menu():
    options = {"1": "즐겨찾기 목록 보기"}
    actions = {"1": lambda: print("즐겨찾기 목록 (추후 구현 예정)")}
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
        clear_screen() # 메인 메뉴를 그리기 전에 화면 지우기
        show_main_menu()
        
        choice = get_valid_input("번호를 입력하세요: ").upper()
        
        match choice:
            case "1": 
                clear_screen() # 메인 메뉴를 그리기 전에 화면 지우기
                manage_prompt_menu()
            case "2": 
                clear_screen() # 메인 메뉴를 그리기 전에 화면 지우기
                manage_category_menu()
            case "3": 
                clear_screen() # 메인 메뉴를 그리기 전에 화면 지우기
                manage_favorite_menu()
            case "S": 
                clear_screen() # 메인 메뉴를 그리기 전에 화면 지우기
                save_prompts()
                pause_screen() # 결과 확인용 대기
            case "L": 
                clear_screen() # 메인 메뉴를 그리기 전에 화면 지우기
                load_prompts()
                pause_screen() # 결과 확인용 대기
            case "E": 
                clear_screen() # 메인 메뉴를 그리기 전에 화면 지우기
                export_to_markdown()
                pause_screen()
            case "0":
                clear_screen() # 메인 메뉴를 그리기 전에 화면 지우기
                print("프로그램을 종료합니다.")
                break
            case _:
                print("잘못된 입력입니다. 다시 선택해주세요.")
                pause_screen()

if __name__ == "__main__":
    main()