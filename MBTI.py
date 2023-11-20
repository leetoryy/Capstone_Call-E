def answers(questions):
    answers = []
    for question in questions:
        answer = input(question).upper()
        while answer not in ['O', 'X']:
            print('O 또는 X만 눌러주세요!')
            answer = input(question).upper()
        answers.append(answer)
    return answers

def mbti_type(answers):
    score = {
        'E': 0,
        'I': 0,
        'S': 0,
        'N': 0,
        'T': 0,
        'F': 0,
        'J': 0,
        'P': 0
    }

    for index, answer in enumerate(answers):
        if answer == 'O':
            if index == 0:
                score['E'] += 1
            elif index == 1:
                score['I'] += 1
            elif index == 2:
                score['S'] += 1
            elif index == 3:
                score['N'] += 1
            elif index == 4:
                score['T'] += 1
            elif index == 5:
                score['F'] += 1
            elif index == 6:
                score['J'] += 1
            elif index == 7:
                score['P'] += 1
        elif answer == 'X':
            if index == 0:
                score['I'] += 1
            elif index == 1:
                score['E'] += 1
            elif index == 2:
                score['N'] += 1
            elif index == 3:
                score['S'] += 1
            elif index == 4:
                score['F'] += 1
            elif index == 5:
                score['T'] += 1
            elif index == 6:
                score['P'] += 1
            elif index == 7:
                score['J'] += 1

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
    questions = [
        '1. 처음 보는 아이들과 쉽게 얘기를 하거나 친해진다.',
        '2. 친구를 쉽게 사귀지 못하고 몇몇 아이들하고만 아주 친하게 지낸다.',
        '3. 주변 사람들의 외모나 다른 특징을 자세하게 기억한다.',
        '4. 엉뚱한 행동이나 생각을 할 때가 종종 있다.',
        '5. 야단을 맞거나 벌을 받아도 눈물을 잘 흘리지 않는다.',
        '6. 불쌍한 사람이나 친구들을 보면 돕고 싶어한다.',
        '7. 공부나 할 일을 해 놓은 후에 노는 편이다.',
        '8. 일이 생기면 그때그때 실행하는 편이다.'
    ]

    print(f'당신의 유형은: {mbti_type(answers(questions))}')

if __name__ == "__main__":
    mbti_test()