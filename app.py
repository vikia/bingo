# coding = utf-8
# author = wufeijia

from flask import Flask, request, json, render_template, Response
import uuid
import hashlib
import random
import logging
import datetime

from cvlib.grabcut import GrabCutter

app = Flask(__name__)

g_cache = {}

CACHE_TIME_OUT = 30 * 60

logging=app.logger

def set_cache(key, item):
    g_cache[key] = (item, datetime.datetime.now())

def get_cache(key):
    if not g_cache.has_key(key):
        return None
    item, start = g_cache[key]
    ds = (datetime.datetime.now() - start).seconds
    if ds > CACHE_TIME_OUT:
        g_cache.pop(key)
        return None
    return item

@app.route('/pintu')
def serve_pintu():
    return render_template('pintu.htm')

@app.route('/color_picker')
def serve_xise():
    return render_template('xise.htm')

@app.route('/demo-v2')
def serve_demo_v2():
    return render_template('demo-v2.html')

@app.route('/bingo_url')
def serve_bingo_url():
    args = "".join(request.url.split('?')[1:])
    print args
    server = 'http://127.0.0.1:8088/bingo/?'
    img_url = server + args
    print img_url
    resp = {"img":img_url}

    return json.jsonify(resp)

@app.route('/bingo')
def serve_bingo():
    return render_template('bingo-design.htm')

@app.route('/grabcut', methods = ['POST', 'GET'])
def serve_grabcut():
    return render_template('grabcut.htm')

@app.route('/filters')
def serve_filters():
    return render_template('filters.htm')

#@app.route('/grabcut', methods = ['POST', 'GET'])
#def serve_grabcut():
#    url = request.args.get('img', '')
#    print url
#    cutter = GrabCutter()
#    img = cutter.process(url)
#
#    return Response(img, mimetype="image/jpeg")

@app.route('/get-userids', methods = ['POST', 'GET'])
def get_old_user():
    app.logger.debug("request url params: %s", request)
    no_cache = request.args.get('cache', '').lower() == 'no'
    ip = str(request.remote_addr)

    result = ''
    if no_cache or get_cache(ip) is None:
        resp = {}
        old_users = g_nn_rec_dict.keys()
        rnd_list = random.sample(range(len(old_users)), min(10, len(old_users)))
        old_sample_users = [old_users[r] for r in rnd_list]
        resp['old'] = old_sample_users
        resp['new'] = [random.randrange(50000, 99999) for i in range(10)]
        app.logger.info("ip=%s route=/get-userids no_cache=%s res=%s", request.remote_addr, no_cache, resp)
        result = json.jsonify(resp)
        set_cache(ip, result)
        return result
    else:
        return get_cache(ip)

@app.route('/get-userids-v2', methods = ['POST', 'GET'])
def get_old_user_v2():
    app.logger.debug("request url params: %s", request)
    no_cache = request.args.get('cache', '').lower() == 'no'
    ip = str(request.remote_addr)

    result = ''
    if no_cache or get_cache(ip) is None:
        resp = {}
        old_users = g_prod_rec_dict.keys()
        rnd_list = random.sample(range(len(old_users)), min(10, len(old_users)))
        old_sample_users = [old_users[r] for r in rnd_list]
        resp['old'] = old_sample_users
        resp['new'] = [random.randrange(50000, 99999) for i in range(10)]
        app.logger.info("ip=%s route=/get-userids no_cache=%s res=%s", request.remote_addr, no_cache, resp)
        result = json.jsonify(resp)
        set_cache(ip, result)
        return result
    else:
        return get_cache(ip)

def rec_nn_model(n, uid):
    rec_list = g_nn_rec_dict[uid]
    return rec_list[:min(n, len(rec_list))]

def rec_prod_model(n, uid):
    rec_list = g_prod_rec_dict[uid]
    return rec_list[:min(n, len(rec_list))]

def rec_hot(n):
    return g_hot_rec_list[:min(n, len(g_hot_rec_list))]

