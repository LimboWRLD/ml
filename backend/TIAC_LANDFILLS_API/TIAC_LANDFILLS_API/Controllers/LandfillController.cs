using BusinessLogicLayer.DTO.Requests.Create;
using BusinessLogicLayer.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace TIAC_LANDFILLS_API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class LandfillController : ControllerBase
    {
        private readonly ILandfillService _landfillService;

        public LandfillController(ILandfillService landfillService)
        {
            _landfillService = landfillService;
        }

        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            var landfills = await _landfillService.GetAllLandfillsAsync();
            return Ok(landfills);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var landfill = await _landfillService.GetLandfillByIdAsync(id);
            if (landfill == null)
            {
                return NotFound();
            }
            return Ok(landfill);
        }

        [HttpGet("nearby")]
        public async Task<IActionResult> GetNearby([FromQuery] double latitude, [FromQuery] double longitude, [FromQuery] int radiusInKm = 2)
        {
            var landfills = await _landfillService.GetLandfillsInRadiusAsync(latitude, longitude, radiusInKm);
            return Ok(landfills);
        }

        [HttpPost]
        public async Task<IActionResult> CreateLandfill([FromBody] CreateLandfillRequest request)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            var createdLandfill = await _landfillService.CreateLandfillAsync(request);
            return CreatedAtAction(nameof(GetById), new { id = createdLandfill.Id }, createdLandfill);
        }
    }
}
