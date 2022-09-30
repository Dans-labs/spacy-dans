from parsr_client import ParsrClient

parsr = ParsrClient('localhost:3001')


def upload_file(file, name, result_type):
    parsr.send_document(file_path=file, config_path="defaultConfig.json", document_name=name, save_request_id=True)
    if result_type == 'JSON':
        return parsr.get_json()
    elif result_type == "MARKDOWN":
        return parsr.get_markdown()
    elif result_type == "TEXT":
        return parsr.get_text()
    else:
        return None
