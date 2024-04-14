from linebot.v3.messaging import (
    TextMessage, QuickReply, QuickReplyItem, PostbackAction
)
import json
import random
import urllib.parse

# 出題数
QUESTION_LIMIT = 5

def generate_reply(data: dict):
    ret = []

    questions = load_questions()
    action = data["action"]
    history = data.copy()
    history.pop("action")

    if action == "start":
        ## 問いかけ
        ret.append(TextMessage(text="大阪地名クイズを始めるで"))
        ## 問題選択
        (picked_question_id, picked_question) = pick_question(questions)
        ## クイックリプライ生成
        quick_reply = generate_quick_replys(history, picked_question_id, picked_question)
        ## メッセージ生成
        ret.append(TextMessage(text=picked_question["word"], quickReply=quick_reply))
    elif action == "answer":
        ret.append(TextMessage(text="次やで"))
        ## 使用済みの問題を外す
        questions = get_unused_questions(questions, history)
        (picked_question_id, picked_question) = pick_question(questions)
        quick_reply = generate_quick_replys(history, picked_question_id, picked_question)
        ret.append(TextMessage(text=picked_question["word"], quickReply=quick_reply))
    else:
        ret.append(TextMessage(text="おわりやで"))
        ret.append(generate_result(questions, history))
    return ret

def load_questions():
    with open("questions.json") as f:
        questions = json.load(f)
    return questions

def pick_question(questions: dict):
    question_id = random.choice(list(questions.keys()))
    return (question_id, questions[question_id])

def generate_quick_replys(history: dict, question_id: str, question: dict):
    question_number = count_answered(history) + 1
    isfinal = question_number == QUESTION_LIMIT
    items = []
    for i in range(len(question["options"])):
        items.append(generate_quick_reply_item(history, question_number, question_id, i, question["options"][i], isfinal))
    return QuickReply(items=items)

def generate_quick_reply_item(history: dict, question_number: int, question_id: str, option_number, option: str, isfinal):
    data = {**history}
    if isfinal:
        data["action"] = "finish"
    else:
        data["action"] = "answer"
    data.update({"q" + str(question_number) + "id": question_id, "q" + str(question_number) + "answer": option_number})
    datastr = urllib.parse.urlencode(data)
    action = PostbackAction(label=option, data=datastr, displayText=option)
    return QuickReplyItem(action=action)

def count_answered(history: dict):
    count = len(list(filter(lambda x: "id" in x, list(history.keys()))))
    return count

def get_unused_questions(questions, history):
    answered_id_keys = list(filter(lambda x: "id" in x, list(history.keys())))
    used_ids = [history[x] for x in answered_id_keys]
    ret = questions.copy()
    for used_id in used_ids:
        del ret[used_id]
    return ret

def generate_result(questions:dict, history: dict):
    correct_ids = []
    for i in range(QUESTION_LIMIT):
        question = questions[history["q" + str(i + 1) + "id"]]
        if question["correct"] == question["options"][int(history["q" + str(i + 1) + "answer"])]:
            correct_ids.append(history["q" + str(i + 1) + "id"])
    return TextMessage(text=f"{QUESTION_LIMIT}問中、{len(correct_ids)}問正解や！")
