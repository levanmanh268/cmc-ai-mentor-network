namespace Group6Live;

public sealed record NewRequest(string? Nickname, string? Topic, string? Message);
public sealed record RequestDraft(string Nickname, string Topic, string Message);
public sealed record RequestRow(long Id, string Nickname, string Topic, string Message, DateTime CreatedAt);
public sealed record MentorRow(long Id, string Name, string Field, string Bio);

public static class PortalValidation
{
    private static readonly HashSet<string> Topics = new(StringComparer.Ordinal)
    {
        "AI", "RAG", "Mentor", "Career", "Other"
    };

    public static bool TryValidate(NewRequest? input, out RequestDraft? draft, out string error)
    {
        draft = null;
        error = "Invalid request";
        if (input is null) return false;
        var nickname = (input.Nickname ?? "").Trim();
        var topic = (input.Topic ?? "").Trim();
        var message = (input.Message ?? "").Trim();
        if (nickname.Length == 0) nickname = "Người học ẩn danh";
        if (nickname.Length > 36 || HasControlCharacters(nickname))
        {
            error = "Tên hiển thị tối đa 36 ký tự, không chứa ký tự điều khiển.";
            return false;
        }
        if (!Topics.Contains(topic))
        {
            error = "Chủ đề không hợp lệ.";
            return false;
        }
        if (message.Length < 5 || message.Length > 380 || HasControlCharacters(message))
        {
            error = "Nội dung phải có 5 đến 380 ký tự, không chứa ký tự điều khiển.";
            return false;
        }
        draft = new RequestDraft(nickname, topic, message);
        error = "";
        return true;
    }

    private static bool HasControlCharacters(string value) =>
        value.Any(ch => char.IsControl(ch) && ch != '\n' && ch != '\t');
}
