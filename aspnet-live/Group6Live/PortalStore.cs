using Npgsql;

namespace Group6Live;

/// <summary>
/// PostgreSQL persistence. Never falls back to an in-memory "database".
/// </summary>
public sealed class PortalStore : IAsyncDisposable
{
    private readonly NpgsqlDataSource? _source;
    private readonly SemaphoreSlim _initLock = new(1, 1);
    private bool _schemaReady;

    public bool IsConfigured => _source is not null;

    public PortalStore(string? rawConnection)
    {
        if (!string.IsNullOrWhiteSpace(rawConnection))
        {
            _source = NpgsqlDataSource.Create(NormalizeConnectionString(rawConnection));
        }
    }

    public static string NormalizeConnectionString(string raw)
    {
        if (!(raw.StartsWith("postgres://", StringComparison.OrdinalIgnoreCase)
             || raw.StartsWith("postgresql://", StringComparison.OrdinalIgnoreCase)))
        {
            return raw;
        }
        var url = new Uri(raw);
        var credentials = url.UserInfo.Split(':', 2);
        if (credentials.Length != 2 || string.IsNullOrEmpty(url.Host))
            throw new ArgumentException("Invalid PostgreSQL URL");
        var connection = new NpgsqlConnectionStringBuilder
        {
            Host = url.Host,
            Port = url.IsDefaultPort ? 5432 : url.Port,
            Username = Uri.UnescapeDataString(credentials[0]),
            Password = Uri.UnescapeDataString(credentials[1]),
            Database = Uri.UnescapeDataString(url.AbsolutePath.TrimStart('/')),
            SslMode = SslMode.Require,
            Timeout = 8,
            CommandTimeout = 8,
            MaxPoolSize = 12,
            Pooling = true,
            ApplicationName = "cmc-group6-aspnet-live"
        };
        return connection.ConnectionString;
    }

    private async Task EnsureSchemaAsync(CancellationToken ct)
    {
        if (_source is null) throw new InvalidOperationException("DATABASE_URL not configured");
        if (_schemaReady) return;
        await _initLock.WaitAsync(ct);
        try
        {
            if (_schemaReady) return;
            await using var conn = await _source.OpenConnectionAsync(ct);
            await using var cmd = new NpgsqlCommand("""
                CREATE SCHEMA IF NOT EXISTS group6_live;
                CREATE TABLE IF NOT EXISTS group6_live.requests (
                    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    nickname VARCHAR(36) NOT NULL,
                    topic VARCHAR(20) NOT NULL,
                    message VARCHAR(380) NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
                CREATE INDEX IF NOT EXISTS idx_group6_live_requests_recent
                  ON group6_live.requests (id DESC);
                CREATE TABLE IF NOT EXISTS group6_live.mentors (
                    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    name VARCHAR(80) NOT NULL,
                    field VARCHAR(80) NOT NULL,
                    bio VARCHAR(240) NOT NULL
                );
                INSERT INTO group6_live.mentors (id, name, field, bio)
                OVERRIDING SYSTEM VALUE VALUES
                    (1, 'Mentor Demo 01', 'RAG / NLP', 'Hướng dẫn tìm tài liệu, truy xuất và đánh giá nguồn.'),
                    (2, 'Mentor Demo 02', 'Machine Learning', 'Hướng dẫn xây dựng mô hình và kiểm thử thực nghiệm.'),
                    (3, 'Mentor Demo 03', 'Software Engineering', 'Hỗ trợ GitHub Issues, Pull Requests và Testing.')
                ON CONFLICT (id) DO NOTHING;
                """, conn);
            await cmd.ExecuteNonQueryAsync(ct);
            _schemaReady = true;
        }
        finally { _initLock.Release(); }
    }

    public async Task<bool> ProbeAsync(CancellationToken ct)
    {
        if (!IsConfigured) return false;
        await EnsureSchemaAsync(ct);
        await using var conn = await _source!.OpenConnectionAsync(ct);
        await using var cmd = new NpgsqlCommand("SELECT 1", conn);
        return (int)(await cmd.ExecuteScalarAsync(ct) ?? 0) == 1;
    }

    public async Task<IReadOnlyList<RequestRow>> RecentAsync(int limit, CancellationToken ct)
    {
        await EnsureSchemaAsync(ct);
        await using var conn = await _source!.OpenConnectionAsync(ct);
        await using var cmd = new NpgsqlCommand("""
            SELECT id, nickname, topic, message, created_at
              FROM group6_live.requests
             ORDER BY id DESC LIMIT @limit
            """, conn);
        cmd.Parameters.AddWithValue("limit", Math.Clamp(limit, 1, 50));
        var result = new List<RequestRow>();
        await using var reader = await cmd.ExecuteReaderAsync(ct);
        while (await reader.ReadAsync(ct))
        {
            result.Add(new RequestRow(reader.GetInt64(0), reader.GetString(1),
                reader.GetString(2), reader.GetString(3), reader.GetDateTime(4)));
        }
        return result;
    }

    public async Task<IReadOnlyList<MentorRow>> MentorsAsync(CancellationToken ct)
    {
        await EnsureSchemaAsync(ct);
        await using var conn = await _source!.OpenConnectionAsync(ct);
        await using var cmd = new NpgsqlCommand("""
            SELECT id, name, field, bio
              FROM group6_live.mentors
             ORDER BY id ASC
            """, conn);
        var result = new List<MentorRow>();
        await using var reader = await cmd.ExecuteReaderAsync(ct);
        while (await reader.ReadAsync(ct))
            result.Add(new MentorRow(reader.GetInt64(0), reader.GetString(1),
                reader.GetString(2), reader.GetString(3)));
        return result;
    }

    public async Task<RequestRow> InsertAsync(RequestDraft item, CancellationToken ct)
    {
        await EnsureSchemaAsync(ct);
        await using var conn = await _source!.OpenConnectionAsync(ct);
        await using var cmd = new NpgsqlCommand("""
            INSERT INTO group6_live.requests (nickname, topic, message)
            VALUES (@name, @topic, @message)
            RETURNING id, nickname, topic, message, created_at
            """, conn);
        cmd.Parameters.AddWithValue("name", item.Nickname);
        cmd.Parameters.AddWithValue("topic", item.Topic);
        cmd.Parameters.AddWithValue("message", item.Message);
        await using var reader = await cmd.ExecuteReaderAsync(ct);
        if (!await reader.ReadAsync(ct)) throw new InvalidOperationException("Insert returned no row");
        return new RequestRow(reader.GetInt64(0), reader.GetString(1),
            reader.GetString(2), reader.GetString(3), reader.GetDateTime(4));
    }

    public async Task<long> CountAsync(CancellationToken ct)
    {
        await EnsureSchemaAsync(ct);
        await using var conn = await _source!.OpenConnectionAsync(ct);
        await using var cmd = new NpgsqlCommand("SELECT COUNT(*) FROM group6_live.requests", conn);
        return (long)(await cmd.ExecuteScalarAsync(ct) ?? 0L);
    }

    public async ValueTask DisposeAsync()
    {
        _initLock.Dispose();
        if (_source is not null) await _source.DisposeAsync();
    }
}
