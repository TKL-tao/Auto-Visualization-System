package datainsights.web;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.reactive.function.client.WebClient;

import lombok.extern.slf4j.Slf4j;

import java.io.File;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.HashMap;
import java.util.Iterator;

import com.fasterxml.jackson.databind.ObjectMapper;

import datainsights.MyChart;
import datainsights.MyQuery;
import datainsights.data.MyQueryRepository;

import com.fasterxml.jackson.core.type.TypeReference;


@Controller
@RequestMapping("/autovisual")
// @Slf4j
public class autoVisualController {

    private MyQueryRepository myQueryRepository;
    // private MyChartRepository myChartRepository;

    public autoVisualController(MyQueryRepository myQueryRepository) {
        this.myQueryRepository = myQueryRepository;
        // this.myChartRepository = myChartRepository;
    }
    
    private final WebClient webClient = WebClient.create();

    @ModelAttribute(name = "myQuery")
    public MyQuery myQuery() {
        return new MyQuery();
    }

    // @ModelAttribute(name = "myChart")
    // public MyChart myChart() {
    //     return new MyChart();
    // }

    @GetMapping
    public String showQueryWindow() {
        return "autovisual";
    }

    @PostMapping
    public String processQuery(@ModelAttribute("myQuery") MyQuery myQuery, Model model) {  
        
        File folder = new File("src/main/java/datainsights/temp");
        File[] listOfFiles = folder.listFiles();
        if (listOfFiles != null && listOfFiles.length > 0) {
            myQuery.setDbName(listOfFiles[0].getName());
            myQuery.setDbPath(listOfFiles[0].getName());
        }
        System.out.println(myQuery.getDbName()); // myQuery.getDbName() has suffix of .sqlite
        // myQuery.setDbName(myQuery.getDbPath().substring(56));

        // save predicted sql and predicted chart pattern into ModelAttribute myQuery
        final String url = "http://127.0.0.1:5000/predict";
        Map<String, String> myRequest = new HashMap<>();
        myRequest.put("question", myQuery.getQuestion());
        myRequest.put("target_db_path", myQuery.getDbPath());
        try {
            Map response = webClient.post()
                                    .uri(url)
                                    .bodyValue(myRequest)
                                    .retrieve()
                                    .bodyToMono(Map.class)
                                    .block();
            if (response != null) {
                myQuery.setPredictedSQL((String) response.get("predicted_sql"));
                myQuery.setVisPattern(response.get("predicted_chart_pattern").toString());
            } else {
                System.out.println("Error: No response body");
            }
        } catch (Exception e) {
            System.out.println("Exception occurred: " + e.getMessage());
        }
        System.out.println(myQuery.getPredictedSQL() + "+++++++++++++++++++++++++++++++++++++------");

        // rule-based plotting
        try {
            // 定义Python程序的路径
            String pythonPath = "D:/Anaconda/envs/env_nl2sql/python.exe";
            String pythonScriptPath = "src/main/python/auto_visual_rule.py";
            // 创建ProcessBuilder实例来运行Python脚本
            ProcessBuilder processBuilder = new ProcessBuilder(pythonPath, pythonScriptPath, 
                                                            myQuery.getPredictedSQL(), "src/main/java/datainsights/temp/" + myQuery.getDbName());
            // 启动进程
            Process process = processBuilder.start();
            // 读取Python脚本的正常输出
            BufferedReader stdoutReader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            StringBuilder modeloutput = new StringBuilder();
            while ((line = stdoutReader.readLine()) != null) {
                modeloutput.append(line);
            }
            // 读取Python脚本的错误输出
            BufferedReader stderrReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
            StringBuilder errorOutput = new StringBuilder();
            while ((line = stderrReader.readLine()) != null) {
                errorOutput.append(line);
            }
            // 等待进程结束并获取退出码
            int exitCode = process.waitFor();
            if (exitCode == 0) {
                ObjectMapper objectMapper = new ObjectMapper();
                List<Map<String, Object>> list = objectMapper.readValue(modeloutput.toString().replace("'", "\""), new TypeReference<List<Map<String, Object>>>() {});
                System.out.println("完成json格式解析-------------------------");

                for (Map<String, Object> data : list) {
                    Iterator<Map.Entry<String, Object>> iterator = data.entrySet().iterator();
                    Map.Entry<String, Object> entry = iterator.next();

                    if (data.get("plot_type").equals("bar")) {
                        MyChart myChart = new MyChart();
                        myChart.setGraphType("bar");
                        String xLabel = entry.getKey();
                        List<String> xData = (List<String>) entry.getValue();
                        myChart.setXLabel(xLabel);myChart.setXValueString(xData);
                        if (iterator.hasNext()) {
                            entry = iterator.next();
                            String yLabel = entry.getKey();
                            // System.out.println("开始转化y轴的数据类型++++++++++++++++++++++++++++++++++++++++++++++++++++");
                            
                            // List<Double> yData = (List<Double>) entry.getValue();
                            List<Double> yData;
                            List<?> rawList = (List<?>) entry.getValue();
                            if (!rawList.isEmpty() && rawList.get(0) instanceof Integer) {
                                yData = rawList.stream()
                                            .map(item -> ((Integer) item).doubleValue())
                                            .collect(Collectors.toList());
                            } else {
                                yData = (List<Double>) rawList;
                            }
                            // System.out.println("y轴的数据类型转化完成++++++++++++++++++++++++++++++++++++++++++++++++++++");
                            myChart.setYLabel(yLabel);myChart.setYValue(yData);
                            // System.out.println("存入y轴的数据类型++++++++++++++++++++++++++++++++++++++++++++++++++++");
                        }
                        if (iterator.hasNext()) {
                            entry = iterator.next();
                            if (!entry.getKey().equals("plot_type")) {
                                List<String> groupValue = (List<String>) entry.getValue();
                                myChart.setGroupValue(groupValue);
                            }
                        }
                        // System.out.println("开始myQuery.addChart(myChart)++++++++++++++++++++++++++++++++++++++++++++++++++++");
                        myQuery.addChart(myChart);
                        // System.out.println("开始myQueryRepository.save(myQuery);++++++++++++++++++++++++++++++++++++++++++++++++++++");
                        // System.out.println(myQuery);
                        // myQueryRepository.save(myQuery);
                        // System.out.println("结束myQueryRepository.save(myQuery);++++++++++++++++++++++++++++++++++++++++++++++++++++");
                    } else if (data.get("plot_type").equals("scatter")) {
                        MyChart myChart = new MyChart();
                        myChart.setGraphType("scatter");
                        String xLabel = entry.getKey();
                        List<Double> xData = (List<Double>) entry.getValue();
                        myChart.setXLabel(xLabel);myChart.setXValueDouble(xData);
                        if (iterator.hasNext()) {
                            entry = iterator.next();
                            String yLabel = entry.getKey();
                            List<Double> yData = (List<Double>) entry.getValue();
                            myChart.setYLabel(yLabel);myChart.setYValue(yData);
                        }
                        if (iterator.hasNext()) {
                            entry = iterator.next();
                            if (!entry.getKey().equals("plot_type")) {
                                List<String> groupValue = (List<String>) entry.getValue();
                                myChart.setGroupValue(groupValue);
                            }
                        }
                        myQuery.addChart(myChart);
                        System.out.println(myQuery);
                        // myQueryRepository.save(myQuery);
                    } else if (data.get("plot_type").equals("pie")) {
                        MyChart myChart = new MyChart();
                        myChart.setGraphType("pie");
                        String xLabel = entry.getKey();
                        List<String> xData = (List<String>) entry.getValue();
                        myChart.setXLabel(xLabel);myChart.setXValueString(xData);
                        if (iterator.hasNext()) {
                            entry = iterator.next();
                            String yLabel = entry.getKey();

                            // List<Double> yData = (List<Double>) entry.getValue();
                            List<Double> yData;
                            List<?> rawList = (List<?>) entry.getValue();
                            if (!rawList.isEmpty() && rawList.get(0) instanceof Integer) {
                                yData = rawList.stream()
                                            .map(item -> ((Integer) item).doubleValue())
                                            .collect(Collectors.toList());
                            } else {
                                yData = (List<Double>) rawList;
                            }


                            myChart.setYLabel(yLabel);myChart.setYValue(yData);
                        }
                        myQuery.addChart(myChart);
                        System.out.println("pie图的query输出：");
                        System.out.println(myQuery);
                    }
                }
                myQueryRepository.save(myQuery);
                
            } else {
                // 处理错误情况，可能需要记录日志或返回错误信息
                System.err.println("Python script exited with error code: " + exitCode);
                System.err.println("Error Output: " + errorOutput.toString());
            }
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
        
        // auto-visualizaiton based plotting
        try {
            // 定义Python程序的路径
            String pythonPath = "D:/Anaconda/envs/env_nl2sql/python.exe";
            String pythonScriptPath = "src/main/python/get_chart_info.py";
            // String nl2visDic = "{'chart': 'bar', 'x_name': 'city', 'y_name': 'avg(lat)', 'grouping_name': 'None'}";
            // System.out.println("My Predicted VIS Partten is: " + myQuery.getVisPattern());
            // System.out.println("My truth VIS Partten is: " + nl2visDic);
            // // 创建ProcessBuilder实例来运行Python脚本
            ProcessBuilder processBuilder = new ProcessBuilder(pythonPath, pythonScriptPath, 
                                                            myQuery.getPredictedSQL(), "src/main/java/datainsights/temp/" + myQuery.getDbName(), myQuery.getVisPattern());
            // ProcessBuilder processBuilder = new ProcessBuilder(pythonPath, pythonScriptPath, 
            //                                                  myQuery.getQuestion(), myQuery.getDbPath());
            // 启动进程
            Process process = processBuilder.start();
            // 读取Python脚本的正常输出
            BufferedReader stdoutReader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            StringBuilder modeloutput = new StringBuilder();
            while ((line = stdoutReader.readLine()) != null) {
                modeloutput.append(line);
            }
            // 读取Python脚本的错误输出
            BufferedReader stderrReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
            StringBuilder errorOutput = new StringBuilder();
            while ((line = stderrReader.readLine()) != null) {
                errorOutput.append(line);
            }
            // 等待进程结束并获取退出码
            int exitCode = process.waitFor();
            if (exitCode == 0) {
                String jsonResponse = modeloutput.toString();
                ObjectMapper objectMapper = new ObjectMapper();
                Map<String, Object> responseMap = objectMapper.readValue(jsonResponse, new TypeReference<HashMap<String, Object>>() {});
                System.out.println("完成推荐图的json格式解析-------------------------");
                System.out.println(jsonResponse);
                if (responseMap.get("chart").equals("bar")) {
                    MyChart myChart = new MyChart();
                    myChart.setGraphType("bar"); myChart.setSuggested(true);
                    System.out.println();
                    String xLabel = (String) responseMap.get("x_name");
                    List<String> xData = (List<String>) responseMap.get("x_data");
                    myChart.setXLabel(xLabel);myChart.setXValueString(xData);

                    String yLabel = (String) responseMap.get("y_name");
                    // List<Double> yData = (List<Double>) responseMap.get("y_data");
                    List<Double> yData;
                    List<?> rawList = (List<?>) responseMap.get("y_data");
                    if (!rawList.isEmpty() && rawList.get(0) instanceof Integer) {
                        yData = rawList.stream()
                                    .map(item -> ((Integer) item).doubleValue())
                                    .collect(Collectors.toList());
                    } else {
                        yData = (List<Double>) rawList;
                    }
                    myChart.setYLabel(yLabel);myChart.setYValue(yData);

                    String groupLabel = (String) responseMap.get("grouping_name");
                    List<String> groupValue = (List<String>) responseMap.get("grouping_data");

                    myQuery.addChart(myChart);
                } else if (responseMap.get("chart").equals("scatter")) {
                    MyChart myChart = new MyChart();
                    myChart.setGraphType("scatter"); myChart.setSuggested(true);
                    String xLabel = (String) responseMap.get("x_name");
                    List<Double> xData = (List<Double>) responseMap.get("x_data");
                    myChart.setXLabel(xLabel);myChart.setXValueDouble(xData);

                    String yLabel = (String) responseMap.get("y_name");
                    List<Double> yData;
                    List<?> rawList = (List<?>) responseMap.get("y_data");
                    if (!rawList.isEmpty() && rawList.get(0) instanceof Integer) {
                        yData = rawList.stream()
                                    .map(item -> ((Integer) item).doubleValue())
                                    .collect(Collectors.toList());
                    } else {
                        yData = (List<Double>) rawList;
                    }
                    myChart.setYLabel(yLabel);myChart.setYValue(yData);

                    String groupLabel = (String) responseMap.get("grouping_name");
                    List<String> groupValue = (List<String>) responseMap.get("grouping_data");

                    myQuery.addChart(myChart);
                } else if (responseMap.get("chart").equals("pie")) {
                    MyChart myChart = new MyChart();
                    myChart.setGraphType("pie"); myChart.setSuggested(true);
                    String xLabel = (String) responseMap.get("x_name");
                    // System.out.println("Predicted Chart Pie is " + (List<String>) responseMap.get("x_data"));
                    // 如果responseMap.get("x_data"))是一个List<char>，好像不能被强制转化为List<String>，这个问题后面需要解决
                    List<String> xData = (List<String>) responseMap.get("x_data");
                    myChart.setXLabel(xLabel);myChart.setXValueString(xData);

                    String yLabel = (String) responseMap.get("y_name");
                    // List<Double> yData = (List<Double>) responseMap.get("y_data");
                    List<Double> yData;
                    List<?> rawList = (List<?>) responseMap.get("y_data");
                    if (!rawList.isEmpty() && rawList.get(0) instanceof Integer) {
                        yData = rawList.stream()
                                    .map(item -> ((Integer) item).doubleValue())
                                    .collect(Collectors.toList());
                    } else {
                        yData = (List<Double>) rawList;
                    }
                    myChart.setYLabel(yLabel);myChart.setYValue(yData);

                    // String groupLabel = (String) responseMap.get("grouping_name");
                    // List<String> groupValue = (List<String>) responseMap.get("grouping_data");

                    myQuery.addChart(myChart);
                    System.out.println("Predicted Chart Pie is " + myQuery);
                } else if (responseMap.get("chart").equals("line")) {
                    MyChart myChart = new MyChart();
                    myChart.setGraphType("line"); myChart.setSuggested(true);
                    String xLabel = (String) responseMap.get("x_name");
                    List<Double> xData = (List<Double>) responseMap.get("x_data");
                    myChart.setXLabel(xLabel);myChart.setXValueDouble(xData);

                    String yLabel = (String) responseMap.get("y_name");
                    List<Double> yData;
                    List<?> rawList = (List<?>) responseMap.get("y_data");
                    if (!rawList.isEmpty() && rawList.get(0) instanceof Integer) {
                        yData = rawList.stream()
                                    .map(item -> ((Integer) item).doubleValue())
                                    .collect(Collectors.toList());
                    } else {
                        yData = (List<Double>) rawList;
                    }
                    myChart.setYLabel(yLabel);myChart.setYValue(yData);

                    String groupLabel = (String) responseMap.get("grouping_name");
                    List<String> groupValue = (List<String>) responseMap.get("grouping_data");

                    myQuery.addChart(myChart);
                }
                myQueryRepository.save(myQuery);
            }else {
                // 处理错误情况，可能需要记录日志或返回错误信息
                System.err.println("Python script exited with error code: " + exitCode);
                System.err.println("Error Output: " + errorOutput.toString());
            }
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
        model.addAttribute("myQuery", myQuery);
        System.out.println(myQuery);
        return "autovisual";
    }
    
}