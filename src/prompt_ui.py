# 메인 메뉴 출력
def show_menu():
    print("\n--- 프롬프트 관리 프로그램 ---")
    print("==============")
    print("1. 프롬프트 관리하기")
    print("2. 카테고리별 보기")
    print("3. 즐겨찾기 관리")
    print("==============")
    print("S. 저장하기")
    print("L. 불러오기")
    print("==============")
    print("0. 종료")

#프롬프트 관리하기
def show_prompt():
    print("\n --- 1. 프롬프트 관리하기 ---")
    print("==============")
    print("1. 추가하기")
    print("2. 리스트 보기")
    print("3. 조회 수 순위로 리스트 보기")
    print("==============")

#카테고리별 보기 - 카테고리 목록 출력
def show_category():
    print("\n --- 2. 카테고리별 보기 ---")
    print("==============")
    print("1. 리스트 보기")
    print("==============")

#즐겨찾기 보기 - 실제 즐겨찾기 된 프롬프트를 출력
def show_favorite():
    print("\n --- 3. 즐겨찾기 관리 ---")
    print("==============")


def main():
    while True:
        show_menu()
        choice = input("번호를 입력하세요: ")
        if choice == "0":
            print("프로그램을 종료합니다.")
            break

        

if __name__ == "__main__":
    main()