namespace Frontend.Models
{
    public class Criminal
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Crime { get; set; }
        public DateTime DateArrested { get; set; }
        public string GovernmentId { get; set; }
    }
}