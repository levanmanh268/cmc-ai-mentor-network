using Npgsql;

namespace Group6Live;

/// <summary>Public, explicitly unverified mentor suggestions. Never overwrite the curated static catalog.</summary>
public sealed record MentorSubmission(
    string? Name, string? Title, string? Company, string? Field, int ExperienceYears,
    string? Bio, string[]? Strengths, string[]? AvailableFor);
public sealed record MentorSuggestion(
    long Id, string Name, string Title, string Company, string Field,
    int ExperienceYears, string Bio, string[] Strengths, string[] AvailableFor,
    DateTime CreatedAt, string VerificationStatus = "unverified");

public static class MentorSubmissionValidator
{
    private static readonly HashSet<string> AllowedSupport =
        new(StringComparer.Ordinal) { "Project", "Thực tập", "CV Review", "Nghiên cứu" };

    public static bool TryValidate(MentorSubmission? value, out MentorSubmission? cleaned, out string reason)
    {
        cleaned = null;
        reason = "Invalid mentor suggestion";
        if (value is null) return false;
        if (!ValidText(value.Name, 100) || !ValidText(value.Title, 100) ||
            !ValidText(value.Company, 120) || !ValidText(value.Field, 80) ||
            !ValidText(value.Bio, 600) ||
            value.ExperienceYears < 0 || value.ExperienceYears > 80)
        {
            reason = "Mentor fields missing, invalid or too long.";
            return false;
        }
        var strengths = value.Strengths?.Select(x => x?.Trim() ?? "").ToArray();
        var supports = value.AvailableFor?.Select(x => x?.Trim() ?? "").ToArray();
        if (strengths is null || strengths.Length is < 1 or > 12 ||
            strengths.Any(x => !ValidText(x, 80)) ||
            supports is null || supports.Length is < 1 or > 4 ||
            supports.Any(x => !AllowedSupport.Contains(x)) ||
            supports.Distinct(StringComparer.Ordinal).Count() != supports.Length)
        {
            reason = "Strengths or support types invalid.";
            return false;
        }
        cleaned = new MentorSubmission(
            value.Name!.Trim(), value.Title!.Trim(), value.Company!.Trim(),
            value.Field!.Trim(), value.ExperienceYears, value.Bio!.Trim(),
            strengths, supports);
        reason = "";
        return true;
    }

    private static bool ValidText(string? text, int limit) =>
        !string.IsNullOrWhiteSpace(text) && text.Trim().Length <= limit &&
        !text.Any(c => char.IsControl(c));
}

public sealed partial class PortalStore
{
    public async Task<IReadOnlyList<MentorSuggestion>> MentorSuggestionsAsync(CancellationToken ct)
    {
        await EnsureSchemaAsync(ct);
        await using var conn = await _source!.OpenConnectionAsync(ct);
        await using var cmd = new NpgsqlCommand("""
            SELECT id, name, title, company, field, experience_years, bio,
                   strengths, available_for, created_at
              FROM group6_live.mentor_suggestions
             ORDER BY id DESC LIMIT 100
            """, conn);
        await using var reader = await cmd.ExecuteReaderAsync(ct);
        var rows = new List<MentorSuggestion>();
        while (await reader.ReadAsync(ct))
        {
            rows.Add(new MentorSuggestion(
                reader.GetInt64(0), reader.GetString(1), reader.GetString(2),
                reader.GetString(3), reader.GetString(4), reader.GetInt32(5),
                reader.GetString(6), reader.GetFieldValue<string[]>(7),
                reader.GetFieldValue<string[]>(8), reader.GetDateTime(9)));
        }
        return rows;
    }

    public async Task<MentorSuggestion> CreateSuggestionAsync(MentorSubmission item, CancellationToken ct)
    {
        await EnsureSchemaAsync(ct);
        await using var conn = await _source!.OpenConnectionAsync(ct);
        await using var cmd = new NpgsqlCommand("""
            INSERT INTO group6_live.mentor_suggestions
                (name, title, company, field, experience_years, bio, strengths, available_for)
            VALUES (@name, @title, @company, @field, @years, @bio, @strengths, @supports)
            RETURNING id, name, title, company, field, experience_years, bio,
                      strengths, available_for, created_at
            """, conn);
        cmd.Parameters.AddWithValue("name", item.Name!);
        cmd.Parameters.AddWithValue("title", item.Title!);
        cmd.Parameters.AddWithValue("company", item.Company!);
        cmd.Parameters.AddWithValue("field", item.Field!);
        cmd.Parameters.AddWithValue("years", item.ExperienceYears);
        cmd.Parameters.AddWithValue("bio", item.Bio!);
        cmd.Parameters.AddWithValue("strengths", item.Strengths!);
        cmd.Parameters.AddWithValue("supports", item.AvailableFor!);
        await using var reader = await cmd.ExecuteReaderAsync(ct);
        if (!await reader.ReadAsync(ct))
            throw new InvalidOperationException("Insert did not return a row");
        return new MentorSuggestion(
            reader.GetInt64(0), reader.GetString(1), reader.GetString(2),
            reader.GetString(3), reader.GetString(4), reader.GetInt32(5),
            reader.GetString(6), reader.GetFieldValue<string[]>(7),
            reader.GetFieldValue<string[]>(8), reader.GetDateTime(9));
    }
}
