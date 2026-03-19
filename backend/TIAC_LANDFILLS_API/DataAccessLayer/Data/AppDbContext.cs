using DataAccessLayer.Common;
using Microsoft.EntityFrameworkCore;
using NetTopologySuite;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DataAccessLayer.Data
{
    public class AppDbContext : DbContext
    {
        public DbSet<LandfillEntity> Landfills { get; set; }

        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            
            modelBuilder.HasPostgresExtension("postgis");

            modelBuilder.HasPostgresEnum<LandfillStatus>();

            base.OnModelCreating(modelBuilder);
        }
    }
}
