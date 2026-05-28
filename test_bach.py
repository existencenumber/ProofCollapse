import requests
import json

BASE_URL = "https://proof-collapse.onrender.com/"  # 本地测试；云端改为 https://你的地址

test_cases = [
    ("每个大于2的偶数可以表示为两个素数之和", "success", "加法域", "乘法域", 1),
    ("存在无穷多对孪生素数", "success", "乘法域", "编织域", 3),
    ("杨-米尔斯理论存在正的质量间隙", "success", "谱域", "加法域", 2),
    ("对于任意正整数，考拉兹迭代最终必达到1", "success", "加法域", "乘法域", 1),
    ("黎曼zeta函数的所有非平凡零点位于临界线上", "success", "乘法域", "谱域", 1),
    ("每个单连通三维闭流形同胚于三维球面", "success", "同伦域", "范畴域", 1),
    ("纳维-斯托克斯方程存在全局光滑解", "success", "积分域", "泛函积分域", 1),
    ("霍奇猜想", "success", "谱域", "乘法域", 1),
    ("BSD猜想", "success", "谱域", "加法域", 2),
    ("朗兰兹函子性猜想", "success", "乘法域", "谱域", 1),
    ("费马大定理", "success", "加法域", "乘法域", 1),
    ("任意两个正交矩阵的乘积仍为正交矩阵", "success", "乘法域", "乘法域", 0),
    ("任意两个整数的和仍为整数", "success", "加法域", "加法域", 0),
    ("矩阵乘法满足结合律", "success", "乘法域", "乘法域", 0),
    ("质数有无穷多个", "success", "乘法域", "乘法域", 0),
    ("每个大于5的素数都可以写成6k±1的形式", "success", "乘法域", "加法域", 1),
    ("每一个偶数都是两个素数之和", "success", "加法域", "乘法域", 1),
    ("素数定理", "success", "乘法域", "谱域", 1),
    ("圆是可尺规作图的吗", "unrecognized", None, None, 0),
    ("根号2是无理数", "unrecognized", None, None, 0),
    ("e是超越数", "unrecognized", None, None, 0),
    ("是否存在奇完全数", "unrecognized", None, None, 0),
    ("连续统假设", "unrecognized", None, None, 0),
    ("选择公理", "unrecognized", None, None, 0),
    ("NP完全问题", "unrecognized", None, None, 0),
    ("P不等于NP", "unrecognized", None, None, 0),
    ("四色定理", "unrecognized", None, None, 0),
    ("费马小定理", "success", "加法域", "乘法域", 1),
    ("欧拉定理 (数论)", "success", "乘法域", "加法域", 1),
    ("每个整数都可以唯一分解为素数的乘积", "success", "加法域", "乘法域", 1),
    ("黎曼猜想", "success", "乘法域", "谱域", 1),
    ("广义黎曼猜想", "success", "乘法域", "谱域", 1),
    ("朗道-西格尔零点猜想", "success", "乘法域", "谱域", 1),
    ("阿廷猜想", "unrecognized", None, None, 0),
    ("贝赫和斯维讷通-戴尔猜想", "unrecognized", None, None, 0), # BSD别名可能识别不出
    ("科拉茨猜想", "success", "加法域", "乘法域", 1),  # 别名
    ("冰雹猜想", "unrecognized", None, None, 0),
    ("角谷猜想", "unrecognized", None, None, 0),
    ("叙拉古猜想", "unrecognized", None, None, 0),
    ("华林问题", "unrecognized", None, None, 0),
    ("哥德巴赫-欧拉猜想", "success", "加法域", "乘法域", 1),
    ("孪生素数有无穷多对吗", "success", "乘法域", "编织域", 3),
    ("素数间隙可以任意小吗", "success", "乘法域", "乘法域", 0),
    ("素数分布是否随机", "success", "乘法域", "谱域", 1),
    ("是否存在无穷多梅森素数", "unrecognized", None, None, 0),
    ("是否存在无穷多费马素数", "success", "乘法域", "乘法域", 0),
    ("二次互反律", "unrecognized", None, None, 0),
    ("狄利克雷定理", "success", "乘法域", "加法域", 1),
    ("素数在等差数列中无穷多", "success", "乘法域", "加法域", 1),
    ("伯兰特-切比雪夫定理", "unrecognized", None, None, 0),
    ("素数定理的误差项", "success", "乘法域", "谱域", 1),
    ("黎曼zeta函数的非平凡零点都在临界线上", "success", "乘法域", "谱域", 1),
    ("黎曼zeta函数在负偶数处有零点", "success", "乘法域", "谱域", 1),
    ("黎曼zeta函数在s=1处有极点", "success", "乘法域", "谱域", 1),
    ("欧拉乘积公式", "success", "乘法域", "谱域", 1),
    ("函数方程", "unrecognized", None, None, 0),
    ("哈代-利特尔伍德圆法", "unrecognized", None, None, 0),
    ("筛法", "unrecognized", None, None, 0),
    ("解析数论", "unrecognized", None, None, 0),
    ("代数数论", "unrecognized", None, None, 0),
    ("椭圆曲线", "unrecognized", None, None, 0),
    ("模曲线", "success", "谱域", "乘法域", 1),
    ("志村簇", "unrecognized", None, None, 0),
    ("伽罗瓦表示", "success", "乘法域", "谱域", 1),
    ("自守形式", "success", "谱域", "乘法域", 1),
    ("朗兰兹纲领", "success", "乘法域", "谱域", 1),
    ("霍奇结构", "success", "谱域", "乘法域", 1),
    ("德拉姆上同调", "unrecognized", None, None, 0),
    ("平展上同调", "unrecognized", None, None, 0),
    ("晶体上同调", "unrecognized", None, None, 0),
    ("韦伊猜想", "unrecognized", None, None, 0),
    ("格罗滕迪克标准猜想", "unrecognized", None, None, 0),
    ("莫德尔猜想", "unrecognized", None, None, 0),
    ("法尔廷斯定理", "unrecognized", None, None, 0),
    ("费马大定理 n=4", "success", "加法域", "乘法域", 1),
    ("怀尔斯证明", "success", "加法域", "乘法域", 1),
    ("谷山-志村猜想", "unrecognized", None, None, 0),
    ("塞尔猜想", "unrecognized", None, None, 0),
    ("里贝特定理", "unrecognized", None, None, 0),
    ("弗雷曲线", "unrecognized", None, None, 0),
    ("岩泽理论", "unrecognized", None, None, 0),
    ("代数K理论", "unrecognized", None, None, 0),
    ("米尔诺K理论", "unrecognized", None, None, 0),
    ("布洛赫-加藤猜想", "unrecognized", None, None, 0),
    ("贝林森猜想", "unrecognized", None, None, 0),
    ("森田等价", "unrecognized", None, None, 0),
    ("阿蒂亚-辛格指标定理", "unrecognized", None, None, 0),
    ("阿蒂亚-博特不动点定理", "unrecognized", None, None, 0),
    ("黎曼-罗赫定理", "unrecognized", None, None, 0),
    ("格罗滕迪克-黎曼-罗赫定理", "unrecognized", None, None, 0),
    ("塞尔对偶", "unrecognized", None, None, 0),
    ("庞加莱对偶", "success", "同伦域", "范畴域", 1),
    ("莱夫谢茨不动点定理", "unrecognized", None, None, 0),
    ("霍奇指标定理", "success", "谱域", "乘法域", 1),
    ("小平邦彦消没定理", "unrecognized", None, None, 0),
    ("博赫纳技巧", "unrecognized", None, None, 0),
    ("调和形式", "unrecognized", None, None, 0),
    ("凯勒流形", "unrecognized", None, None, 0),
    ("卡拉比-丘流形", "unrecognized", None, None, 0),
    ("爱因斯坦流形", "success", "同伦域", "范畴域", 1),
    ("里奇流", "success", "积分域", "同伦域", 2),  # 可能识别积分域+同伦域
    ("哈密顿量", "unrecognized", None, None, 0),
    ("薛定谔方程", "unrecognized", None, None, 0),
    ("狄拉克方程", "unrecognized", None, None, 0),
    ("麦克斯韦方程组", "unrecognized", None, None, 0),
    ("杨-米尔斯方程", "success", "谱域", "加法域", 2),
    ("纳维-斯托克斯方程", "success", "积分域", "泛函积分域", 1),
    ("欧拉方程 (流体)", "unrecognized", None, None, 0),
    ("热方程", "unrecognized", None, None, 0),
    ("波动方程", "unrecognized", None, None, 0),
]

passed = 0
failed = 0

for statement, exp_status, exp_source, exp_target, exp_depth in test_cases:
    try:
        resp = requests.post(f"{BASE_URL}/api/reason", json={"statement": statement})
        data = resp.json()
        status = data.get("status")
        if status == exp_status:
            # 对于成功情况，进一步检查域和深度
            if status == "success":
                source_ok = data.get("source") == exp_source
                target_ok = data.get("target") == exp_target
                depth_ok = data.get("depth") == exp_depth
                if source_ok and target_ok and depth_ok:
                    print(f"✅ {statement}: 成功")
                    passed += 1
                else:
                    print(f"⚠️ {statement}: 域或深度不匹配 (expected {exp_source}→{exp_target} depth={exp_depth}, got {data.get('source')}→{data.get('target')} depth={data.get('depth')})")
                    failed += 1
            else:
                print(f"✅ {statement}: 正确返回 {status}")
                passed += 1
        else:
            print(f"❌ {statement}: 期望 {exp_status}, 实际 {status}")
            failed += 1
    except Exception as e:
        print(f"❌ {statement}: 请求错误 {e}")
        failed += 1

print(f"\n测试完毕: 通过 {passed}/{len(test_cases)}, 失败 {failed}/{len(test_cases)}")
