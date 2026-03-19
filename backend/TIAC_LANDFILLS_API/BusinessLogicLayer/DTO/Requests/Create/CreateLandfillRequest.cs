using System.ComponentModel.DataAnnotations;
using DataAccessLayer.Common;

namespace BusinessLogicLayer.DTO.Requests.Create
{

    public class CreateLandfillRequest
    {
        [Required(ErrorMessage = "ID deponije je obavezan.")]
        [StringLength(50)]
        public string LandfillId { get; set; }

        [Required(ErrorMessage = "Status je obavezan.")]
        public LandfillStatus Status { get; set; }

        [Required(ErrorMessage = "Geografska širina je obavezna.")]
        [Range(-90, 90, ErrorMessage = "Geografska širina mora biti između -90 i 90.")]
        public double Latitude { get; set; }

        [Required(ErrorMessage = "Geografska dužina je obavezna.")]
        [Range(-180, 180, ErrorMessage = "Geografska dužina mora biti između -180 i 180.")]
        public double Longitude { get; set; }

        public float? AreaM2 { get; set; }
        public float? VolumeM3 { get; set; }
        public float? WasteMassTons { get; set; }
        public int? StartYear { get; set; }
        public float? MethaneTonsPerYear { get; set; }
        public float? Co2eqTonsPerYear { get; set; }
    }
}
