using System.Text.Json.Serialization;

namespace CredentialPortal.Models;

public class AuditRecord
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = "";

    [JsonPropertyName("recipient_name")]
    public string RecipientName { get; set; } = "";

    [JsonPropertyName("recipient_email")]
    public string RecipientEmail { get; set; } = "";

    [JsonPropertyName("system_name")]
    public string SystemName { get; set; } = "";

    [JsonPropertyName("created_at")]
    public string CreatedAt { get; set; } = "";

    [JsonPropertyName("expiry_date")]
    public string ExpiryDate { get; set; } = "";

    [JsonPropertyName("part1_status")]
    public string Part1Status { get; set; } = "PENDING";

    [JsonPropertyName("part2_status")]
    public string Part2Status { get; set; } = "PENDING";

    [JsonPropertyName("completed_at")]
    public string? CompletedAt { get; set; }

    [JsonPropertyName("error_info")]
    public string? ErrorInfo { get; set; }
}
