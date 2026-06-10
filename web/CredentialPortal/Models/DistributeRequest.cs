using System.Text.Json.Serialization;

namespace CredentialPortal.Models;

public class DistributeRequest
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = "";

    [JsonPropertyName("email")]
    public string Email { get; set; } = "";

    [JsonPropertyName("credential")]
    public string Credential { get; set; } = "";

    [JsonPropertyName("system_name")]
    public string SystemName { get; set; } = "Company Portal";

    [JsonPropertyName("account_login")]
    public string AccountLogin { get; set; } = "";

    [JsonPropertyName("expiry_days")]
    public int? ExpiryDays { get; set; }
}
