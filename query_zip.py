import json
import string
import zlib
import base64

maketrans = bytes.maketrans

plantuml_alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase + '-_'
base64_alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'
b64_to_plantuml = maketrans(base64_alphabet.encode('utf-8'), plantuml_alphabet.encode('utf-8'))
plantuml_to_b64 = maketrans(plantuml_alphabet.encode('utf-8'), base64_alphabet.encode('utf-8'))


def query_json_encode(plantuml_dict: dict):
    text = json.dumps(plantuml_dict, ensure_ascii=False, default=str)
    return query_encode(plantuml_text=text)


def query_encode(plantuml_text: str):
    """zlib compress the plantuml text and encode it for the plantuml server"""
    zlibbed_str = zlib.compress(plantuml_text.encode('utf-8'))
    compressed_string = zlibbed_str[2:-4]
    return base64.b64encode(compressed_string).translate(b64_to_plantuml).decode('utf-8')


def query_decode(plantuml_url: str):
    """decode plantuml encoded url back to plantuml text"""
    data = base64.b64decode(plantuml_url.translate(plantuml_to_b64).encode("utf-8"))
    dec = zlib.decompressobj()  # without check the crc.
    header = b'x\x9c'
    return dec.decompress(header + data).decode("utf-8")


def query_json_decode(plantuml_url: str) -> dict:
    try:
        return json.loads(query_decode(plantuml_url=plantuml_url))
    except Exception:
        return dict()
