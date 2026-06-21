# openclaw-s14-operation-diagnosis-skill/templates/ota_diagnosis_report_demo.template.html

类型：项目资料
关键词：OTA, 诊断

---

">
 <nav class="sidebar dashboard-only">
 <a href="#overview">顶部总览卡片</a><a href="#modules">模块得分条形图</a><a href="#trend">经营趋势图</a><a href="#funnel">流量漏斗对比</a><a href="#rooms">房型排行表</a><a href="#promotion">推广效率表</a><a href="#tasks">整改任务表</a><a href="#missing">补采提示</a>
 </nav>
 <main>
 <section id="overview"><div class="section-head"><div><h2>顶部总览卡片</h2><p>规则、模块权重、封顶和展示组件均从《酒店OTA全面诊断系统_开发交付总文档_v2_精简版.xlsx》读取；当前数据源为本地测试表格，未接数据库。</p></div><span class="status warn">风险：中风险</span></div>
 <div class="section-body"><div class="kpi-grid">
 <div class="kpi"><label>总分</label><strong class="num">64 / 100</strong><span>原始分 63.8，转化封顶：转化下单模块低于60%，需优先核查浏览-支付转化。</span></div>
 <div class="kpi"><label>数据可信度</label><strong class="num">36%</strong><span>缺失字段会进入补采提示，不包装成已获取</span></div>
 <div class="kpi"><label>核心问题</label><strong>转化/趋势补采</strong><span>飞猪经营折线趋势、直通车点击/CPC未完整采集</span></div>
 <div class="kpi"><label>复盘周期</label><strong class="num">7 / 14 天</strong><span>复盘日期：2026-06-17</span></div>
 </div><div class="cap-alert"><b>封顶/校准规则</b><span><ul><li>数据可信度封顶：关键经营字段缺失超过30%，总分最高不得超过70。</li><li>转化封顶：转化下单模块低于60%，需优先核查浏览-支付转化。</li></ul></span><span class="status warn">按交付表校准</span></div></div>
 </section>
 <section id="modules"><div class="section-head"><div><h2>模块得分条形图</h2><p>8个模块得分 / 权重 / 得分率，低于60%标红，60-79%标黄</p></div></div><div class="section-body"><table class='data-table'><thead><tr><th>模块</th><th>得分</th><th>得分率</th><th>状态</th><th>核心依据</th></tr></thead><tbody><tr><td>M01 经营结果与收益锚点</td><td><div class='score-bar'><span>14.3 / 20</span><div class='bar-track'><div class='bar-fill warn' style='width:72%'></div></div><b>72%</b></div></td><td>72%</td><td><span class='status warn'>需要优化</span></td><td>订单结果：飞猪订单数与同行预订订单对比<br>收入结果：门店收入环比 -78.1%<br>RevPAR收益质量：RevPAR 114.14，近3月均值 122.00</td></tr><tr><td>M02 流量曝光与竞争圈</td><td><div class='score-bar'><span>10.5 / 15</span><div class='bar-track'><div class='bar-fill warn' style='width:70%'></div></div><b>70%</b></div></td><td>70%</td><td><span class='status warn'>需要优化</span></td><td>曝光竞争圈倍数：飞猪经营数据趋势未逐点补齐，按已确认入口和当前快照暂估<br>浏览竞争圈倍数：飞猪经营数据趋势未逐点补齐，按已确认入口和当前快照暂估<br>广告/非广告曝光结构：免费流量和广告流量结构</td></tr><tr><td>M03 转化下单与路径断点</td><td><div class='score-bar'><span>7.0 / 15</span><div class='bar-track'><div class='bar-fill bad' style='width:46%'></div></div><b>46%</b></div></td><td>46%</td><td><span class='status bad'>严重短板</span></td><td>曝光-浏览转化：转化趋势/流失数据不完整，按缺口降分<br>浏览-支付转化：转化趋势/流失数据不完整，按缺口降分<br>支付订单能力：转化趋势/流失数据不完整，按缺口降分</td></tr><tr><td>M04 价格收益与房态库存</td><td><div class='score-bar'><span>9.1 / 15</span><div class='bar-track'><div class='bar-fill warn' style='width:60%'></div></div><b>60%</b></div></td><td>60%</td><td><span class='status warn'>需要优化</span></td><td>库存销售速度：低效房型 7 个<br>房型RevPAR分层：低效房型 7 个<br>价格带覆盖：覆盖多个价格入口</td></tr><tr><td>M05 推广效率与ROI</td><td><div class='score-bar'><span>7.2 / 10</span><div class='bar-track'><div class='bar-fill warn' style='width:72%'></div></div><b>72%</b></div></td><td>72%</td><td><span class='status warn'>需要优化</span></td><td>推广ROI：推广ROI 14.68<br>推广订单产出：全网推有产出，但曝光/点击/CPC仍需补采<br>推广点击效率：全网推有产出，但曝光/点击/CPC仍需补采</td></tr><tr><td>M06 页面展示与入口基础</td><td><div class='score-bar'><span>4.5 / 10</span><div class='bar-track'><div class='bar-fill bad' style='width:45%'></div></div><b>45%</b></div></td><td>45%</td><td><span class='status bad'>严重短板</span></td><td>信息分与名称：页面质量来自模拟飞书表单，部分项为 partial<br>权益与服务配置：页面质量来自模拟飞书表单，部分项为 partial<br>图片视频亮点：页面质量来自模拟飞书表单，部分项为 partial</td></tr><tr><td>M07 口碑信任与服务响应</td><td><div class='score-bar'><span>6.8 / 8</span><div class='bar-track'><div class='bar-fill good' style='width:85%'></div></div><b>85%</b></div></td><td>85%</td><td><span class='status good'>正常/轻微可优化</span></td><td>点评分与大众点评：可见评价均分 4.50，未回复 5<br>点评数量与新增：可见评价均分 4.50，未回复 5<br>回复率与时效：可见评价均分 4.50，未回复 5</td></tr><tr><td>M08 执行复盘与数据完整度</td><td><div class='score-bar'><span>4.5 / 7</span><div class='bar-track'><div class='bar-fill warn' style='width:64%'></div></div><b>64%</b></div></td><td>64%</td><td><span class='status warn'>需要优化</span></td><td>数据完整度：关键字段完整度 36.4%<br>动作完成率：模拟表单已提供整改动作和异常复盘<br>整改前后对比：模拟表单已提供整改动作和异常复盘</td></tr></tbody></table></div></section>
 <section id="trend"><div class="section-head"><div><h2>经营趋势图</h2><p>ADR、出租率、RevPAR、门店收入；月度趋势来自 JY03 测试数据</p></div></div><div class="section-body two-col"><div class="subpanel trend-wrap"><h3>月度经营趋势（鼠标悬停查看数值）</h3><div class="subpanel-content"><svg viewBox="0 0 640 250" class="trend-chart" aria-label="经营趋势图">

<line x1="55" y1="215.0" x2="620" y2="215.0" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="4,4"/>
<text x="50" y="215.0" text-anchor="end" dominant-baseline="middle" style="font-size:11px;fill:#6b7280">-15</text>

<line x1="55" y1="176.0" x2="620" y2="176.0" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="4,4"/>
<text x="50" y="176.0" text-anchor="end" dominant-baseline="middle" style="font-size:11px;fill:#6b7280">21</text>

<line x1="55" y1="137.0" x2="620" y2="137.0" stroke="#e5e7eb" stroke-width="1" stroke-dasharray="4,4"/>
<text x="50" 
