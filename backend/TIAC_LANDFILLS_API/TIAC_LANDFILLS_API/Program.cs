using BusinessLogicLayer.Interfaces;
using BusinessLogicLayer.Service;
using DataAccessLayer.Common.Interface;
using DataAccessLayer.Data;
using DataAccessLayer.Repositories;
using Microsoft.EntityFrameworkCore;
using NetTopologySuite;
using Microsoft.AspNetCore.Builder;

var builder = WebApplication.CreateBuilder(args);
builder.WebHost.UseUrls("http://0.0.0.0:8080");
string _cors = "cors";

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection"),
        o => o.UseNetTopologySuite()));

builder.Services.AddHttpContextAccessor();
builder.Services.AddSwaggerGen(c =>
{
});

builder.Services.AddCors(options => {
    options.AddPolicy(name: _cors, builder =>
    {
        builder.AllowAnyOrigin().AllowAnyHeader().AllowAnyMethod();
    });
});


builder.Services.AddSingleton(NtsGeometryServices.Instance);

builder.Services.AddScoped<ILandfillRepository, LandfillRepository>();
builder.Services.AddScoped<ILandfillService, LandfillService>();

builder.Services.AddControllers();
builder.Services.AddOpenApi();
builder.Services.AddProblemDetails();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "Landfills v1");
    });
}
app.UseCors(_cors);

//app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();
