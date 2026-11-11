using Xunit;
using Group6Live;
using Npgsql;

namespace Group6Live.Tests;

public sealed class PortalValidationTests
{
    [Fact]
    public void AcceptsValidSubmission()
    {
        Assert.True(PortalValidation.TryValidate(new NewRequest("Bạn A", "RAG", "Mình muốn học RAG."), out var draft, out var error));
        Assert.Equal("Bạn A", draft!.Nickname);
        Assert.Equal("RAG", draft.Topic);
        Assert.Equal("", error);
    }

    [Fact]
    public void DefaultsToAnonymousNickname()
    {
        Assert.True(PortalValidation.TryValidate(new NewRequest("", "Mentor", "Tìm mentor AI."), out var draft, out _));
        Assert.Equal("Người học ẩn danh", draft!.Nickname);
    }

    [Theory]
    [InlineData("AI", "")]
    [InlineData("AI", "abc")]
    [InlineData("Unknown", "Câu hỏi hợp lệ")]
    public void RejectsInvalidTopicOrMessage(string topic, string message)
    {
        Assert.False(PortalValidation.TryValidate(new NewRequest("A", topic, message), out var draft, out _));
        Assert.Null(draft);
    }

    [Fact]
    public void RejectsOversizedContent()
    {
        Assert.False(PortalValidation.TryValidate(new NewRequest("A", "AI", new string('x', 381)), out _, out _));
        Assert.False(PortalValidation.TryValidate(new NewRequest(new string('A', 37), "AI", "Thông tin hợp lệ"), out _, out _));
    }

    [Fact]
    public void RejectsNullAndControlCharacters()
    {
        Assert.False(PortalValidation.TryValidate(null, out _, out _));
        Assert.False(PortalValidation.TryValidate(new NewRequest("A", "AI", "Hello\u0000there"), out _, out _));
    }

    [Fact]
    public void TrimsWhitespaceWithoutDroppingUnicode()
    {
        Assert.True(PortalValidation.TryValidate(new NewRequest("  Mạnh  ", "AI", "  Tìm hiểu thế giới  "), out var draft, out _));
        Assert.Equal("Mạnh", draft!.Nickname);
        Assert.Equal("Tìm hiểu thế giới", draft.Message);
    }

    [Fact]
    public void HtmlPayloadRemainsDataNotInterpretedCode()
    {
        const string content = "<img src=x onerror=alert(1)> muốn học AI";
        Assert.True(PortalValidation.TryValidate(new NewRequest("Bạn B", "AI", content), out var draft, out _));
        Assert.Equal(content, draft!.Message);
        // Browser renders via textContent, not innerHTML; this test only checks backend integrity.
    }

    [Fact]
    public void PostgreSqlUrlRequiresTlsAndDecodesCredentials()
    {
        var connection = PortalStore.NormalizeConnectionString(
            "postgresql://group6_user:p%40ssword@db.example.test:5432/group6_live");
        var parsed = new NpgsqlConnectionStringBuilder(connection);
        Assert.Equal("group6_user", parsed.Username);
        Assert.Equal("p@ssword", parsed.Password);
        Assert.Equal("group6_live", parsed.Database);
        Assert.Equal(SslMode.Require, parsed.SslMode);
    }

    [Fact]
    public void LocalDbConnectionStringCanUseTestOnlyNonTls()
    {
        const string local = "Host=127.0.0.1;Database=test;SSL Mode=Disable";
        Assert.Equal(local, PortalStore.NormalizeConnectionString(local));
    }

    [Fact]
    public void AcceptsValidCommunityMentorSuggestion()
    {
        var submitted = new MentorSubmission("Mentor Demo", "AI Engineer", "CMCU",
            "NLP & LLM", 4, "Dạy các môn AI, RAG và kiểm thử phần mềm.",
            new[] { "RAG", "Python" }, new[] { "Project" });
        Assert.True(MentorSubmissionValidator.TryValidate(submitted, out var cleaned, out _));
        Assert.Equal("Mentor Demo", cleaned!.Name);
    }

    [Fact]
    public void MentorSuggestionRejectsInvalidExperienceAndPrivateControlChars()
    {
        var input = new MentorSubmission("A", "Engineer", "Demo", "AI",
            -1, "Hỗ trợ dự án AI", new[] { "AI" }, new[] { "Project" });
        Assert.False(MentorSubmissionValidator.TryValidate(input, out _, out _));
        Assert.False(MentorSubmissionValidator.TryValidate(
            input with { ExperienceYears = 2, Name = "bad\u0000name" }, out _, out _));
    }

    [Fact]
    public void MentorSuggestionRejectsFakeSupportAndEmptySkills()
    {
        var original = new MentorSubmission("A", "Engineer", "Demo", "AI",
            2, "Hỗ trợ dự án AI", new[] { "AI" }, new[] { "Project" });
        Assert.False(MentorSubmissionValidator.TryValidate(
            original with { AvailableFor = new[] { "Untrusted role" } }, out _, out _));
        Assert.False(MentorSubmissionValidator.TryValidate(
            original with { Strengths = Array.Empty<string>() }, out _, out _));
    }
}
