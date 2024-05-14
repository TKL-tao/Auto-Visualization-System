package datainsights.web.api;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import datainsights.MyChart;
import datainsights.MyQuery;
import datainsights.data.MyQueryRepository;

import org.springframework.core.io.InputStreamResource;
import org.springframework.core.io.Resource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;

import java.util.List;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;

@RestController
@RequestMapping(path = "/api/plot_data", produces = "application/json")
public class PlotController {

    private MyQueryRepository myQueryRepository;

    public PlotController(MyQueryRepository myQueryRepository) {
        this.myQueryRepository = myQueryRepository;
    }

    @GetMapping(params = "plot")
    public List<MyChart> getChartData() {
        System.out.println("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++");
        System.out.println(myQueryRepository.findAllMyCharts());
        return myQueryRepository.findAllMyCharts();
    }

    @GetMapping(params = "csv")
    public ResponseEntity<Resource> generateCsv() throws IOException, InterruptedException {
        // 构建Python脚本命令
        String pythonPath = "D:/Anaconda/envs/env_nl2sql/python.exe";
        String pythonScriptPath = "src/main/python/output_csv.py";
        Pageable pageable = PageRequest.of(0, 1);
        System.out.println("+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+");
        System.out.println("D:/NL2SQL/Data"+myQueryRepository.findLastMyDBpath(pageable).get(0).substring(35));
        ProcessBuilder processBuilder = new ProcessBuilder(pythonPath, pythonScriptPath, 
            myQueryRepository.findLastPredictedSQL(pageable).get(0),
            "D:/NL2SQL/Data"+myQueryRepository.findLastMyDBpath(pageable).get(0).substring(35));

        Process process = processBuilder.start();
        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new RuntimeException("执行Python脚本时出错");
        }

        // 读取生成的CSV文件
        String csvFilename = "queried_results.csv";
        File csvFile = new File("src/main/python/output_files", csvFilename);
        InputStreamResource resource = new InputStreamResource(new FileInputStream(csvFile));

        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType("text/csv"))
                .header("Content-Disposition", "attachment; filename=\"" + csvFilename + "\"")
                .body(resource);
    }

    // @GetMapping(params = "recent")
    // public Iterable<MyQuery> recentCharts() {
    //     PageRequest page = PageRequest.of(0, 12, Sort.by("createdAt").descending());
    //     return myQueryRepository.findAll(page).getContent();
    // }
    
}