package datainsights;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.OneToMany;
import javax.persistence.CascadeType;

import lombok.Data;

import java.util.List;
import java.util.ArrayList;

@Data
@Entity
public class MyQuery {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;
    
    private String question;
    private String predictedSQL;
    private String visPattern;
    private String dbPath;

    private String dbName;

    @OneToMany(targetEntity=MyChart.class, cascade = CascadeType.ALL)
    private List<MyChart> charts = new ArrayList<>();;

    public void addChart(MyChart myChart) {
        this.charts.add(myChart);
    }
}