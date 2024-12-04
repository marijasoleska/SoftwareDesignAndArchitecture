package finki.dians.Repository;

import jakarta.annotation.PostConstruct;
import finki.dians.Model.Observation;
import lombok.Getter;
import lombok.Setter;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Repository;

import java.io.FileReader;
import java.io.IOException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.text.NumberFormat;
import java.text.ParseException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;

@Getter
@Setter
@Repository
public class StockDataRepository {

    @Value("${database.data.path}")
    private String dbPath;

    private final Map<String, List<Observation>> companies;

    public StockDataRepository() {
        companies = new HashMap<>();

    }

    @PostConstruct
    public void update()  {
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(Paths.get(dbPath))) {
            for (Path companyCSV : stream) {

                List<List<String>> companyData = readCSV(companyCSV.toString());
                companyData = companyData.subList(1, companyData.size());

                String companyName = companyCSV.toString().split("\\\\")[4].split("\\.")[0];

                List<Observation> observations = companyData.stream()
                        .map(this::createObservation)
                        .filter(Optional::isPresent)
                        .map(Optional::get)
                        .toList();

                companies.put(companyName, observations);
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

    }

    public List<Observation> getRecordsFromTo(String company, LocalDate from, LocalDate to) {
        return companies.get(company)
                .stream()
                .filter(obs -> obs.getDate().isBefore(to.plusDays(1))
                        &&
                        obs.getDate().isAfter(from.minusDays(1)))
                .sorted()
                .toList();
    }

    public List<String> listCompanies() {
        return companies.keySet()
                .stream()
                .sorted(Comparator.naturalOrder())
                .toList();
    }


    private List<List<String>> readCSV(String company) {
        List<List<String>> records = new ArrayList<>();
        try {

            FileReader reader = new FileReader(String.format("%s", company));
            CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT);

            for (CSVRecord csvRecord : csvParser) {
                List<String> row = new ArrayList<>();
                csvRecord.forEach(row::add);
                records.add(row);
            }

        } catch (IOException e) {
            e.printStackTrace();
        }

        return records;
    }

    private Optional<Observation> createObservation(List<String> ls) {


        DateTimeFormatter dtf = DateTimeFormatter.ofPattern("MM/dd/yyyy");
        NumberFormat numFormat = NumberFormat.getInstance(Locale.ITALY);

        Optional<Observation> retval = Optional.empty();

        try {
            LocalDate date = LocalDate.parse(ls.get(0), dtf);
            Double lastTrade = !ls.get(1).trim().isEmpty() ? numFormat.parse(ls.get(1)).doubleValue() : null;
            Double max = !ls.get(2).trim().isEmpty() ? numFormat.parse(ls.get(2)).doubleValue() : null;
            Double min = !ls.get(3).trim().isEmpty() ? numFormat.parse(ls.get(3)).doubleValue() : null;
            Double avgPrice = !ls.get(4).trim().isEmpty() ? numFormat.parse(ls.get(4)).doubleValue() : null;
            Double chg = !ls.get(5).trim().isEmpty() ? numFormat.parse(ls.get(5)).doubleValue() : null;
            Long volume = !ls.get(6).trim().isEmpty() ? numFormat.parse(ls.get(6)).longValue() : null;
            Long turnoverBestMKD = !ls.get(7).trim().isEmpty() ? numFormat.parse(ls.get(7)).longValue() : null;
            Long totalTurnoverMKD = !ls.get(8).trim().isEmpty() ? numFormat.parse(ls.get(8)).longValue() : null;

            retval = Optional.of(new Observation(date, lastTrade, max, min, avgPrice, chg, volume, turnoverBestMKD, totalTurnoverMKD));
        } catch (ParseException exception) {
            System.err.println(exception.getMessage());
        }

        return retval;
    }
}
