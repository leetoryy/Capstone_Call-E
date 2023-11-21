def answers(questions):
    # 질문에 대한 답변 저장
    answers = []
    for question in questions:
        answer = input(question)
        # 유효한 답변이 아닐 경우 다시 입력 요청
        while answer not in ['1', '2']:
            print('1 또는 2만 눌러주세요!')
            answer = input(question)
        answers.append(answer)
    return answers

def mbti_type(answers):
    # MBTI 항목별 점수 기록하는 딕셔너리 초기화
    score = {key: 0 for key in ['E', 'I', 'S', 'N', 'T', 'F', 'J', 'P']}
    # MBTI 유형에 따라 점수 부여
    for index, answer in enumerate(answers):
        # 답변이 1일 경우 MBTI 유형에 따라 점수 부여
        if answer == '1':
            if index == 0:
                score['I'] += 1
            elif index == 1:
                score['E'] += 1
            elif index == 2:
                score['E'] += 1
            elif index == 3:
                score['I'] += 1
            elif index == 4:
                score['S'] += 1
            elif index == 5:
                score['S'] += 1
            elif index == 6:
                score['S'] += 1
            elif index == 7:
                score['N'] += 1
            elif index == 8:
                score['T'] += 1
            elif index == 9:
                score['F'] += 1
            elif index == 10:
                score['T'] += 1
            elif index == 11:
                score['T'] += 1
            elif index == 12:
                score['J'] += 1
            elif index == 13:
                score['J'] += 1
            elif index == 14:
                score['J'] += 1
            elif index == 15:
                score['P'] += 1
        # 답변이 2일 경우 MBTI 유형에 따라 점수 부여
        elif answer == '2':
            if index == 0:
                score['E'] += 1
            elif index == 1:
                score['I'] += 1
            elif index == 2:
                score['I'] += 1
            elif index == 3:
                score['E'] += 1
            elif index == 4:
                score['N'] += 1
            elif index == 5:
                score['N'] += 1
            elif index == 6:
                score['N'] += 1
            elif index == 7:
                score['S'] += 1
            elif index == 8:
                score['F'] += 1
            elif index == 9:
                score['T'] += 1
            elif index == 10:
                score['F'] += 1
            elif index == 11:
                score['F'] += 1
            elif index == 12:
                score['P'] += 1
            elif index == 13:
                score['P'] += 1
            elif index == 14:
                score['P'] += 1
            elif index == 15:
                score['J'] += 1
    # 점수 비교하여 MBTI 유형 문자열 생성
    mbti_type = ""
    if score['E'] > score['I']:
        mbti_type += 'E'
    else:
        mbti_type += 'I'
    if score['S'] > score['N']:
        mbti_type += 'S'
    else:
        mbti_type += 'N'
    if score['T'] > score['F']:
        mbti_type += 'T'
    else:
        mbti_type += 'F'
    if score['J'] > score['P']:
        mbti_type += 'J'
    else:
        mbti_type += 'P'

    return mbti_type

def mbti_test():
    # MBTI 검사지
    questions = [
        '1. 나는 새로운 친구를 사귈 때..\n(1) 친구가 먼저 다가오면 이야기를 하는 경우가 많아요.\n(2) 내가 먼저 다가가서 이야기를 하는 경우가 더 많아요.\n',
        '2. 새로운 모둠 반에 처음 들어가게 되었어요. 이때 나는..\n(1) 새로운 친구들을 만나게 되어 신이나요.\n(2) 새로운 친구들과 어떻게 지낼까 걱정이 돼요.\n',
        '3. 내 성격은..\n(1) 활발하다는 말을 많이 들어요.\n(2) 부끄러움을 많이 타요.\n',
        '4. 나는 놀 때..\n(1) 혼자 노는 걸 좋아해요.\n(2) 친구들과 다같이 노는 걸 좋아해요.\n',
        '5. 나는 만들기 시간에 선생님이 만드신 것과..\n(1) 비슷하게 만드는 것이 더 즐거워요.\n(2) 다르게 내 생각대로 만드는 것이 더 즐거워요.\n',
        '6. 나는 책을 읽을 때..\n(1) 실제 이야기가 좋아요.\n(2) 상상 속의 이야기가 좋아요.\n',
        '7. 주변 사람의 모습을..\n(1) 잘 기억해요.\n(2) 잘 기억 못해요.\n',
        '8. 그림 그리기 시간에 나는..\n(1) 그리고 싶은 그림을 그리는 것이 좋아요.\n(2) 그려져 있는 그림을 예쁘게 색칠하는 것이 좋아요.\n',
        '9. 친구가 울고 있을 때 나는..\n(1) “친구야, 왜 울어?”하고 왜 우는지 물어봐요.\n(2) “친구야, 울지 마”하고 달래줘요.\n',
        '10. 부모님께 혼났을 때 나는..\n(1) 슬퍼서 울다가 말을 제대로 하지 못해요.\n(2) “그래서 이럴 수 밖에 없었어요.” 하고 이유를 설명해요.\n',
        '11. 나는 커서..\n(1) 공평한 사람이 되고 싶어요.\n(2) 친절한 사람이 되고 싶어요.\n',
        '12. 나는 친구들과 놀 때 뭐 하면서 놀지..\n(1) 빨리 정해요.\n(2) 쉽게 정하지 못해요.\n',
        '13. 오늘 수업 시간에 게임이나 만들기를 한대요..\n(1) 전에 배웠던 방법으로 하고 싶어요.\n(2) 새로운 방법으로 해보고 싶어요.\n',
        '14. 나는 숙제를..\n(1) 미리 끝내놓는 게 좋아요.\n(2) 마지막까지 미루는 게 좋아요.\n',
        '15. 나는 물건을 사용하고 나서..\n(1) 정해진 자리에 둬요.\n(2) 바로 사용하기 쉽게 적당한 곳에 둬요.\n',
        '16. 나는 하루를 보낼 때..\n(1) 특별한 계획 없이 즐겁게 보내는 것이 좋아요.\n(2) 미리 정해놓은 계획에 따라 보내는 것이 좋아요.\n'
    ]

    print(f'당신의 유형은: {mbti_type(answers(questions))}')

if __name__ == "__main__":
    mbti_test()