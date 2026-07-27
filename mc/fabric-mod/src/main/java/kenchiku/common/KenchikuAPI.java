package kenchiku.common;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.concurrent.CompletableFuture;
import java.time.Duration;

public class KenchikuAPI {
    private static final String DEFAULT_BASE_URL = "http://localhost:8000";
    private final HttpClient client;
    private final String baseUrl;

    public KenchikuAPI() {
        this(DEFAULT_BASE_URL);
    }

    public KenchikuAPI(String baseUrl) {
        this.baseUrl = baseUrl.replaceAll("/$", "");
        this.client = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .build();
    }

    public CompletableFuture<String> get(String path) {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + path))
                .GET()
                .timeout(Duration.ofSeconds(10))
                .build();
        return client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenApply(HttpResponse::body);
    }

    public CompletableFuture<String> post(String path, String jsonBody) {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + path))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
                .timeout(Duration.ofSeconds(10))
                .build();
        return client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenApply(HttpResponse::body);
    }

    public CompletableFuture<String> healthCheck() {
        return get("/health");
    }
}
