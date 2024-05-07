from openai import OpenAI

# context = [{'role': 'system', 'content': """
# You are a medical robot, providing medical consultation services to patients.
# First, you should greet the patient and ask what's the name and age and symptoms
# then wait for them give answer. Please make sure you collect all the information before you proceed/
# After gathering the information, confirm whether the patient needs to add anything else.
# You need to inform the patient about the possible diseases related to their symptoms,
# whether they can take any medication on their own, or if they should seek immediate medical attention,
# and which department they should visit.
# You should also advise the patient on how to prevent diseases.
# Finally, offer your well wishes.
# Please ensure that your responses are casual and friendly, and make sure they are logical.
# """}]


client = OpenAI(api_key=open_api_key)


def casual_talk(user_input, model="gpt-3.5-turbo"):
    return True


def check_for_dob(user_input, model="gpt-3.5-turbo"):
    context = [
        {'role': 'system',
         'content': "Extract the date of birth from the user's response using format YYYY-MM-DD, if present. If not, return that No DOB was found."
                    "For example, you found the date of birth is 1993-03-30, then just return '1993-03-30' as the response in str."
                    "also accept mm/dd/yyyy format or other formats"},
        {'role': 'user', 'content': user_input}
    ]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=context,
            max_tokens=50
        )
        extracted_response = response.choices[0].message.content
        if extracted_response.lower().__contains__("no") and extracted_response.lower().__contains__('found'):
            return [False, extracted_response]
        else:
            return [True, extracted_response]
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def check_for_name(user_input, model="gpt-3.5-turbo"):
    context = [
        {'role': 'system',
         'content': "Extract the name from the user's response, if present. If not, return that no name was found. "
                    "For example, you found the name is Shiva, then just return Shiva as the response"},
        {'role': 'user', 'content': user_input}
    ]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=context,
            max_tokens=50
        )
        extracted_response = response.choices[0].message.content
        if extracted_response.lower().__contains__("no name was found"):
            return [False, extracted_response]
        else:
            return [True, extracted_response]
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def check_for_age(user_input, model="gpt-3.5-turbo"):
    context = [
        {'role': 'system',
         'content': "Extract the age from the user's response, if present. If not, return that no age was found. "
                    "For example, you found the age is 13, then just return 13 as the response"},
        {'role': 'user', 'content': user_input}
    ]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=context,
            max_tokens=50
        )
        extracted_response = response.choices[0].message.content
        if extracted_response.lower().__contains__("no age was found"):
            return [False, extracted_response]
        else:
            return [True, extracted_response]
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def check_for_health_condition(user_input, model="gpt-3.5-turbo"):
    context = [
        {'role': 'system',
         'content': "Extract the health condition or symptom from the user's response, if present. If not, return that no health condition was found. "
                    "For example, you found the health condition is having a cold, then just put having a cold in the response"},
        {'role': 'user', 'content': user_input}
    ]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=context,
            max_tokens=50
        )
        extracted_response = response.choices[0].message.content
        if extracted_response.lower().__contains__("no health condition was found"):
            return [False, extracted_response]
        else:
            return [True, extracted_response]
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# def process_input(request):
#     user_input = request.json['message']
#     name = check_for_name(user_input)
#     if name:
#         response_message = f"Thank you for providing your name, {name}. What is your age?"
#     else:
#         response_message = "I couldn't find a name in your response. Could you please tell me your name?"
#
#     return jsonify({"message": response_message})



#
# def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
#     response = client.chat.completions.create(
#         model=model,
#         messages=messages,
#         temperature=temperature,
#     )
#     return response.choices[0].message.content