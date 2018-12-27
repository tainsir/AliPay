from django.shortcuts import render, redirect, HttpResponse
from utils.pay import AliPay
import json
import time
def ali():
    # 沙箱环境地址：https://openhome.alipay.com/platform/appDaily.htm?tab=info
    # 一个商户号是唯一的appid
    app_id = "2016092000554611"
    # 支付宝收到用户的支付,会向商户发两个请求,一个get请求,一个post请求，带的数据是支付成功/失败的标志，
    # 程序能收到请求，会把订单号发过来，通过订单号确定支付状态(从待支付到)是否已支付，钱到了商户号那里，商户再从商户号取钱

    # POST请求，用于最后的检测
    # 服务器地址，类比127.0.0.1，支付宝内侧用42.56.89.12，后期要放在公网的ip上，别人可以直接访问
    notify_url = "http://42.56.89.12:80/page2/"

    # GET请求，用于页面的跳转展示
    return_url = "http://42.56.89.12:80/page2/"
    # 交互数据必须要加密。支付宝返回status=100，appid=1001，向接口发POST请求，订单号、状态都有了，钱可能没付，订单状态改了，黑客可能模拟支付宝发请求。
    # 非对称性加密，公钥、私钥，在keys文件夹下面，随机字符串
    # 私钥不能丢，易被黑客窃取，能模拟请求，黑客提交100w订单，模拟支付成功，申请退款退给黑客
    merchant_private_key_path = "keys/app_private_2048.txt"
    alipay_public_key_path = "keys/alipay_public_2048.txt"
    # 生成一个AliPay的对象
    alipay = AliPay(
        appid=app_id,
        app_notify_url=notify_url,
        return_url=return_url,
        app_private_key_path=merchant_private_key_path,
        alipay_public_key_path=alipay_public_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
        debug=True,  # 默认False,
    )
    return alipay


def page1(request):
    if request.method == "GET":

        return render(request, 'page1.html')
    else:
        money = float(request.POST.get('money'))
        # 生成一个对象
        alipay = ali()
        # 生成支付的url
        # 对象调用direct_pay
        query_params = alipay.direct_pay(
            subject="充气娃娃",  # 商品简单描述
            out_trade_no="x2" + str(time.time()),  # 商户订单号
            total_amount=money,  # 交易金额(单位: 元 保留俩位小数)
        )
        # 支付宝网关，不带dev是实际地址，带dev是测试环境，向测试环境发get请求，带数据过去，生成支付宝支付的页面。
        pay_url = "https://openapi.alipaydev.com/gateway.do?{}".format(query_params)
        print(pay_url)
        # 朝这个地址发get请求，
        # 输金额，'去支付'，朝支付宝地址发请求，交易支付成功后支付宝给我发get，post俩请求，重定向到'交易付款成功，正在跳转至商户页面'
        return redirect(pay_url)


def page2(request):
    alipay = ali()
    # post请求
    if request.method == "POST":
        # 检测是否支付成功
        # 去请求体中获取所有返回的数据：状态/订单号
        from urllib.parse import parse_qs

        # 从body体拿数据，不知道是urlenco/json编码格式，转码成字符串。
        body_str = request.body.decode('utf-8')
        print(body_str)
        # 系统内置解析方法parse_qs，解析成字典格式，放在post_dict内，
        post_data = parse_qs(body_str)
        print('支付宝给我的数据:::---------',post_data)
        post_dict = {}
        for k, v in post_data.items():
            post_dict[k] = v[0]
        print('转完之后的字典',post_dict)

        # 传参字典+签名，status校验成功/失败，post_dict中的订单号可以取出来，确定订单状态
        sign = post_dict.pop('sign', None)
        status = alipay.verify(post_dict, sign)
        print('POST验证', status)
        return HttpResponse('POST返回')

    # get请求
    else:
        # 数据转成字典
        params = request.GET.dict()
        # 拿出字典中的sign字段
        sign = params.pop('sign', None)
        # 验证的方法，通过sign把数据传过去后，校验成功/失败，不是直接状态码取出来校验
        # 调用verify方法，传参数据+sign，
        status = alipay.verify(params, sign)
        print('GET验证', status)
        return HttpResponse('支付成功')
