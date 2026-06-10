using System.Text.Json.Serialization;

namespace CredentialPortal.Models;

public class DistributeResult
{
    [JsonPropertyName("success")]
    public bool Success { get; set; }

    [JsonPropertyName("message")]
    public string Message { get; set; } = "";
}
