import sys
import pandas as pd
import json
from collections import Counter
import sqlite3

def main():
    if len(sys.argv) != 3:
        print("Usage: python simple_script.py <question> <dbPath>")
        sys.exit(1)

    sql = sys.argv[1]
    target_db = sys.argv[2]
    
    img_outputpath = "D:/NL2SQL/python_workspace/NL2SQL_data_preparation/AutoVisual_Results/test6/images/"
    json_outputpath = "D:/NL2SQL/python_workspace/NL2SQL_data_preparation/AutoVisual_Results/test6/test6.json"

    def sql2data(sql, target_db):
        conn = sqlite3.connect(target_db)
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]
            # print('SQL query succeeded.')
        except sqlite3.OperationalError:
            # print('SQL query failed.')
            return None, None, None

        column_types = []
        for item in rows[0]:
            if type(item).__name__ == 'int' or type(item).__name__ == 'float':
                column_types.append('numeric')
            else:
                column_types.append('categorical')
        # print(rows, column_names, column_types, sep='\n')
        return rows, column_names, column_types

    rows, column_names, column_types = sql2data(sql, target_db)
    # outputcsv_filepath = "D:/Development/HUAWEI_DataInsight/src/main/resources/csv_files/queried_results.csv"
    # pd.DataFrame(rows, columns=column_names).to_csv(outputcsv_filepath, index=False)

    class Data2Visual():
        def __init__(self, img_outputpath, json_outputpath):
            self.df = pd.DataFrame({})
            self.column_types = []

            self.column1_rule = {'categorical0': ['histogram'],
                                'categorical1': ['pie']}
            self.column2_rule = {'categorical0': ['scatter', 'line'],
                                'categorical1': ['bar', 'pie'],
                                'categorical2': []}
            self.column3_rule = {'categorical0': [],
                                'categorical1': ['scatter', 'line'],
                                'categorical2': ['bar'],
                                'categorical3': []}
            self.column4_rule = {}
            self.rules = {'column1': self.column1_rule,
                        'column2': self.column2_rule,
                        'column3': self.column3_rule,
                        'column4': self.column4_rule}
            self.img_outputpath = img_outputpath
            self.json_outputpath = json_outputpath
        def load_data(self, rows, column_names, column_types):
            self.df = pd.DataFrame(rows, columns=column_names)
            self.column_types = column_types

        def scatter_plot(self, json_list, plot_id):
            plot_type_id = 0
            numeric_indices = [i for i, value in enumerate(self.column_types) if value == 'numeric']
            categorical_indices = [i for i, value in enumerate(self.column_types) if value == 'categorical']
            for x_index in numeric_indices:
                remaining_numeric_indices = numeric_indices.copy()
                remaining_numeric_indices.remove(x_index)
                for y_index in remaining_numeric_indices:
                    if categorical_indices == []:  # 针对于查询数据中只有两列的情况
                        x = self.df.iloc[:, x_index]
                        y = self.df.iloc[:, y_index]
                        xaxis_title = self.df.columns[x_index]
                        yaxis_title = self.df.columns[y_index]
                        df = pd.DataFrame({f'{xaxis_title}': x, f'{yaxis_title}': y})
                        df_dict = df.to_dict(orient='list')
                        df_dict['plot_type'] = 'scatter'
                        df_dict['plot_type_id'] = plot_type_id
                        df_dict['plot_id'] = plot_id
                        json_list.append(df_dict)

                        # 绘图代码
                        # fig = px.scatter(df, x=f'{xaxis_title}', y=f'{yaxis_title}')
                        # fig.update_layout(xaxis_title=xaxis_title, yaxis_title=yaxis_title,
                        #                   font=dict(family='Times New Roman', size=24, color='black'))
                        # print('Output scatter plot')
                        # fig.write_image(self.img_outputpath + 'scatter{}.png'.format(plot_type_id))
                        # fig.show()

                        plot_type_id += 1
                        plot_id += 1

                    else:  # 针对查询数据中大于两列的情况
                        for class_index in categorical_indices:
                            x = self.df.iloc[:, x_index]
                            y = self.df.iloc[:, y_index]
                            grouped_class = self.df.iloc[:, class_index]
                            xaxis_title = self.df.columns[x_index]
                            yaxis_title = self.df.columns[y_index]
                            grouped_title = self.df.columns[class_index]
                            df = pd.DataFrame({f'{xaxis_title}': x, f'{yaxis_title}': y, f'{grouped_title}': grouped_class})
                            df_dict = df.to_dict(orient='list')
                            df_dict['plot_type'] = 'scatter'
                            df_dict['plot_type_id'] = plot_type_id
                            df_dict['plot_id'] = plot_id
                            json_list.append(df_dict)

                            # 绘图代码
                            # fig = px.scatter(df, x=f'{xaxis_title}', y=f'{yaxis_title}', color=f'{grouped_title}',
                            #                  hover_data=[f'{grouped_title}'], hover_name=f'{grouped_title}')
                            # fig.update_layout(xaxis_title=xaxis_title, yaxis_title=yaxis_title,
                            #                   font=dict(family='Times New Roman', size=24, color='black'))
                            # print('Output scatter plot')
                            # fig.write_image(self.img_outputpath + 'scatter{}.png'.format(plot_type_id))
                            # fig.show()

                            plot_type_id += 1
                            plot_id += 1
            return json_list, plot_id

        def bar_chart(self, json_list, plot_id):
            plot_type_id = 0
            numeric_indices = [i for i, value in enumerate(self.column_types) if value == 'numeric']
            categorical_indices = [i for i, value in enumerate(self.column_types) if value == 'categorical']
            for y_index in numeric_indices:
                for x_index in categorical_indices:
                    remaining_categorical_indices = categorical_indices.copy()
                    remaining_categorical_indices.remove(x_index)
                    if remaining_categorical_indices == []:  # 针对于查询数据中只有两列的情况
                        x = self.df.iloc[:, x_index]
                        y = self.df.iloc[:, y_index]
                        xaxis_title = self.df.columns[x_index]
                        yaxis_title = self.df.columns[y_index]
                        df = pd.DataFrame({f'{xaxis_title}': x, f'{yaxis_title}': y})
                        df_dict = df.to_dict(orient='list')
                        df_dict['plot_type'] = 'bar'
                        df_dict['plot_type_id'] = plot_type_id
                        df_dict['plot_id'] = plot_id
                        json_list.append(df_dict)

                        # 绘图代码
                        # fig = px.bar(df, x=f'{xaxis_title}', y=f'{yaxis_title}')
                        # fig.update_layout(xaxis_title=xaxis_title, yaxis_title=yaxis_title,
                        #                   font=dict(family='Times New Roman', size=24, color='black'))
                        # print('Output bar chart')
                        # fig.write_image(self.img_outputpath + 'bar{}.png'.format(plot_type_id))
                        # fig.show()

                        plot_type_id += 1
                        plot_id += 1

                    else:  # 针对查询数据中大于两列的情况
                        for class_index in remaining_categorical_indices:
                            x = self.df.iloc[:, x_index]
                            y = self.df.iloc[:, y_index]
                            grouped_class = self.df.iloc[:, class_index]
                            xaxis_title = self.df.columns[x_index]
                            yaxis_title = self.df.columns[y_index]
                            grouped_title = self.df.columns[:, class_index]
                            df = pd.DataFrame({f'{xaxis_title}': x, f'{yaxis_title}': y, f'{grouped_title}': grouped_class})
                            df_dict = df.to_dict(orient='list')
                            df_dict['plot_type'] = 'bar'
                            df_dict['plot_type_id'] = plot_type_id
                            df_dict['plot_id'] = plot_id
                            json_list.append(df_dict)

                            # 绘图代码
                            # fig = px.bar(df, x=f'{xaxis_title}', y=f'{yaxis_title}', color=f'{grouped_title}', barmode='group')
                            # fig.update_layout(xaxis_title=xaxis_title, yaxis_title=yaxis_title,
                            #                   font=dict(family='Times New Roman', size=24, color='black'))
                            # print('Output bar chart')
                            # fig.write_image(self.img_outputpath + 'bar{}.png'.format(plot_type_id))
                            # fig.show()

                            plot_type_id += 1
                            plot_id += 1
            return json_list, plot_id

        def pie_chart(self, json_list, plot_id):
            plot_type_id = 0
            if self.df.shape[1] == 1:  # 针对查询数据中仅有一列的情况
                x = Counter(self.df.iloc[:, 0]).keys()
                y = Counter(self.df.iloc[:, 0]).values()
                xaxis_title = self.df.columns[0]
                yaxis_title = 'Count'
                df = pd.DataFrame({f'{xaxis_title}': x, yaxis_title: y})
                df_dict = df.to_dict(orient='list')
                df_dict['plot_type'] = 'pie'
                df_dict['plot_type_id'] = plot_type_id
                df_dict['plot_id'] = plot_id
                json_list.append(df_dict)

                # 绘图代码
                # fig = px.pie(data_frame=df, names=f'{xaxis_title}', values=yaxis_title)
                # print('Output pie chart')
                # fig.show()
                # fig.write_image(self.img_outputpath + 'pie{}.png'.format(plot_type_id))

                plot_type_id += 1
                plot_id += 1
            elif self.df.shape[1] == 2:  # 针对查询数据中有两列的情况
                numeric_indices = [i for i, value in enumerate(self.column_types) if value == 'numeric']
                categorical_indices = [i for i, value in enumerate(self.column_types) if value == 'categorical']
                x_index, y_index = categorical_indices[0], numeric_indices[0]
                x = self.df.iloc[:, x_index]
                y = self.df.iloc[:, y_index]
                xaxis_title = self.df.columns[x_index]
                yaxis_title = self.df.columns[y_index]
                df = pd.DataFrame({f'{xaxis_title}': x, f'{yaxis_title}': y})
                df_dict = df.to_dict(orient='list')
                df_dict['plot_type'] = 'pie'
                df_dict['plot_type_id'] = plot_type_id
                df_dict['plot_id'] = plot_id
                json_list.append(df_dict)

                # 绘图代码
                # fig = px.pie(data_frame=df, names=f'{xaxis_title}', values=f'{yaxis_title}')
                # print('Output pie chart')
                # fig.show()
                # fig.write_image(self.img_outputpath + 'pie{}.png'.format(plot_type_id))

                plot_type_id += 1
                plot_id += 1
            return json_list, plot_id

        def histogram(self, json_list, plot_id):
            plot_type_id = 0
            y = self.df.iloc[:, 0]
            yaxis_title = self.df.columns[0]
            df = pd.DataFrame({f'{yaxis_title}': y})
            df_dict = df.to_dict(orient='list')
            df_dict['plot_type'] = 'histogram'
            df_dict['plot_type_id'] = plot_type_id
            df_dict['plot_id'] = plot_id
            json_list.append(df_dict)

            # 绘图代码
            # fig = px.histogram(data_frame=df, x=f'{yaxis_title}', nbins=3)
            # print('Output histogram')
            # fig.show()
            # fig.write_image(self.img_outputpath + 'histogram{}.png'.format(plot_type_id))

            plot_type_id += 1
            plot_id += 1
            return json_list, plot_id

        def plot(self):
            type_count = Counter(self.column_types)
            plot_types = self.rules['column{}'.format(self.df.shape[1])]['categorical{}'.format(type_count['categorical'])]
            # print('plot_types: ', plot_types)
            plot_id = 0
            json_list = []
            for plot_type in plot_types:
                if plot_type == 'scatter':
                    json_list, plot_id = self.scatter_plot(json_list.copy(), plot_id)

                if plot_type == 'line':
                    # 目前还没有设计折线图的画法，因为折线图涉及对x轴排序（升序降序），可能情况比较多。
                    pass

                if plot_type == 'bar':
                    json_list, plot_id = self.bar_chart(json_list.copy(), plot_id)

                if plot_type == 'pie':
                    json_list, plot_id = self.pie_chart(json_list.copy(), plot_id)

                if plot_type == 'histogram':
                    json_list, plot_id = self.histogram(json_list.copy(), plot_id)

            # with open(self.json_outputpath, 'w') as json_file:
            #     json_str = json.dumps(json_list, indent=4)
            #     json_file.write(json_str)
            print(json_list)

    data2visual = Data2Visual(img_outputpath, json_outputpath)
    data2visual.load_data(rows, column_names, column_types)
    data2visual.plot()


if __name__ == "__main__":
    main()