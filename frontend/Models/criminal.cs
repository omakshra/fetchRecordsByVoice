using System;
using System.ComponentModel.DataAnnotations;

namespace Frontend.Models
{
    public class Criminal
    {
        public int Id { get; set; }

        [Required(ErrorMessage = "Name is required")]
        public string Name { get; set; } = string.Empty;

        [Required(ErrorMessage = "Crime is required")]
        public string Crime { get; set; } = string.Empty;

        [Required(ErrorMessage = "Date Arrested is required")]
        public DateTime DateArrested { get; set; }

        [Required(ErrorMessage = "Government ID is required")]
        public string GovernmentId { get; set; } = string.Empty;
    }
}
