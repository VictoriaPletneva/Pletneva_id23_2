from collections import defaultdict
import heapq
import base64
import json

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanXOR:
    def __init__(self, key):
        self.key = key
        self.codes = {}
        self.padding_value = 0

    def count_freq(self, text):
        freq = defaultdict(int)
        for char in text:
            freq[char] += 1
        return freq

    def build_huffman_tree(self, text):
        freq = self.count_freq(text)
        priority_queue = [Node(char, f) for char, f in freq.items()]
        heapq.heapify(priority_queue)

        while len(priority_queue) > 1:
            left = heapq.heappop(priority_queue)
            right = heapq.heappop(priority_queue)
            merged = Node(None, left.freq + right.freq)
            merged.left = left
            merged.right = right
            heapq.heappush(priority_queue, merged)

        return priority_queue[0]

    def generate_codes(self, node, current_code=""):
        if node is None:
            return
        if node.char is not None:
            self.codes[node.char] = current_code
            return
        self.generate_codes(node.left, current_code + "0")
        self.generate_codes(node.right, current_code + "1")

    def replace_codes(self, text):
        return ''.join(self.codes[char] for char in text)

    def pad(self, encoded_text):
        self.padding_value = 8 - len(encoded_text) % 8
        if self.padding_value != 8:
            encoded_text += "0" * self.padding_value
        return encoded_text

    def to_bytes(self, padded_encoded_text):
        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i + 8]
            b.append(int(byte, 2))
        return b

    def xor_encrypt(self, data: bytearray):
        key_bytes = self.key.encode('utf-8')
        return bytearray([data[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(data))])

    def encode_base64(self, byte_data):
        return base64.b64encode(byte_data).decode('utf-8')

    def encode(self, text):
        root = self.build_huffman_tree(text)
        self.generate_codes(root)
        encoded_text = self.replace_codes(text)
        padded_text = self.pad(encoded_text)
        byte_data = self.to_bytes(padded_text)
        encrypted_data = self.xor_encrypt(byte_data)
        encoded_encrypted = self.encode_base64(encrypted_data)

        return {
            "encoded_data": encoded_encrypted,
            "key": self.key,
            "huffman_codes": self.codes,
            "padding": self.padding_value
        }

    def decode(self, encoded_data, huffman_codes, padding_value):
        decoded_bytes = base64.b64decode(encoded_data)
        decrypted_bytes = self.xor_encrypt(decoded_bytes)
        bit_string = ''.join(f'{byte:08b}' for byte in decrypted_bytes)
        bit_string = bit_string[:-padding_value]

        reverse_codes = {v: k for k, v in huffman_codes.items()}
        current_code = ""
        decoded_text = ""

        for bit in bit_string:
            current_code += bit
            if current_code in reverse_codes:
                decoded_text += reverse_codes[current_code]
                current_code = ""

        return {"decoded_text": decoded_text}


if __name__ == "__main__":
    text = input("Введите текст \n")
    key = input("Введите ключ \n")

    encryptor = HuffmanXOR(key)
    encode_response = encryptor.encode(text)

    print("Результат шифрования (encode):")
    print(json.dumps(encode_response, indent=4))

    decode_response = encryptor.decode(
        encode_response["encoded_data"],
        encode_response["huffman_codes"],
        encode_response["padding"]
    )

    print("\nРезультат расшифровки (decode):")
    print(json.dumps(decode_response, indent=4))



