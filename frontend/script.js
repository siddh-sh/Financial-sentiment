let sentimentChart = null;
let confidenceChart = null;

// ===============================
//  BACKEND URL CONFIG
// ===============================
const BACKEND_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? "http://127.0.0.1:8000"
  : "https://financial-sentiment.onrender.com";

// ===============================
//  LOAD TICKERS FROM BACKEND
// ===============================
window.addEventListener("DOMContentLoaded", async () => {
  const tickerSelect = document.getElementById("tickerSelect");

  try {
    const res = await fetch(`${BACKEND_URL}/tickers`);
    const data = await res.json();

    if (data.tickers && data.tickers.length > 0) {
      tickerSelect.innerHTML = data.tickers
        .map(t => `<option value="${t}">${t}</option>`)
        .join("");
    } else {
      tickerSelect.innerHTML = `<option>No tickers found</option>`;
    }
  } catch (err) {
    tickerSelect.innerHTML = `<option>Failed to load tickers</option>`;
    console.error("Ticker load error:", err);
  }
});

// ===============================
//  ANALYZE BUTTON ACTION
// ===============================
document.getElementById("analyzeBtn").addEventListener("click", analyze);

async function analyze() {
  const ticker = document.getElementById("tickerSelect").value;
  const loading = document.getElementById("loading");
  const resultBox = document.getElementById("resultContainer");
  const mainCard = document.getElementById("mainCard");
  const newsContainer = document.getElementById("newsContainer");

  if (!ticker) return alert("Please select a valid stock!");

  resultBox.classList.add("hidden");
  loading.classList.remove("hidden");

  try {
    const res = await fetch(`${BACKEND_URL}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker, limit: 8 })
    });

    const data = await res.json();
    loading.classList.add("hidden");

    if (data.error) return alert(data.error);

    resultBox.classList.remove("hidden");

    const bullish = (data.overall_bullish_prob * 100).toFixed(1);
    const bearish = (100 - bullish).toFixed(1);

    mainCard.innerHTML = `
      <h1>${data.ticker}</h1>
      <h2 class="${bullish > 50 ? "green" : "red"}">${bullish}% Bullish</h2>
    `;

    const ctx1 = document.getElementById("sentimentPie").getContext("2d");
    if (sentimentChart) sentimentChart.destroy();
    sentimentChart = new Chart(ctx1, {
      type: "pie",
      data: {
        labels: ["Bullish", "Bearish"],
        datasets: [{
          data: [bullish, bearish],
          backgroundColor: ["#4ade80", "#ef4444"],
          borderWidth: 0
        }]
      },
      options: {
        plugins: { legend: { labels: { color: "white" } } }
      }
    });

    const ctx2 = document.getElementById("confidenceBar").getContext("2d");
    if (confidenceChart) confidenceChart.destroy();
    confidenceChart = new Chart(ctx2, {
      type: "bar",
      data: {
        labels: ["Confidence %"],
        datasets: [{
          label: "Model Confidence",
          data: [bullish],
          backgroundColor: "#a855f7",
        }]
      },
      options: {
        scales: {
          y: { ticks: { color: "white" }, beginAtZero: true, max: 100 },
          x: { ticks: { color: "white" } }
        },
        plugins: { legend: { labels: { color: "white" } } }
      }
    });

    newsContainer.innerHTML = data.results.map(n => `
      <a href="${n.url}" target="_blank" rel="noopener noreferrer" class="news-item">
        <h3>${n.headline}</h3>
        <p class="${n.direction === 'Bullish' ? 'green' : 'red'}">
          ${n.direction} (${(n.prob * 100).toFixed(1)}%)
        </p>
      </a>
    `).join("");

  } catch (err) {
    loading.classList.add("hidden");
    console.error("Prediction error:", err);
    alert("Error fetching prediction. Please check backend logs.");
  }
}
