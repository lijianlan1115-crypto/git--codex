# openclaw-s14-operation-diagnosis-skill/templates/ota_diagnosis_report_demo.template.html

类型：项目资料
关键词：OTA, 诊断

---

>建立整改动作日志和7/14天复盘机制</td><td>动作完成率、订单、收入、RevPAR</td><td>14天</td></tr></tbody></table></div></section>
 <section id="missing"><div class="section-head"><div><h2>补采提示</h2><p>缺失字段、影响、采集方式；数据缺失不等于经营差，但影响可信度</p></div></div><div class="section-body"><table class='data-table'><thead><tr><th>缺失字段</th><th>当前状态</th><th>处理建议</th><th>责任来源</th></tr></thead><tbody><tr><td>RevPAR</td><td>当前页面未直接看到</td><td>由房费收入/可售房量或 PMS 计算</td><td>系统计算/PMS</td></tr><tr><td>ADR</td><td>飞猪显示间夜单价</td><td>可映射为飞猪口径 ADR，与 PMS ADR 区分</td><td>飞猪/系统计算</td></tr><tr><td>CPC/点击均价</td><td>全网推未展示，直通车待确认</td><td>从直通车数据中心或报表导出采集</td><td>飞猪直通车</td></tr><tr><td>推广曝光/点击</td><td>全网推未展示，直通车待确认</td><td>从直通车数据中心/API/导出采集</td><td>飞猪直通车</td></tr><tr><td>图片质量/HOS 历史/入口标签质量</td><td>入口可查，质量判断需人工或视觉模型</td><td>飞书表单补采，必要时接视觉模型</td><td>人工/模型</td></tr><tr><td>核心竞对名单</td><td>同行动态有同行列表/价库对比</td><td>飞书表单维护 1-4 个核心竞对</td><td>人工</td></tr><tr><td>整改动作与复盘原因</td><td>平台不自动知道业务原因</td><td>飞书表单/任务中心记录</td><td>人工</td></tr></tbody></table></div></section>
 </main>
 </div>
 
<script>
var tooltip = null;

function showTooltip(event, label, value, x, y) {
 if (!tooltip) {
 tooltip = document.createElement('div');
 tooltip.className = 'chart-tooltip';
 tooltip.style.cssText = 'position:absolute; pointer-events:none; padding:6px 10px; background:#1d2430; color:#fff; border-radius:4px; font-size:12px; z-index:1000; box-shadow:0 2px 8px rgba(0,0,0,0.3);';
 document.body.appendChild(tooltip);
 }
 tooltip.innerHTML = '<strong>' + label + '</strong><br/>' + value.toFixed(2);
 tooltip.style.left = (event.clientX + 10) + 'px';
 tooltip.style.top = (event.clientY - 30) + 'px';
 tooltip.style.display = 'block';
}

function hideTooltip() {
 if (tooltip) {
 tooltip.style.display = 'none';
 }
}

function switchChannel(channel) {
 document.querySelectorAll('[data-channel-section]').forEach(function(el) {
 el.style.display = 'none';
 });
 
 if (channel === 'all') {
 document.querySelectorAll('[data-channel-section]').forEach(function(el) {
 el.style.display = '';
 });
 } else {
 document.querySelectorAll('[data-channel-section="' + channel + '"]').forEach(function(el) {
 el.style.display = '';
 });
 }
 
 document.querySelectorAll('.channel-tab').forEach(function(tab) {
 tab.classList.remove('active');
 });
 document.querySelector('[data-channel-tab="' + channel + '"]')?.classList.add('active');
 
 document.getElementById('channelSelector').value = channel;
}
</script>

</body>
</html>
