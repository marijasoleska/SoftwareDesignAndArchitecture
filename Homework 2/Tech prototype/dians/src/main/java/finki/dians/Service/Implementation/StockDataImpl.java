package finki.dians.Service.Implementation;

import finki.dians.Model.Observation;
import finki.dians.Repository.StockDataRepository;
import finki.dians.Service.StockDataService;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

@Service
public class StockDataImpl implements StockDataService {

    private final StockDataRepository stockDataRepository;

    public StockDataImpl(StockDataRepository stockDataRepository) {
        this.stockDataRepository = stockDataRepository;
    }

    @Override
    public List<Observation> getRecordsFromTo(String company, LocalDate from, LocalDate to) {
        return stockDataRepository.getRecordsFromTo(company,from, to);
    }

    @Override
    public List<String> listCompanies() {
        return stockDataRepository.listCompanies();
    }
}
