using System.Threading.Channels;
using System.Threading.RateLimiting;
using Group6Live;

var builder = WebApplication.CreateBuilder(args);
builder.WebHost.ConfigureKestrel(options => options.Limits.MaxRequestBodySize = 16_384);
builder.Services.AddSingleton(new PortalStore(Environment.GetEnvironmentVariable("DATABASE_URL")));
builder.Services.AddSingleton<LiveBus>();
builder.Services.AddRateLimiter(options =>
{
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    options.AddPolicy("public-write", context =>
        RateLimitPartition.GetFixedWindowLimiter(
            context.Connection.RemoteIpAddress?.ToString() ?? "unknown",
            _ => new FixedWindowRateLimiterOptions
            {
                PermitLimit = 8,
                Window = TimeSpan.FromMinutes(1),
                QueueLimit = 0,
                AutoReplenishment = true
            }));
});

var app = builder.Build();
app.Use(async (context, next) =>
{
    context.Response.Headers["X-Content-Type-Options"] = "nosniff";
    context.Response.Headers["X-Frame-Options"] = "DENY";
    context.Response.Headers["Referrer-Policy"] = "no-referrer";
    context.Response.Headers["Content-Security-Policy"] =
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; " +
        "connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'";
    await next();
});
app.UseDefaultFiles();
app.UseStaticFiles();
app.UseRateLimiter();

app.MapGet("/health/live", () => Results.Ok(new
{
    status = "running",
    api = "aspnet-core",
    version = "1.0",
    utc = DateTimeOffset.UtcNow
}));

app.MapGet("/health/ready", async (PortalStore store, ILogger<Program> log, CancellationToken ct) =>
{
    try
    {
        if (await store.ProbeAsync(ct))
            return Results.Ok(new { status = "ready", database = "postgresql" });
    }
    catch (Exception ex) when (ex is not OperationCanceledException)
    {
        log.LogWarning("Database readiness check failed: {Type}", ex.GetType().Name);
    }
    return Results.Json(new { status = "not_ready", database = "unavailable" }, statusCode: 503);
});

app.MapGet("/api/status", async (PortalStore store, LiveBus bus, ILogger<Program> log, CancellationToken ct) =>
{
    try
    {
        if (!await store.ProbeAsync(ct))
            return Results.Json(new { online = false, database = "not_configured" }, statusCode: 503);
        return Results.Ok(new
        {
            online = true,
            database = "postgresql",
            realtime = "server-sent-events",
            connectedBrowsers = bus.ConnectedBrowsers,
            requests = await store.CountAsync(ct),
            serverUtc = DateTimeOffset.UtcNow
        });
    }
    catch (Exception ex) when (ex is not OperationCanceledException)
    {
        log.LogWarning("Database status failed: {Type}", ex.GetType().Name);
        return Results.Json(new { online = false, database = "unavailable" }, statusCode: 503);
    }
});

app.MapGet("/api/requests", async (PortalStore store, ILogger<Program> log, CancellationToken ct) =>
{
    try { return Results.Ok(await store.RecentAsync(40, ct)); }
    catch (Exception ex) when (ex is not OperationCanceledException)
    {
        log.LogWarning("Requests lookup failed: {Type}", ex.GetType().Name);
        return Results.Json(new { error = "Database is not available" }, statusCode: 503);
    }
});

app.MapGet("/api/mentors", async (PortalStore store, ILogger<Program> log, CancellationToken ct) =>
{
    try { return Results.Ok(await store.MentorsAsync(ct)); }
    catch (Exception ex) when (ex is not OperationCanceledException)
    {
        log.LogWarning("Mentors lookup failed: {Type}", ex.GetType().Name);
        return Results.Json(new { error = "Database is not available" }, statusCode: 503);
    }
});

// These records are unverified public suggestions, separate from the curated mentor list.
app.MapGet("/api/mentor-suggestions", async (PortalStore store, ILogger<Program> log, CancellationToken ct) =>
{
    try { return Results.Ok(await store.MentorSuggestionsAsync(ct)); }
    catch (Exception ex) when (ex is not OperationCanceledException)
    {
        log.LogWarning("Mentor suggestion lookup failed: {Type}", ex.GetType().Name);
        return Results.Json(new { error = "Database is not available" }, statusCode: 503);
    }
});

app.MapPost("/api/mentor-suggestions", async (
    MentorSubmission input, PortalStore store, LiveBus bus, ILogger<Program> log, CancellationToken ct) =>
{
    if (!MentorSubmissionValidator.TryValidate(input, out var cleaned, out var reason))
        return Results.BadRequest(new { error = reason });
    try
    {
        var saved = await store.CreateSuggestionAsync(cleaned!, ct);
        bus.PublishChange();
        return Results.Created($"/api/mentor-suggestions/{saved.Id}", saved);
    }
    catch (Exception ex) when (ex is not OperationCanceledException)
    {
        log.LogWarning("Mentor suggestion insert failed: {Type}", ex.GetType().Name);
        return Results.Json(new { error = "Database is not available" }, statusCode: 503);
    }
}).RequireRateLimiting("public-write");

app.MapPost("/api/requests", async (
    NewRequest input, PortalStore store, LiveBus bus, ILogger<Program> log, CancellationToken ct) =>
{
    if (!PortalValidation.TryValidate(input, out var draft, out var error))
        return Results.BadRequest(new { error });
    try
    {
        var inserted = await store.InsertAsync(draft!, ct);
        bus.PublishChange();
        return Results.Created($"/api/requests/{inserted.Id}", inserted);
    }
    catch (Exception ex) when (ex is not OperationCanceledException)
    {
        log.LogWarning("Database write failed: {Type}", ex.GetType().Name);
        return Results.Json(new { error = "Database is not available" }, statusCode: 503);
    }
}).RequireRateLimiting("public-write");

app.MapGet("/api/events", async (HttpContext context, LiveBus bus) =>
{
    context.Response.Headers["Cache-Control"] = "no-cache, no-transform";
    context.Response.Headers["X-Accel-Buffering"] = "no";
    context.Response.ContentType = "text/event-stream; charset=utf-8";
    var ct = context.RequestAborted;
    var (id, reader) = bus.Subscribe();
    try
    {
        await context.Response.WriteAsync(": connected\n\n", ct);
        await context.Response.Body.FlushAsync(ct);
        while (!ct.IsCancellationRequested)
        {
            using var timeout = CancellationTokenSource.CreateLinkedTokenSource(ct);
            timeout.CancelAfter(TimeSpan.FromSeconds(20));
            try
            {
                var notification = await reader.ReadAsync(timeout.Token);
                await context.Response.WriteAsync($"event: changed\ndata: {notification}\n\n", ct);
            }
            catch (OperationCanceledException) when (!ct.IsCancellationRequested)
            {
                await context.Response.WriteAsync(": keepalive\n\n", ct);
            }
            await context.Response.Body.FlushAsync(ct);
        }
    }
    catch (OperationCanceledException) when (ct.IsCancellationRequested) { }
    catch (ChannelClosedException) { }
    finally { bus.Unsubscribe(id); }
});

app.Run();
