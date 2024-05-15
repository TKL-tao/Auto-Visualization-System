# Auto-Visualization-System
This is my independent project in HKUST(GZ). The topic is given by HUAWEI Cloud and Prof. Luo.  Given a database (SQLite), this system can generate an intended visualization graph based on users' natural language requests.

(**Demonstration Video and technical document are coming soon...**)

# Functionality Test Cases
Here use the example from Spider test database **candidate_poll**, whose database schema is shown below.

![](static/imgs/candidate_poll.png)

## Login and upload database
![](static/videos/demonstration1.gif)

## Cross-table querying in a database
Question: 我只想知道候选者中的男女性别比例。

![](static/videos/demonstration2.gif)

## Specify the plot type
Question: 我只想知道候选者中的男女性别比例，用条形图表示。

![](static/videos/demonstration3.gif)

## Specify the axes
Question: 我想知道所有男生的身高和体重的散点图分布，横坐标为体重。

![](static/videos/demonstration4.gif)

## Involving a calculation formula
Question: 我想知道所有人的BMI，BMI等于体重除以身高的平方，请用条形图表示，横坐标为姓名，纵坐标为BMI。

![](static/videos/demonstration5.gif)
