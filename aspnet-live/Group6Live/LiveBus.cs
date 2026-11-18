using System.Collections.Concurrent;
using System.Threading.Channels;

namespace Group6Live;

public sealed class LiveBus
{
    private readonly ConcurrentDictionary<Guid, Channel<string>> _clients = new();

    public (Guid Id, ChannelReader<string> Reader) Subscribe()
    {
        var id = Guid.NewGuid();
        var channel = Channel.CreateBounded<string>(new BoundedChannelOptions(8)
        {
            FullMode = BoundedChannelFullMode.DropOldest,
            SingleReader = true,
            SingleWriter = false
        });
        _clients[id] = channel;
        return (id, channel.Reader);
    }

    public void Unsubscribe(Guid id)
    {
        if (_clients.TryRemove(id, out var channel)) channel.Writer.TryComplete();
    }

    public void PublishChange()
    {
        foreach (var client in _clients.Values)
            client.Writer.TryWrite("refresh");
    }

    public int ConnectedBrowsers => _clients.Count;
}
