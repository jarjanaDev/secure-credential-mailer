using CredentialPortal.Models;
using CredentialPortal.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace CredentialPortal.Pages;

[Authorize]
public class AuditModel : PageModel
{
    private readonly MailerApiClient _api;
    public List<AuditRecord> Records { get; private set; } = new();
    public string ExportMessage { get; private set; } = "";

    public AuditModel(MailerApiClient api) => _api = api;

    public async Task OnGetAsync()
    {
        Records = await _api.GetAuditLogAsync(limit: 200);
    }

    public async Task<IActionResult> OnPostExportReportAsync()
    {
        try
        {
            var path = await _api.ExportReportAsync();
            ExportMessage = $"Report exported to: {path}";
        }
        catch (HttpRequestException ex)
        {
            ExportMessage = $"Export failed: {ex.Message}";
        }
        Records = await _api.GetAuditLogAsync(limit: 200);
        return Page();
    }
}
