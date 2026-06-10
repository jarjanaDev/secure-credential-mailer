using CredentialPortal.Models;
using CredentialPortal.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace CredentialPortal.Pages;

[Authorize]
public class IndexModel : PageModel
{
    private readonly MailerApiClient _api;
    private readonly IConfiguration _config;

    public DistributeResult? Result { get; private set; }
    public DistributeRequest Input { get; private set; } = new();
    public int DelaySeconds { get; private set; } = 30;

    public IndexModel(MailerApiClient api, IConfiguration config)
    {
        _api = api;
        _config = config;
    }

    public void OnGet() { }

    public async Task<IActionResult> OnPostAsync(
        string name, string email, string credential,
        string systemName = "Company Portal",
        string accountLogin = "",
        int? expiryDays = null)
    {
        Input = new DistributeRequest
        {
            Name = name,
            Email = email,
            SystemName = systemName,
            AccountLogin = accountLogin,
            ExpiryDays = expiryDays,
        };

        try
        {
            Result = await _api.DistributeAsync(new DistributeRequest
            {
                Name = name,
                Email = email,
                Credential = credential,
                SystemName = systemName,
                AccountLogin = accountLogin,
                ExpiryDays = expiryDays,
            });
        }
        catch (HttpRequestException ex)
        {
            Result = new DistributeResult
            {
                Success = false,
                Message = $"API error: {ex.Message}",
            };
        }

        return Page();
    }
}
