package finki.dians.Service;

import finki.dians.Model.Observation;
import finki.dians.Repository.StockDataRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.chrono.ChronoLocalDate;
import java.util.List;

@Service
public interface StockDataService {

    List<Observation> getRecordsFromTo(String company, LocalDate from, LocalDate to);
    List<String> listCompanies();

}
