package finki.dians.Controller;

import finki.dians.Model.Observation;
import finki.dians.Service.StockDataService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;


import java.util.List;

@RestController
public class FileController {

    @Autowired
    private final StockDataService stockDataService;

    public FileController(StockDataService stockDataService) {
        this.stockDataService = stockDataService;
    }

    @PostMapping
    public ResponseEntity<List<Observation>> filterData(
            @RequestParam
            String company,
            @RequestParam (required = false)
            @DateTimeFormat(pattern = "yyyy-MM-dd")
            LocalDate dateFrom,
            @RequestParam
            @DateTimeFormat(pattern = "yyyy-MM-dd")
            LocalDate dateTo
    ) {
        return ResponseEntity.ok(stockDataService.getRecordsFromTo(company, dateFrom, dateTo));
    }
}