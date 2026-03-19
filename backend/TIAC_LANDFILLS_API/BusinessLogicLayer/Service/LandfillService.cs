using BusinessLogicLayer.DTO;
using BusinessLogicLayer.DTO.Requests.Create;
using BusinessLogicLayer.Interfaces;
using DataAccessLayer.Common.Interface;
using NetTopologySuite.Geometries;

namespace BusinessLogicLayer.Service
{
    public class LandfillService : ILandfillService
    {
        private readonly ILandfillRepository _repository;

        public LandfillService(ILandfillRepository repository)
        {
            _repository = repository;
        }

        public async Task<LandfillDto> CreateLandfillAsync(CreateLandfillRequest request)
        {
            var entity = new LandfillEntity
            {
                LandfillId = request.LandfillId,
                Status = request.Status,
                Location = new Point(request.Longitude, request.Latitude) { SRID = 4326 },
                AreaM2 = request.AreaM2,
                VolumeM3 = request.VolumeM3,
                WasteMassTons = request.WasteMassTons,
                StartYear = request.StartYear,
                MethaneTonsPerYear = request.MethaneTonsPerYear,
                Co2eqTonsPerYear = request.Co2eqTonsPerYear
            };

            var newEntity = await _repository.AddAsync(entity);

            return MapToDto(newEntity);
        }

        public async Task<IEnumerable<LandfillDto>> GetAllLandfillsAsync()
        {
            var entities = await _repository.GetAllAsync();
            var dtos = new List<LandfillDto>();
            foreach (var entity in entities)
            {
                dtos.Add(MapToDto(entity));
            }
            return dtos;
        }

        public async Task<LandfillDto?> GetLandfillByIdAsync(int id)
        {
            var entity = await _repository.GetByIdAsync(id);
            return entity == null ? null : MapToDto(entity);
        }

        public async Task<IEnumerable<LandfillDto>> GetLandfillsInRadiusAsync(double latitude, double longitude, int radiusInKm)
        {
            var userLocation = new Point(longitude, latitude) { SRID = 4326 };
            int radiusInMeters = radiusInKm * 1000;

            var entities = await _repository.FindInRadiusAsync(userLocation, radiusInMeters);

            var dtos = new List<LandfillDto>();
            foreach (var entity in entities)
            {
                dtos.Add(MapToDto(entity));
            }
            return dtos;
        }

        private LandfillDto MapToDto(LandfillEntity entity)
        {
            return new LandfillDto
            {
                Id = entity.Id,
                LandfillId = entity.LandfillId,
                Status = entity.Status.ToString(),
                Latitude = entity.Location.Y,
                Longitude = entity.Location.X,
                AreaM2 = entity.AreaM2,
                VolumeM3 = entity.VolumeM3,
                WasteMassTons = entity.WasteMassTons,
                StartYear = entity.StartYear,
                MethaneTonsPerYear = entity.MethaneTonsPerYear,
                Co2eqTonsPerYear = entity.Co2eqTonsPerYear
            };
        }
    }
}
