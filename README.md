# CSES2ICS
## Convert the Course Schedule Exchange Schema to iCalendar

将CSES格式的课程表转换为iCS格式的日历文件，便于在设备上订阅并设置提醒或在嵌入式设备上查看课表。

## Usage

1. Create a CSES file with your course schedule
2. Run the converter:
```bash
python main.py schedule.yaml
```
3. The script will generate a `schedule.ics` file
4. Import the ICS file into your calendar app or set up calendar subscription

## Features

- Converts CSES format to standard iCalendar format
- Supports recurring events with specific weekday patterns
- Preserves teacher/location information
- Compatible with most calendar applications
- Handles both single and recurring classes

## Requirements

- Python 3.6+
- Required packages listed in requirements.txt

## Installation

```bash
pip install -r requirements.txt
```
