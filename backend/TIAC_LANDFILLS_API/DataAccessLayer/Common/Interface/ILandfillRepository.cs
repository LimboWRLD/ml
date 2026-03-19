using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using NetTopologySuite.Geometries;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace DataAccessLayer.Common.Interface
{

    public interface ILandfillRepository
    {
        Task<IEnumerable<LandfillEntity>> GetAllAsync();
        Task<LandfillEntity?> GetByIdAsync(int id);
        Task<LandfillEntity> AddAsync(LandfillEntity landfill);
        Task<IEnumerable<LandfillEntity>> FindInRadiusAsync(Point userLocation, int radiusInMeters);
    }
}
