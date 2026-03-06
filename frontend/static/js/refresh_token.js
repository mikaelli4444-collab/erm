// api.js
// Maneja requests y refresh automático

let accessToken = null;

// ===============================
// FUNCIÓN PRINCIPAL PARA REQUESTS
// ===============================
async function apiFetch(url, options = {}) {

    const headers = options.headers || {};

    // Si tenemos access token, lo mandamos
    if (accessToken) {
        headers["Authorization"] = "Bearer " + accessToken;
    }

    const response = await fetch(url, {
        ...options,
        headers,
        credentials: "include" // 🔥 ENVÍA COOKIE DEL REFRESH
    });

    // ===============================
    // SI TODO OK → DEVOLVER
    // ===============================
    if (response.status !== 401) {
        return response;
    }

    // ===============================
    // TOKEN EXPIRÓ → REFRESH
    // ===============================
    console.log("Access token expiró, refrescando...");

    const refreshResponse = await fetch("/home/refresh", {
        method: "GET",
        credentials: "include"
    });

    if (!refreshResponse.ok) {
        // Refresh inválido → login
        window.location.href = "/login";
        return;
    }

    const data = await refreshResponse.json();
    accessToken = data.access_token;

    // ===============================
    // REINTENTAR REQUEST ORIGINAL
    // ===============================
    headers["Authorization"] = "Bearer " + accessToken;

    return fetch(url, {
        ...options,
        headers,
        credentials: "include"
    });
}

// ===============================
// EXPORTAR PARA USAR EN HTML
// ===============================
window.apiFetch = apiFetch;