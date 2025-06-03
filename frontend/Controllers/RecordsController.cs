using Microsoft.AspNetCore.Mvc;
using Frontend.Data;
using Frontend.Models;

public class RecordsController : Controller
{
    private readonly ApplicationDbContext _context;

    public RecordsController(ApplicationDbContext context)
    {
        _context = context;
    }

    [HttpPost]
    public IActionResult AddCitizen(Citizen citizen)
    {
        if (ModelState.IsValid)
        {
            _context.Citizens.Add(citizen);
            _context.SaveChanges();
            return RedirectToAction("CitizenAdded");
        }
        return View("Records", citizen);
    }

    public IActionResult CitizenAdded()
    {
        return Content("Citizen added successfully.");
    }
}

[HttpPost]
public IActionResult AddCriminal(Criminal criminal)
{
    if (ModelState.IsValid)
    {
        _context.Criminals.Add(criminal);
        _context.SaveChanges();
        return RedirectToAction("CriminalAdded");
    }
    return View("Records", criminal);
}

public IActionResult CriminalAdded()
{
    return Content("Criminal added successfully.");
}
