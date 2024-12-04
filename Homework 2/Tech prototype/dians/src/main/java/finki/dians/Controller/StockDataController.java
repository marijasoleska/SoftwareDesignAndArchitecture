package finki.dians.Controller;

import finki.dians.Model.Observation;
import finki.dians.Service.StockDataService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/stocks")
public class StockDataController {

    @Autowired

    private final StockDataService stockDataService;

    public StockDataController(StockDataService stockDataService) {
        this.stockDataService = stockDataService;
    }

    @GetMapping
    @SuppressWarnings("unchecked")
    public String getStockVisualPage(HttpServletRequest request,
                                     @RequestParam(required = false) String company,
                                     @RequestParam(required = false) String dateFrom,
                                     @RequestParam(required = false) String dateTo,
                                     Model model) {
        model.addAttribute("companies", stockDataService.listCompanies());
        List<Observation> observations = (List<Observation>) request.getSession().getAttribute("observationsPresent");

        if (observations != null) {
            model.addAttribute("observations", observations);
        }
        if (dateFrom != null && dateTo != null && company != null)  {
            model.addAttribute("dateFrom", dateFrom);
            model.addAttribute("company", company);
            model.addAttribute("dateTo", dateTo);
        }

        return "api/stocks";
    }

    @PostMapping
    public String filterData(
            HttpServletRequest request,
            @RequestParam String company,
            @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd") LocalDate dateFrom,
            @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd") LocalDate dateTo
    ) {
        List<Observation> observationList = stockDataService.getRecordsFromTo(company, dateFrom, dateTo);
        HttpSession session = request.getSession();

        session.setAttribute("observationsPresent", observationList);

        return String.format("redirect:/api/stocks?company=%s&dateFrom=%s&dateTo=%s",company, dateFrom, dateTo);
    }
}