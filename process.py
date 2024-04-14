from linebot.v3.messaging import (
    TextMessage, QuickReply, QuickReplyItem, PostbackAction,
    FlexMessage, FlexBubble, FlexBox, FlexText, FlexSeparator, FlexSpan
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

    header_text = FlexText(text="結果発表～～", size="lg", weight="bold")
    header_box = FlexBox(layout="horizontal", paddingBottom="0px", contents=[header_text])
    result_count_box = FlexBox(layout="horizontal", height="100px", contents=[FlexText(align="center", contents=[FlexSpan(text=str(len(correct_ids)) + "/", size="5xl"), FlexSpan(text=f"{QUESTION_LIMIT}", size="3xl")])])
    detail_results = []
    for i in range(QUESTION_LIMIT):
        detail_results.append(generate_detail_result(i + 1, questions[history["q" + str(i + 1) + "id"]], history["q" + str(i + 1) + "answer"]))
    body_box = FlexBox(layout="vertical", paddingTop="0px", contents=[
        FlexText(text="正解数は..."),
        result_count_box,
        FlexSeparator(),
        FlexText(text="正しい読み方はこうやで"),
        *detail_results
    ])
    flex_bubble = FlexBubble(header=header_box, body=body_box)
    flex_message = FlexMessage(altText="flex", contents=flex_bubble)
    return flex_message

def generate_detail_result(question_number: int, question: dict, answer: str):
    iscorrect = question["options"][int(answer)] == question["correct"]
    if iscorrect:
        result_icon = "O"
        result_icon_color = "#009900"
    else:
        result_icon = "X"
        result_icon_color = "#DD0000"
    
    return FlexBox(layout="vertical",contents=[
        FlexText(text=f"Q.{question_number}", size="lg"),
        FlexBox(layout="horizontal", contents=[
            FlexText(text=result_icon, color=result_icon_color, weight="bold", flex=0),
            FlexText(text=question["word"]),
            FlexText(text=question["correct"])
        ])
    ])
