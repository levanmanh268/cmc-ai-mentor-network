FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /source
COPY Group6Live.csproj .
RUN dotnet restore Group6Live.csproj
COPY . .
RUN dotnet publish Group6Live.csproj -c Release -o /app/publish --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final
WORKDIR /app
COPY --from=build /app/publish .
ENV ASPNETCORE_URLS=http://0.0.0.0:10000
EXPOSE 10000
USER $APP_UID
ENTRYPOINT ["dotnet", "Group6Live.dll"]
