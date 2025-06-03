using System;
using System.ComponentModel.DataAnnotations;

namespace Frontend.Models
{
    public class Report
    {
        public int Id { get; set; }

        [Required]
        public DateTime DateTime { get; set; }

        [Required]
        public string OfficerName { get; set; }

        [Required]
        public string Location { get; set; }

        public string InvolvedPersons { get; set; }

        [Required]
        public string Description { get; set; }
    }
}
