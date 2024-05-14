package datainsights.data;

// import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.PagingAndSortingRepository;

import datainsights.MyChart;
import datainsights.MyQuery;

import org.springframework.data.jpa.repository.Query;
import org.springframework.data.domain.Pageable;



import java.util.List;

public interface MyQueryRepository extends PagingAndSortingRepository<MyQuery, Long> {
    @Query("SELECT q.charts FROM MyQuery q WHERE q.id = (SELECT MAX(mq.id) FROM MyQuery mq)")
    List<MyChart> findAllMyCharts();

    @Query("SELECT m.predictedSQL FROM MyQuery m ORDER BY m.id DESC")
    List<String> findLastPredictedSQL(Pageable pageable);

    @Query("SELECT m.dbPath FROM MyQuery m ORDER BY m.id DESC")
    List<String> findLastMyDBpath(Pageable pageable);
}