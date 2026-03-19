using DataAccessLayer.Common;
using NetTopologySuite.Geometries; 
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

[Table("landfills")] 
public class LandfillEntity
{
    [Key]
    [Column("id")]
    public int Id { get; set; }

    [Required]
    [StringLength(50)]
    [Column("landfill_id")]
    public string LandfillId { get; set; }

    [Required]
    [Column("status", TypeName = "landfill_status")] 
    public LandfillStatus Status { get; set; }

    [Required]
    [Column("location", TypeName = "geometry (point, 4326)")]
    public Point Location { get; set; }

    [Column("area_m2")]
    public float? AreaM2 { get; set; }

    [Column("volume_m3")]
    public float? VolumeM3 { get; set; }

    [Column("waste_mass_tons")]
    public float? WasteMassTons { get; set; }

    [Column("start_year")]
    public int? StartYear { get; set; }

    [Column("methane_tons_per_year")]
    public float? MethaneTonsPerYear { get; set; }

    [Column("co2eq_tons_per_year")]
    public float? Co2eqTonsPerYear { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; }
}