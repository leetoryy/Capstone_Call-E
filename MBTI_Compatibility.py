def Compatibility(user, counselor):
    score = 0
    if user[0] == counselor[0]:
        score += 1
    else:
        score += 0.5
    
    if user[1] == counselor[1]:
        score += 1
    else:
        score += 0.5
    
    if user[2] == counselor[2]:
        score += 1
    else:
        score += 0.5
    
    if user[3] == counselor[3]:
        score += 1
    else:
        score += 0.5
    
    compatibility = (score / 4) * 100
    return compatibility

if __name__ == "__main__":
    compatibility = Compatibility(input("사용자 MBTI: ").upper(), input('상담사 MBTI: ').upper())
    print(f"궁합도: {compatibility:.2f}%")