# AliPay

今日内容:
	支付宝支付
		正式环境:用营业执照,申请商户号,appid
		测试环境:沙箱环境:https://openhome.alipay.com/platform/appDaily.htm?tab=info
		支付宝提供接口:给商户使用,收钱
		-Java,php,C#的demo,没有python的demo
		-git有人封装了,pycryptodome模块内有加密算法。
		-需要安装模块:pip3 install pycryptodome
		-应用私钥---自己保存,一定不能丢
		-应用公钥---给别人用
		-支付宝公钥---支付宝用的
		-生成公钥私钥:https://docs.open.alipay.com/291/105971
		-把应用公钥配置在支付宝上:应用公钥,配置完成以后,支付宝自动生成一个支付宝公钥
		
		-在程序中:配置应用私钥app_private】】_2048,支付宝公钥alipay_public_2048
		
		-如果支付成功,支付宝会回调,但是如果你的服务器挂掉了怎么办?
			-支付宝24小时以内不定时再给你发,你修改掉订单状态即可
		-支付成功,支付宝会有一个get回调,一个post回调:修改订单状态
