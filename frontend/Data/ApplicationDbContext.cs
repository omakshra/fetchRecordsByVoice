using Microsoft.EntityFrameworkCore;
using Frontend.Models; // If your models are in Frontend.Models

namespace Frontend.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options) { }

        public DbSet<Citizen> Citizens { get; set; }
        public DbSet<Criminal> Criminals { get; set; }
        public DbSet<Report> Reports { get; set; }
    }
}
