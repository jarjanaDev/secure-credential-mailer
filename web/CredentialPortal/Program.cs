using System.Net.Http.Headers;
using System.Text;
using CredentialPortal.Services;
using Microsoft.AspNetCore.Authentication.Cookies;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorPages();

builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options =>
    {
        options.LoginPath = "/Login";
        options.ExpireTimeSpan = TimeSpan.FromHours(8);
        options.SlidingExpiration = true;
    });

builder.Services.AddAuthorization();

builder.Services.AddHttpClient<MailerApiClient>((sp, client) =>
{
    var cfg = sp.GetRequiredService<IConfiguration>();
    var baseUrl = cfg["MailerApi:BaseUrl"] ?? "http://localhost:8000";
    var user    = cfg["MailerApi:Username"] ?? "itops";
    var pass    = cfg["MailerApi:Password"] ?? "changeme";
    client.BaseAddress = new Uri(baseUrl);
    client.Timeout = TimeSpan.FromMinutes(5); // allow for enforced split delay
    var token = Convert.ToBase64String(Encoding.ASCII.GetBytes($"{user}:{pass}"));
    client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Basic", token);
});

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    app.UseHsts();
    app.UseHttpsRedirection();
}

app.UseStaticFiles();
app.UseRouting();
app.UseAuthentication();
app.UseAuthorization();
app.MapRazorPages();

app.Run();
