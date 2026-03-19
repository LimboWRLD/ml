using BusinessLogicLayer.DTO;
using BusinessLogicLayer.DTO.Requests.Create;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace BusinessLogicLayer.Interfaces
{
    public interface ILandfillService
    {
        Task<IEnumerable<LandfillDto>> GetAllLandfillsAsync();
        Task<LandfillDto?> GetLandfillByIdAsync(int id);
        Task<LandfillDto> CreateLandfillAsync(CreateLandfillRequest request);
        Task<IEnumerable<LandfillDto>> GetLandfillsInRadiusAsync(double latitude, double longitude, int radiusInKm);
    }
}
