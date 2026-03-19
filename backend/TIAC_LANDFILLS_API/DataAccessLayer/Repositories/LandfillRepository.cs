using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using DataAccessLayer.Common.Interface;
using Microsoft.EntityFrameworkCore;
using NetTopologySuite.Geometries;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using DataAccessLayer.Data;

namespace DataAccessLayer.Repositories
{

    public class LandfillRepository : ILandfillRepository
    {
        private readonly AppDbContext _context;

        public LandfillRepository(AppDbContext context)
        {
            _context = context;
        }

        public async Task<LandfillEntity> AddAsync(LandfillEntity landfill)
        {
            await _context.Landfills.AddAsync(landfill);
            await _context.SaveChangesAsync();
            return landfill;
        }

        public async Task<IEnumerable<LandfillEntity>> GetAllAsync()
        {
            return await _context.Landfills.AsNoTracking().ToListAsync();
        }

        public async Task<LandfillEntity?> GetByIdAsync(int id)
        {
            return await _context.Landfills.FindAsync(id);
        }

        public async Task<IEnumerable<LandfillEntity>> FindInRadiusAsync(Point userLocation, int radiusInMeters)
        {
            return await _context.Landfills
                .Where(l => l.Location.IsWithinDistance(userLocation, radiusInMeters))
                .AsNoTracking()
                .ToListAsync();
        }
    }
}
