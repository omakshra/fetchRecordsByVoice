using Microsoft.AspNetCore.Mvc;
using Frontend.Data;
using Frontend.Models;

public class ReportController : Controller
{
    private readonly ApplicationDbContext _context;

    public ReportController(ApplicationDbContext context)
    {
        _context = context;
    }

    [HttpPost]
    public IActionResult SubmitReport(Report report)
    {
        if (ModelState.IsValid)
        {
            _context.Reports.Add(report);
            _context.SaveChanges();
            return RedirectToAction("ReportSubmitted");
        }
        return View("Report", report);
    }

    public IActionResult ReportSubmitted()
    {
        return Content("Incident report submitted successfully.");
    }
}
