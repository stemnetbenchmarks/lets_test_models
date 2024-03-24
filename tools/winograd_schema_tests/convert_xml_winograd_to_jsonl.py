
import xml.etree.ElementTree as ET
import json

def get_answer_index(correct_answer):
    if correct_answer.strip().upper().replace(".","") == 'A':
        return 1
    elif correct_answer.strip().upper().replace(".","") == 'B':
        return 2
    else:
        return None

def process_xml(xml_file, jsonl_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    with open(jsonl_file, 'w', encoding='utf-8') as file:
        for schema in root.findall('schema'):
            text_elements = schema.find('text')
            txt1 = text_elements.find('txt1').text.strip()
            pron = text_elements.find('pron').text.strip()
            txt2 = text_elements.find('txt2').text.strip()

            question = f"{txt1} {pron} {txt2}"

            # answers = [answer.text.strip() for answer in schema.find('answers').findall('answer')]
            answers = [f"{i+1}. {answer.text.strip()}" for i, answer in enumerate(schema.find('answers').findall('answer'))]

            correct_answer = schema.find('correctAnswer').text.strip()
            answer_index = get_answer_index(correct_answer)

            quote_elements = schema.find('quote')
            if quote_elements is not None:
                quote_pron = quote_elements.find('pron')
                quote2 = quote_elements.find('quote2')
                if quote_pron is not None and quote2 is not None:
                    quote = f"{quote_pron.text.strip()} {quote2.text.strip()}"
                else:
                    quote = None
            else:
                quote = None

            data = {
                'task': question,
                'options': answers,
                'answer_from_index_start_at_1': answer_index,
                # 'quote': quote
            }

            json_line = json.dumps(data)
            file.write(json_line + '\n')

# Usage example
xml_file = 'WSCollection.xml'
jsonl_file = 'output.jsonl'
process_xml(xml_file, jsonl_file)