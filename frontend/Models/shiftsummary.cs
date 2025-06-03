using System;
using System.ComponentModel.DataAnnotations;

namespace Frontend.Models
{
    public class ShiftSummary
    {
        public int Id { get; set; }

        [Required]
        public string OfficerName { get; set; }

        [Required]
        public DateTime ShiftStart { get; set; }

        [Required]
        public DateTime ShiftEnd { get; set; }

        [Required]
        public string SummaryText { get; set; }
    }
}
