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
        public async Task<JsonResult> OnGetSearchCitizensAsync(string query)
        {
            if (string.IsNullOrWhiteSpace(query))
            {
                // Return all citizens if query is empty
                var allCitizens = await _context.Citizens.ToListAsync();
                return new JsonResult(allCitizens);
            }
            else
            {
                var results = await _context.Citizens
                    .Where(c => c.Name.Contains(query) || c.GovernmentId.Contains(query))
                    .ToListAsync();
                return new JsonResult(results);
            }
        }

        public async Task<JsonResult> OnGetSearchCriminalsAsync(string query)
        {
            if (string.IsNullOrWhiteSpace(query))
            {
                var allCriminals = await _context.Criminals.ToListAsync();
                return new JsonResult(allCriminals);
            }
            else
            {
                var results = await _context.Criminals
                    .Where(c => c.Name.Contains(query) || c.GovernmentId.Contains(query))
                    .ToListAsync();
                return new JsonResult(results);
            }
        }


    }
}
