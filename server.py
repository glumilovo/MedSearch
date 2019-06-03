import hashlib
import datetime as date
import json
from uuid import uuid4, UUID

from flask import Flask, jsonify, request

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    def hash_block(self):
        temp = {
            'index' : self.index,
            'data' : self.data
        }
        block_string = json.dumps(temp, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


class Blockchain(object):
    def __init__(self):
        self.blockchain = [self.create_genesis_block()]
        self.previous_block = self.blockchain[0]

    def create_genesis_block(self):
        # Manually construct a block with
        # index zero and arbitrary previous hash
        return Block(0, date.datetime.now(), "Genesis Block", "0")

    def next_block(self, last_block, data):
        this_index = last_block.index + 1
        this_timestamp = date.datetime.now()
        this_data = data
        this_hash = last_block.hash
        return Block(this_index, this_timestamp, this_data, this_hash)

    def generate_block(self, data):
        new_block = self.next_block(self.previous_block, data)
        self.previous_block = new_block
        self.blockchain.append(new_block)
        return new_block

    def check(self, hash):
        for block in self.blockchain:
            if block.hash == hash:
                return block

        return None


# Создаем экземпляр узла
app = Flask(__name__)

# Генерируем уникальный на глобальном уровне адрес для этого узла
node_identifier = str(uuid4()).replace('-', '')

# Создаем экземпляр блокчейна
blockchain = Blockchain()

# Список активных сессий
accessList = []

# Юзеры
users = [{"login": "admin", "password": "admin"}]


@app.route('/generate', methods=['GET'])
def mine():
    values = request.get_json()

    # Убедитесь в том, что необходимые поля находятся среди POST-данных
    required = ['data']
    if not all(k in values for k in required):
        return 'Missing values', 400

    block = blockchain.generate_block(values['data'])
    response = {'hash': block.hash}
    return jsonify(response), 200


@app.route('/check', methods=['GET'])
def full_chain():
    values = request.get_json()

    # Убедитесь в том, что необходимые поля находятся среди POST-данных
    required = ['hash']
    if not all(k in values for k in required):
        return 'Missing values', 400

    block = blockchain.check(values['hash'])
    if not(block is None):
        response = {'data': block.data}
        return jsonify(response), 200

    return 'Check failed', 400


@app.route('/test', methods=['GET'])
def test():
    return '', 200


@app.route('/login', methods=['GET'])
def login():
    login = request.args['login']
    password = request.args['password']
    for user in users:
        if user['login'] == login and user['password'] == password:
            token = uuid4()
            response = {'Success': True, 'AccessToken': token}
            accessList.append(token)
            return jsonify(response), 200

    response = {'Success': False, 'AccessToken': ''}
    return jsonify(response), 200


@app.route('/logout', methods=['GET'])
def logout():

    access_token = UUID(request.args['access_token'])


    accessList.remove(access_token)
    return '', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)

