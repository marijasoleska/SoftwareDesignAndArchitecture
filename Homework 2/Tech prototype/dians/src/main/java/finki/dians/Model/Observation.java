package finki.dians.Model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.Getter;
import lombok.Setter;

import java.text.NumberFormat;
import java.time.LocalDate;
import java.util.Locale;

@Data
@Getter
@Setter
public class Observation implements Comparable<Observation> {

    private final LocalDate date;
    private final Double lastTradePrice;
    private final Double max;
    private final Double min;
    private final Double avgPrice;
    private final Double chg;
    private final Long volume;
    private final Long turnoverBestMKD;
    private final Long totalTurnoverMKD;

    private static NumberFormat format = NumberFormat.getInstance(Locale.ITALY);

    public Observation(LocalDate date, Double lastTradePrice, Double max, Double min, Double avgPrice, Double chg, Long volume, Long turnoverBestMKD, Long totalTurnoverMKD) {
        this.date = date;
        this.lastTradePrice = lastTradePrice;
        this.max = max;
        this.min = min;
        this.avgPrice = avgPrice;
        this.chg = chg;
        this.volume = volume;
        this.turnoverBestMKD = turnoverBestMKD;
        this.totalTurnoverMKD = totalTurnoverMKD;
    }

    public LocalDate getDate() {
        return date;
    }

    public Double getLastTradePrice() {
        return lastTradePrice;
    }

    public Double getMax() {
        return max;
    }

    public Double getMin() {
        return min;
    }

    public Double getAvgPrice() {
        return avgPrice;
    }

    public Double getChg() {
        return chg;
    }

    public Long getVolume() {
        return volume;
    }

    public Long getTurnoverBestMKD() {
        return turnoverBestMKD;
    }

    public Long getTotalTurnoverMKD() {
        return totalTurnoverMKD;
    }

    public static NumberFormat getFormat() {
        return format;
    }

    public static void setFormat(NumberFormat format) {
        Observation.format = format;
    }

    @Override
    public int compareTo(Observation o) {
        return date.compareTo(o.date);
    }

    @Override
    public String toString() {
        return "Observation{" +
                "date=" + date +
                ", lastTradePrice=" + lastTradePrice +
                ", max=" + (max == null ? "" : max) +
                ", min=" + (min == null ? "" : min) +
                ", avgPrice=" + avgPrice +
                ", chg=" + chg +
                ", volume=" + volume +
                ", turnoverBestMKD=" + turnoverBestMKD +
                ", totalTurnoverMKD=" + totalTurnoverMKD +
                '}';
    }

    public String getFormattedNum(Object num) {
        if (num == null) {
            return "";
        }
        Number n = (Number) num;
        return format.format(n);
    }
}
