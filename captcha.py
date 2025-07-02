import random

def generate_captcha():
    num1 = random.randint(1, 100)
    num2 = random.randint(1, 100)
    
    operation = random.choice(['+', '-'])
    
    if operation == '-' and num1 < num2:
        num1, num2 = num2, num1
    
    if operation == '+':
        correct_answer = num1 + num2
    else:
        correct_answer = num1 - num2

    answers = set()
    answers.add(correct_answer)
    while len(answers) < 3:
        wrong_answer = correct_answer + random.randint(-10, 10)
        if wrong_answer != correct_answer and wrong_answer > 0:
            answers.add(wrong_answer)

    answers = list(answers)
    random.shuffle(answers)
    
    captcha_question = f"What is {num1} {operation} {num2}?"
    return captcha_question, answers, correct_answer

