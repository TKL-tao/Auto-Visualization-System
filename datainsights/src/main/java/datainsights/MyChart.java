package datainsights;

import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.ElementCollection;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;

import lombok.Data;

import java.util.List;

@Data
@Entity
public class MyChart {
    
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;

    private String graphType;

    private boolean isSuggested = false;

    @ElementCollection
    private List<String> xValueString;

    @ElementCollection
    private List<Double> xValueDouble;
    private String xLabel;

    @ElementCollection
    private List<Double> yValue;
    private String yLabel;

    @ElementCollection
    private List<String> groupValue;
    private String groupLabel;
}