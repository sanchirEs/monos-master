""" bot buttons """
import json

def get_button_list():
    """
    get button list
    """

    button_list = list()

    button_list.append({"content_type":"text", "title":"Материал", "payload": '{"type": 1, "choice": 1, "text": "monos"}'})

    button_list.append({"content_type":"text", "title":"Тест", "payload": '{"type": 1, "choice": 2, "text": "monos"}'})

    button_list.append({"content_type":"text", "title":"Зөвлөмж", "payload": '{"type": 1, "choice": 3, "text": "monos"}'})

    button_list.append({"content_type":"text", "title":">", "payload": '{"type": 1, "choice": 4, "text": "monos"}'})

    return button_list


def get_button_list2():
    """
    get button list2
    """

    button_list = list()

    button_list.append({"content_type":"text", "title":"<", "payload": '{"type": 1, "choice": 5, "text": "monos"}'})

    button_list.append({"content_type":"text", "title":"Жагсаалт", "payload": '{"type": 1, "choice": 7, "text": "monos"}'})

    button_list.append({"content_type":"text", "title":"Хөтөлбөр сонгох", "payload": '{"type": 1, "choice": 6, "text": "monos"}'})

    return button_list


def get_button_list3():
    """
    get button list3
    """

    button_list = list()

    button_list.append({"content_type":"text", "title":"Сонгох", "payload": '{"type": 1, "choice": 6, "text": "monos"}'})

    button_list.append({"content_type":"text", "title":"Жагсаалт", "payload": '{"type": 1, "choice": 7, "text": "monos"}'})

    return button_list


def get_button_list4(campaign_hashtag, campaign_name):
    """
    get button list4
    """

    payload = dict()

    payload['type'] = 20

    payload['choice'] = 1

    payload['text'] = {'hashtag':campaign_hashtag, 'name':campaign_name}

    button_list = list()

    button_list.append({"content_type":"text", "title":"<", "payload": json.dumps(payload)})

    payload['choice'] = 2

    button_list.append({"content_type":"text", "title":"Материал", "payload": json.dumps(payload)})

    payload['choice'] = 3

    button_list.append({"content_type":"text", "title":"Тест", "payload": json.dumps(payload)})

    payload['choice'] = 5

    button_list.append({"content_type":"text", "title":"Зөвлөгөө", "payload": json.dumps(payload)})

    return button_list


def get_button_cancel(next_step_id):
    """
    get button cancel
    """

    payload = dict()

    payload['type'] = 1

    payload['choice'] = 8

    payload['text'] = next_step_id

    button_list = list()

    button_list.append({"content_type":"text", "title":"Болих", "payload": json.dumps(payload)})

    return button_list


def get_button_continue(button_text, next_step_id):
    """
    get button continue
    """

    payload = dict()

    payload['type'] = 1

    payload['choice'] = 9

    payload['text'] = next_step_id

    button_list = list()

    button_list.append({"content_type":"text", "title":button_text, "payload": json.dumps(payload)})

    return button_list


def get_user_reg_buttons():
    """
    get button list2
    """

    button_list = list()

    button_list.append({"content_type":"text", "title":"Хүсэлт илгээх", "payload": '{"type": 10, "choice": 1, "text": "monos"}'})

    return button_list
