using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace CredentialPortal.Pages;

public class LoginModel : PageModel
{
    private readonly IConfiguration _config;
    public string ErrorMessage { get; private set; } = "";

    public LoginModel(IConfiguration config) => _config = config;

    public IActionResult OnGet()
    {
        if (User.Identity?.IsAuthenticated == true)
            return RedirectToPage("/Index");
        return Page();
    }

    public async Task<IActionResult> OnPostAsync(string username, string password)
    {
        var validUser = _config["Auth:Username"];
        var validPass = _config["Auth:Password"];

        if (string.IsNullOrEmpty(validUser) || string.IsNullOrEmpty(validPass))
            throw new InvalidOperationException("Auth:Username and Auth:Password must be configured via environment variables or user-secrets.");

        static byte[] ToBytes(string s) => Encoding.UTF8.GetBytes(s);
        var userOk = CryptographicOperations.FixedTimeEquals(ToBytes(username ?? ""), ToBytes(validUser));
        var passOk = CryptographicOperations.FixedTimeEquals(ToBytes(password ?? ""), ToBytes(validPass));

        if (!(userOk & passOk))
        {
            ErrorMessage = "Invalid credentials.";
            return Page();
        }

        var claims = new List<Claim>
        {
            new(ClaimTypes.Name, username),
            new(ClaimTypes.Role, "ITOps"),
        };
        var principal = new ClaimsPrincipal(
            new ClaimsIdentity(claims, CookieAuthenticationDefaults.AuthenticationScheme));

        await HttpContext.SignInAsync(CookieAuthenticationDefaults.AuthenticationScheme, principal);
        return RedirectToPage("/Index");
    }
}
