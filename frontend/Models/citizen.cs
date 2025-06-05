using System.ComponentModel.DataAnnotations;

namespace Frontend.Models
{
    public class Citizen
    {
        public int Id { get; set; }

        [Required(ErrorMessage = "Name is required")]
        public string Name { get; set; } = string.Empty;

        [Range(1, 150, ErrorMessage = "Age must be between 1 and 150")]
        public int Age { get; set; }

        [Required(ErrorMessage = "Address is required")]
        public string Address { get; set; } = string.Empty;

        [Required(ErrorMessage = "Government ID is required")]
        public string GovernmentId { get; set; } = string.Empty;
    }
}
