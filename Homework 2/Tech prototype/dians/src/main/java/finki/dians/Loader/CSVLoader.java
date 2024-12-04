package finki.dians.Loader;

import finki.dians.Model.Observation;
import finki.dians.Repository.StockDataRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.text.NumberFormat;
import java.time.LocalDate;
import java.util.Locale;

@Service
public class CSVLoader {

    @Autowired
    private StockDataRepository repository;

/*    public void loadCSV(String companyName) throws IOException {
        String filePath = System.getProperty("${database.data.path}") + companyName + ".csv";

        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            boolean isHeader = true;

            while ((line = br.readLine()) != null) {
                if (isHeader) {
                    isHeader = false;
                    continue; // Skip header row
                }

                try {
                    String[] data = line.split(",");

                    // Parse data
                    LocalDate date = LocalDate.parse(data[0]);
                    double open = parseNumericValue(data[1]);
                    double high = parseNumericValue(data[2]);
                    double low = parseNumericValue(data[3]);
                    double close = parseNumericValue(data[4]);
                    double adjustedClose = parseNumericValue(data[5]);
                    Double volume = Double.valueOf(parseIntValue(data[6]));
                    if (volume == null) volume = (double) 0; // Handle null volume gracefully
                    double changePercent = parseNumericValue(data[7]);
                    double otherMetric = parseNumericValue(data[8]);

                    // Create StockData object
                    Observation stock = new Observation(date, open, high, low, close, adjustedClose, volume, changePercent, otherMetric);

                    // Save to repository
                    repository.save(companyName, stock);

                } catch (Exception e) {
                    System.err.println("Error processing line: " + line);
                    e.printStackTrace();
                }
            }
        }
    }*/

    private double parseNumericValue(String value) {
        try {
            if (value == null || value.trim().isEmpty()) {
                return Double.NaN;
            }
            value = value.replace(",", "").replace("\"", "").replace(" ", "");
            return Double.parseDouble(value);
        } catch (NumberFormatException e) {
            return Double.NaN; // Default to NaN for invalid numbers
        }
    }

    private Integer parseIntValue(String value) {
        try {
            if (value == null || value.trim().isEmpty()) {
                return null; // Return null for missing or invalid integers
            }
            value = value.replace(",", "").replace("\"", "").replace(" ", "");
            return Integer.parseInt(value);
        } catch (NumberFormatException e) {
            return null; // Return null for invalid integers
        }
    }
}
