using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BusinessLogicLayer.DTO
{
    public class LandfillDto
    {
        public int Id { get; set; }
        public string LandfillId { get; set; }
        public string Status { get; set; } 
        public double Latitude { get; set; }
        public double Longitude { get; set; }
        public float? AreaM2 { get; set; }
        public float? VolumeM3 { get; set; }
        public float? WasteMassTons { get; set; }
        public int? StartYear { get; set; }
        public float? MethaneTonsPerYear { get; set; }
        public float? Co2eqTonsPerYear { get; set; }
    }
}
