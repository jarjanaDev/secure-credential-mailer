using System.Net.Http.Json;
using System.Text.Json;
using CredentialPortal.Models;

namespace CredentialPortal.Services;

public class MailerApiClient
{
    private readonly HttpClient _http;

    // snake_case ↔ PascalCase mapping for Python API responses
    private static readonly JsonSerializerOptions _opts = new()
    {
        PropertyNameCaseInsensitive = true,
    };

    public MailerApiClient(HttpClient http) => _http = http;

    public async Task<DistributeResult> DistributeAsync(DistributeRequest req)
    {
        var resp = await _http.PostAsJsonAsync("/distribute", req, _opts);
        resp.EnsureSuccessStatusCode();
        return await resp.Content.ReadFromJsonAsync<DistributeResult>(_opts)
               ?? throw new InvalidOperationException("Empty response from API");
    }

    public async Task<List<AuditRecord>> GetAuditLogAsync(int limit = 200)
    {
        return await _http.GetFromJsonAsync<List<AuditRecord>>($"/audit?limit={limit}", _opts)
               ?? new List<AuditRecord>();
    }

    public async Task<string> ExportReportAsync()
    {
        var resp = await _http.PostAsync("/audit/report", null);
        resp.EnsureSuccessStatusCode();
        var result = await resp.Content.ReadFromJsonAsync<Dictionary<string, string>>(_opts);
        return result?["path"] ?? "unknown";
    }
}