def rec_prod_hot(n):
    hot_list = g_prod_hot_list[:min(n, len(g_prod_hot_list))]
    rec_list = []
    for tup in hot_list:
        uid, score = tup
        item = g_prod_info_dict[int(uid)] or {}
        item['score'] = score
        rec_list.append(item)
    return rec_list

def rec_random(n):
    rec_list = []
    rnd_list = random.sample(range(len(g_materials_list)), min(n, len(g_materials_list)))
    for i in range (0, n): 
        rec_item = g_materials_list[rnd_list[i]]
        rec_item['score'] = str(random.random() * 5)
        rec_item['strategy'] = 'random'
        rec_list.append(rec_item)
    return rec_list

def rec_random_prod(n): 
    rec_list = []
    ori_list = g_prod_info_dict.keys()
    rnd_list = random.sample(range(len(ori_list)), min(n, len(ori_list)))
    for i in range (0, n): 
        rec_item = g_prod_info_dict[ori_list[rnd_list[i]]]
        rec_item['score'] = str(random.random() * 5)
        rec_item['strategy'] = 'random'
        rec_list.append(rec_item)
    return rec_list

@app.route('/ad-rec-v2', methods = ['POST', 'GET'])
def get_rec_by_uid_v2():
    # params = request.get_json()
    app.logger.debug("request url params: %s", request)
    resp = {}
    uid = ''
    req_num = 0
    try:
        uid = request.args.get('uid')
        req_num = int(request.args.get('num'))

        resp['uid'] = uid
        rec_list = []
        if g_prod_rec_dict.has_key(int(uid)):
            # rec_list = g_nn_rec_dict[int(uid)]
            rec_list = rec_prod_model(req_num, int(uid))
            # resp['ad_res'] = rec_list[:req_num]
            resp['history'] = g_prod_info_dict[int(uid)]
        else:
            hot_num = int(req_num * 0.6)
            rand_num = req_num - hot_num
            rec_list = rec_prod_hot(hot_num) + rec_random_prod(rand_num)
        resp['ad_res'] = rec_list
    except Exception as e:
        app.logger.warning("Bad request: %s", e)
        resp = {"error_code":1, "error":"invalid param"}

    result = json.jsonify(resp)
    app.logger.info("ip=%s route=/ad-rec uid=%s req_num=%d ad_res=%s", \
            request.remote_addr, uid, req_num, resp)
    return result

@app.route('/ad-rec', methods = ['POST', 'GET'])
def get_rec_by_uid():
    # params = request.get_json()
    app.logger.debug("request url params: %s", request)
    resp = {}
    uid = ''
    req_num = 0
    try:
        uid = request.args.get('uid')
        req_num = int(request.args.get('num'))

        # validate
        # verify = params['v']
        # c = "?uid=%s&salt=poc" % uid
        # if verify.lower() != hashlib.md5(c).hexdigest():
            # raise ValueError("Bad verify code")

        resp['uid'] = uid
        rec_list = []
        if g_nn_rec_dict.has_key(int(uid)):
            # rec_list = g_nn_rec_dict[int(uid)]
            rec_list = rec_nn_model(req_num, int(uid))
            # resp['ad_res'] = rec_list[:req_num]
        else:
            hot_num = int(req_num * 0.6)
            rand_num = req_num - hot_num
            rec_list = rec_hot(hot_num) + rec_random(rand_num)
        resp['ad_res'] = rec_list
    except Exception as e:
        app.logger.warning("Bad request: %s", e)
        resp = {"error_code":1, "error":"invalid param"}

    result = json.jsonify(resp)
    app.logger.info("ip=%s route=/ad-rec uid=%s req_num=%d ad_res=%s", \
            request.remote_addr, uid, req_num, resp)
    return result

if __name__ == '__main__':
    # logging.basicConfig(filename="log/rec-serv.log", level="INFO", \
            # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # logging.setLevel('INFO')

    app.run(debug=False, port=3389, host='0.0.0.0')
