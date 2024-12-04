package finki.dians.Service.Implementation;

import finki.dians.Repository.StockDataRepository;
import finki.dians.Service.RefreshService;
import org.springframework.stereotype.Service;

import java.text.ParseException;

@Service
public class RefreshImpl implements RefreshService {

    private final StockDataRepository stockDataRepository;

    public RefreshImpl(StockDataRepository stockDataRepository) {
        this.stockDataRepository = stockDataRepository;
    }

    @Override
    public void refreshDatabase() {
        this.stockDataRepository.update();
    }

}
