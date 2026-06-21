# openclaw-s14-operation-diagnosis-skill/references/excel_field_mapping.csv

类型：字段契约
关键词：收益, RevPAR, ADR, OCC, OTA, 渠道, 订单, 字段, PMS, 诊断

---

卖点状态|房型卖点|room_selling_point_status,enum,M06,是,_calculate_m06：complete/partial/poor/unknown评分,首个非空,日/周/月/诊断周期,建议提供 data_date；周期内多行会按聚合方式计算,是,按渠道房型页区分,否,缺失默认unknown
entry_tag_quality,入口标签质量|入口标签|entry_tag_quality,enum,M06,是,_calculate_m06：complete/partial/poor/unknown评分,首个非空,日/周/月/诊断周期,建议提供 data_date；周期内多行会按聚合方式计算,是,按渠道入口标签区分,否,缺失默认unknown
rating_total,平台评分|评分|点评分|rating_total,number,M07,是,_calculate_m07：rating_total/4.8*0.5*8,平均值,日/周/月/诊断周期,建议提供 data_date；周期内多行会按聚合方式计算,是,按渠道评分体系区分,是,缺失默认4.0并进入缺失字段
bad_review_rate,差评率|低分评价率|bad_review_rate,ratio,M07,是,_calculate_m07：bad_review_rate 与0.03目标反向比较,平均值,日/周/月/诊断周期,建议提供 data_date；周期内多行会按聚合方式计算,是,按渠道评价体系区分,否,缺失默认0.08
unreplied_reviews,未回复评价|未回复评价数|unreplied_reviews,number,M07,是,_calculate_m07：未回复越多扣分,求和,日/周/月/诊断周期,建议提供 data_date；周期内多行会按聚合方式计算,是,按渠道评价回复区分,否,缺失按0
completed_actions,已完成动作|已完成整改|completed_actions,string,M08,是,_calculate_m08：有已完成和待完成动作得动作分,首个非空,日/周/月/诊断周期,建议提供 data_date；周期内多行会按聚合方式计算,是,动作可按渠道记录,否,缺失降低M08动作分
pending_actions,待完成动作|待整改动作|pending_actions,string,M08,是,_calculate_m08：有已完成和待完成动作得动作分,首个非空,日/周/月/诊断周期,建议提供 data_date；周期内多行会按聚合方式计算,是,动作可按渠道记录,否,缺失降低M08动作分
review_reason,复盘原因|异常原因|review_reason,string,M08,是,_calculate_m08：有复盘原因得复盘分,首个非空,日/周/月/诊断周期,建议提供 data_date；周期内多行会按聚合方式计算,是,复盘原因可按渠道记录,否,缺失降低M08复盘分
field_completeness,字段完整度|数据完整度|field_completeness,ratio,M08,是,_calculate_m08 和 apply_cap_rules：低于0.7触发C07,平均值/自动计算,日/周/月/诊断周期,建议提供 data_date；周期内多行会按聚合方式计算,是,按渠道字段完整度计算,否,缺失时由runtime按关键字段自动计算
