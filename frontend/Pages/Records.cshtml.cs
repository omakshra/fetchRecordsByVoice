using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Frontend.Models;
using Frontend.Data;
using Microsoft.EntityFrameworkCore;

namespace Frontend.Pages
{
    public class RecordsModel : PageModel
    {
        private readonly ApplicationDbContext _context;

        public RecordsModel(ApplicationDbContext context)
        {
            _context = context;
        }

        [BindProperty]
        public Citizen Citizen { get; set; }

        [BindProperty]
        public Criminal Criminal { get; set; }

        public List<Citizen> Citizens { get; set; }
        public List<Criminal> Criminals { get; set; }

        public async Task OnGetAsync()
        {
            Citizens = await _context.Citizens.ToListAsync();
            Criminals = await _context.Criminals.ToListAsync();
        }

        public async Task<IActionResult> OnPostAddCitizenAsync()
        {
            if (!ModelState.IsValid)
                return Page();

            _context.Citizens.Add(Citizen);
            await _context.SaveChangesAsync();
            return RedirectToPage();
        }

        public async Task<IActionResult> OnPostAddCriminalAsync()
        {
            if (!ModelState.IsValid)
                return Page();

            _context.Criminals.Add(Criminal);
            await _context.SaveChangesAsync();
            return RedirectToPage();
        }
    }
}
