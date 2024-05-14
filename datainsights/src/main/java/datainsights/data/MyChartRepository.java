package datainsights.data;

import org.springframework.data.repository.CrudRepository;

import datainsights.MyChart;

public interface MyChartRepository extends CrudRepository<MyChart, Long>{
    
    
}