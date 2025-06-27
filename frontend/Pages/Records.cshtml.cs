using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.EntityFrameworkCore;
using Frontend.Models;
using Frontend.Data;
using Microsoft.AspNetCore.Mvc.ModelBinding.Validation;

namespace Frontend.Pages
{
    public class RecordsModel : PageModel
    {
        private readonly ApplicationDbContext _context;

        public RecordsModel(ApplicationDbContext context)
        {
            _context = context;
        }

        // REMOVE BindProperty attributes
        public Citizen Citizen { get; set; } = new();
        public Criminal Criminal { get; set; } = new();


        public List<Citizen> Citizens { get; set; } = new();
        public List<Criminal> Criminals { get; set; } = new();

        public async Task OnGetAsync()
        {
            Citizens = await _context.Citizens.ToListAsync();
            Criminals = await _context.Criminals.ToListAsync();
        }

        public async Task<IActionResult> OnPostAddCitizenAsync()
        {
            Console.WriteLine("➡️ AddCitizen handler triggered");

            var citizen = new Citizen();
            bool isUpdated = await TryUpdateModelAsync(citizen, "Citizen");

            if (!isUpdated || !ModelState.IsValid)
            {
                LogModelErrors();
                return Page();
            }

            _context.Citizens.Add(citizen);
            await _context.SaveChangesAsync();

            Console.WriteLine($"✅ Citizen saved: {citizen.Name}");

            return RedirectToPage(new { tab = "citizen" });

        }


        public async Task<IActionResult> OnPostAddCriminalAsync()
        {
            Console.WriteLine("➡️ AddCriminal handler triggered");

            var criminal = new Criminal();
            bool isUpdated = await TryUpdateModelAsync(criminal, "Criminal");

            if (!isUpdated || !ModelState.IsValid)
            {
                LogModelErrors();
                return Page();
            }

            _context.Criminals.Add(criminal);
            await _context.SaveChangesAsync();

            Console.WriteLine($"✅ Criminal saved: {criminal.Name}");

            return RedirectToPage(new { tab = "criminal" });

        }

        private void RemoveModelStateKeysStartingWith(string prefix)
        {
            var keysToRemove = ModelState.Keys.Where(k => k.StartsWith(prefix + ".", System.StringComparison.OrdinalIgnoreCase)).ToList();
            foreach (var key in keysToRemove)
            {
                ModelState.Remove(key);
            }
        }
        private void LogModelErrors()
        {
            foreach (var entry in ModelState)
            {
                foreach (var error in entry.Value.Errors)
                {
                    Console.WriteLine($"validation error on {entry.Key}: {error.ErrorMessage}");
                }
            }
            Console.WriteLine("❌ Invalid model");
        }
        public async Task<JsonResult> OnGetSearchCitizensAsync(string? query, string? name, string? age, string? address, string? governmentId)
        {
            IQueryable<Citizen> queryable = _context.Citizens;

            bool usedSpecificFilters = false;

            if (!string.IsNullOrWhiteSpace(name))
            {
                queryable = queryable.Where(c => EF.Functions.Like(c.Name, $"%{name}%"));
                usedSpecificFilters = true;
            }

            if (!string.IsNullOrWhiteSpace(age) && int.TryParse(age, out int ageValue))
            {
                queryable = queryable.Where(c => c.Age == ageValue);
                usedSpecificFilters = true;
            }

            if (!string.IsNullOrWhiteSpace(address))
            {
                queryable = queryable.Where(c => EF.Functions.Like(c.Address, $"%{address}%"));
                usedSpecificFilters = true;
            }

            if (!string.IsNullOrWhiteSpace(governmentId))
            {
                queryable = queryable.Where(c => c.GovernmentId == governmentId);
                usedSpecificFilters = true;
            }

            // Only use fallback `query` if no specific filters are provided
            if (!usedSpecificFilters && !string.IsNullOrWhiteSpace(query))
            {
                queryable = queryable.Where(c =>
                    EF.Functions.Like(c.Name, $"%{query}%") ||
                    EF.Functions.Like(c.GovernmentId, $"%{query}%") ||
                    EF.Functions.Like(c.Address, $"%{query}%") ||
                    c.Age.ToString() == query);
            }

            var results = await queryable.ToListAsync();
            return new JsonResult(results);
        }


        public async Task<JsonResult> OnGetSearchCriminalsAsync(
    string? query,
    string? name,
    string? crime,
    string? governmentId,
    string? dateArrested)
        {
            IQueryable<Criminal> queryable = _context.Criminals;
            bool usedSpecificFilters = false;

            if (!string.IsNullOrWhiteSpace(name))
            {
                queryable = queryable.Where(c => EF.Functions.Like(c.Name, $"%{name}%"));
                usedSpecificFilters = true;
            }

            if (!string.IsNullOrWhiteSpace(crime))
            {
                queryable = queryable.Where(c => EF.Functions.Like(c.Crime, $"%{crime}%"));
                usedSpecificFilters = true;
            }

            if (!string.IsNullOrWhiteSpace(governmentId))
            {
                queryable = queryable.Where(c => c.GovernmentId == governmentId);
                usedSpecificFilters = true;
            }

            if (!string.IsNullOrWhiteSpace(dateArrested) &&
                DateTime.TryParse(dateArrested, out DateTime parsedDate))
            {
                queryable = queryable.Where(c => c.DateArrested.Date == parsedDate.Date);
                usedSpecificFilters = true;
            }

            if (!usedSpecificFilters && !string.IsNullOrWhiteSpace(query))
            {
                queryable = queryable.Where(c =>
                    EF.Functions.Like(c.Name, $"%{query}%") ||
                    EF.Functions.Like(c.Crime, $"%{query}%") ||
                    EF.Functions.Like(c.GovernmentId, $"%{query}%") ||
                    EF.Functions.Like(c.DateArrested.ToString(), $"%{query}%"));
            }

            var results = await queryable.ToListAsync();
            return new JsonResult(results);
        }


    }
}
