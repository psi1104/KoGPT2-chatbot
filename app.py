from flask import Flask, request, Response, jsonify, render_template
from queue import Queue, Empty
import time
import threading
import torch
from gluonnlp.data import SentencepieceTokenizer
from kogpt2.pytorch_kogpt2 import get_pytorch_kogpt2_model
from kogpt2.utils import get_tokenizer
from train_torch import KoGPT2Chat

# Server & Handling Setting
app = Flask(__name__)

requests_queue = Queue()
BATCH_SIZE = 1
CHECK_INTERVAL = 0.1

tok_path = get_tokenizer()
tok = SentencepieceTokenizer(tok_path, num_best=0, alpha=0)

_, vocab = get_pytorch_kogpt2_model()

model = KoGPT2Chat.load_from_checkpoint("model_chp/model_last.ckpt")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

U_TKN = '<usr>'
S_TKN = '<sys>'
BOS = '<s>'
EOS = '</s>'
MASK = '<unused0>'
SENT = '<unused1>'


# Queue 핸들링
def handle_requests_by_batch():
    try:
        while True:
            requests_batch = []

            while not (
              len(requests_batch) >= BATCH_SIZE
            ):
              try:
                requests_batch.append(requests_queue.get(timeout=CHECK_INTERVAL))
              except Empty:
                continue

            batch_outputs = []

            for request in requests_batch:
                batch_outputs.append(chat(request['input'][0]))

            for request, output in zip(requests_batch, batch_outputs):
                request['output'] = output

    except Exception as e:
        while not requests_queue.empty():
            requests_queue.get()
        print(e)
# 쓰레드
threading.Thread(target=handle_requests_by_batch).start()

def chat(text):
    sent_tokens = tok('0')
    with torch.no_grad():
        q = text.strip()
        q_tok = tok(q)
        a = ''
        a_tok = []
        start_time = time.time()
        while 1:
            running_time = time.time()
            if running_time - start_time > 2:
                return "timeout"

            input_ids = torch.LongTensor([vocab[U_TKN]] + vocab[q_tok] +
                                         vocab[EOS, SENT] + vocab[sent_tokens] +
                                         vocab[EOS, S_TKN] +
                                         vocab[a_tok]).unsqueeze(dim=0)

            input_ids = input_ids.to(device)

            pred = model(input_ids)
            gen = vocab.to_tokens(
                torch.argmax(
                    pred,
                    dim=-1).cpu().squeeze().numpy().tolist())[-1]
            if gen == EOS:
                break
            a += gen.replace('▁', ' ')
            a_tok = tok(a)

        return a.strip()


@app.route("/gpt2-chat", methods=['POST'])
def gpt2_chat():
    try:
        # 큐에 쌓여있을 경우,
        if requests_queue.qsize() > BATCH_SIZE:
            return jsonify({'error': 'Too Many Requests'}), 429

        try:
            args = []
            text = request.form['text']
            args.append(text)

        except Exception as e:
            print("Empty Text")
            print(e)
            return Response("fail", status=400)

        # Queue - put data
        req = {
            'input': args
        }
        requests_queue.put(req)

        # Queue - wait & check
        while 'output' not in req:
            time.sleep(CHECK_INTERVAL)

        return req['output']

    except Exception as e:
        print(e)
        return jsonify({"error": "server error."}), 500


@app.route('/')
def main():
    return render_template('index.html')


# Health Check
@app.route("/healthz", methods=["GET"])
def healthCheck():
    return "", 200


if __name__ == "__main__":
    from waitress import serve
    serve(app, host='0.0.0.0', port=80)
