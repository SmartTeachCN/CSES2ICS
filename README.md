# CSES2ICS
: 转换 CSES(Course Schedule Exchange Schema) 为 iCalendar

CSES2ICS是一个简单的 Python 3 程序，旨在将CSES格式的课程表转换为`.ics`格式的日历文件，允许使用者将课程表转换为日程并导入至日历软件或带有日历/提醒同步功能的手环/手表等。

## 快速使用

```bash
pip install -r requirements.txt
python main.py schedule.yaml
```
其中`schedule.yaml`应为 CSES v1 的课程表文件。
缺省输出文件为`schedule.ics`

## 功能简介

- [x] 解析 CSES v1 文件
- [x] 输出有效的 iCalendar 文件
- [x] 猜测课程表起始与结束日期
- [x] 处理单双周课表并去重
- [x] 忽略特定名称的课程
- [ ] 忽略特定时间段的课程

## 参数说明

| 参数                      | 说明                                | 缺省值        | 示例            |
|---------------------------|-------------------------------------|---------------|-----------------|
| -h/--help                 | 显示帮助                            | -             | -               |
| --timezone                | 设置时区                            | Asia/Shanghai | Asia/Shanghai   |
| --calendar-start-date     | 日历开始日期[^1]                    | -             | 2025-01-31      |
| --calendar-end-date       | 日历结束日期                        | -             | 2025-07-31      |
| --use-teacher-as-location | 使用`teacher`字段作为`location`的值 | True          | False           |
| --ignore-class-names      | 忽略课程的名称列表,使用英文逗号隔开   |               | 眼保健操,晚自习 |
| --output-filename         | 输出文件名                          | schedule.ics  | schedule.ics    |

[^1]: 课程计算将于该日后（含该日）的第一个星期一开始

## 依赖

- Python 3.6+
- Required packages listed in requirements.txt
