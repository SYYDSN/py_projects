
2017-08-09
team_info表
增加一列 root_team =1  =0
表示是否是公司的根团队（一个公司只有一个根团队）
plan_item_info 删除member_sn的外键


2017-07-12
增加
base_track_info 基本跟进信息
track_info 跟进信息
track_type 跟进类型


修改
customer_info 增加 in_pool列 默认值0 ，增加in_count_company，默认值1
employee_info   修改team_sn非空，默认值1 删除外键约束
customer_info 增加触发器，同步修改team_sn ?



2017-07-11
修改
team_info  删除company_sn外键设置，sn从50000开始
position_info 增加has_team 列，删除 position_name 唯一性检查



2017-07-08
修改
position_info 删除parent_sn的外键
employee_info  删除position_sn的外键

删除
staff_info 表


2017-07-04
新增 
extend_channel_info 推广渠道信息
extend_pattern_info 推广方式信息
extend_platform_info 推广平台信息


修改
special_url_info 
增加channel_sn,pattern_sn,platform_sn和外键。
增加is_3th 是否第三方这一列


2017-07-01

新增
employee_info 表 员工
team_info 表 团队
special_url_info  专用链接表

删除
staff_info 表


修改
customer_info
增加 employee_sn 所属员工sn
增加 in_count 是否参与分配统计 默认是1，参与
position_info
增加 company_sn 外键约束
增加 parent_sn 上级职务的sn
