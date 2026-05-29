const form = document.querySelector("#analysis-form");
const fileInput = document.querySelector("#file-input");
const fileList = document.querySelector("#file-list");
const threshold = document.querySelector("#threshold");
const eps = document.querySelector("#eps");
const minSamples = document.querySelector("#min-samples");
const thresholdValue = document.querySelector("#threshold-value");
const epsValue = document.querySelector("#eps-value");
const minSamplesValue = document.querySelector("#min-samples-value");
const docCount = document.querySelector("#doc-count");
const pairCount = document.querySelector("#pair-count");
const topScore = document.querySelector("#top-score");
const topScoreSub = document.querySelector("#top-score-sub");
const thresholdSub = document.querySelector("#threshold-sub");
const statusBadge = document.querySelector("#status-badge");
const statusText = document.querySelector("#status-text");
const pairNote = document.querySelector("#pair-note");
const pairsBody = document.querySelector("#pairs-body");
const heatmapSvg = document.querySelector("#heatmap");
const pcaSvg = document.querySelector("#pca");
const clustersBody = document.querySelector("#clusters-body");
const clusterNote = document.querySelector("#cluster-note");

const svgNs = "http://www.w3.org/2000/svg";
const groupColor = {
  copy: "#e15a4d",
  orig: "#58b98b",
  para: "#d49a45",
  ind: "#756f66",
};

/* ── Cluster palette for DBSCAN labels ── */
const clusterPalette = [
  "#58b98b", "#5a9fd4", "#d49a45", "#c46bb5",
  "#7cd47c", "#d4605a", "#8b8bd4", "#45c4b0",
];

function updateRange(input, output, digits = 2) {
  const min = Number(input.min);
  const max = Number(input.max);
  const value = Number(input.value);
  const percent = ((value - min) / (max - min)) * 100;
  output.value = digits === 0 ? String(value) : value.toFixed(digits);
  input.style.setProperty("--range-progress", `${percent}%`);
}

function updateControls() {
  updateRange(threshold, thresholdValue, 2);
  updateRange(eps, epsValue, 2);
  updateRange(minSamples, minSamplesValue, 0);
  thresholdSub.textContent = `above threshold ${Number(threshold.value).toFixed(2)}`;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#039;",
  })[char]);
}

function shortName(name) {
  return String(name).replace(/\.txt$/i, "");
}

function shortLabel(name) {
  return shortName(name).replace(/^nw_/, "").replace(/^db_/, "").replace(/^ml_/, "").replace(/^cs_/, "").replace(/^cc_/, "");
}

function fileGroup(name) {
  const lower = String(name).toLowerCase();
  if (lower.includes("copy")) return "copy";
  if (lower.includes("orig")) return "orig";
  if (lower.includes("para")) return "para";
  return "ind";
}

function renderFileList() {
  const files = [...fileInput.files];
  fileList.innerHTML = "";

  if (!files.length) {
    fileList.innerHTML = '<div class="file-item"><span class="file-dot"></span><span class="file-name">No files selected</span></div>';
    return;
  }

  files.forEach((file) => {
    const item = document.createElement("div");
    item.className = "file-item";
    item.innerHTML = `<span class="file-dot ${fileGroup(file.name)}"></span><span class="file-name">${escapeHtml(file.name)}</span>`;
    fileList.appendChild(item);
  });
}

function setStatus(text, state = "idle") {
  statusText.textContent = text;
  statusBadge.classList.remove("idle", "error", "complete");
  statusBadge.classList.add(state);
}

function scoreClass(score) {
  if (score >= 0.9) return "score-r";
  if (score >= 0.75) return "score-a";
  return "score-g";
}

function clearSvg(svg) {
  while (svg.firstChild) svg.removeChild(svg.firstChild);
}

function svgEl(name, attrs = {}) {
  const el = document.createElementNS(svgNs, name);
  Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, value));
  return el;
}

function valueColor(value) {
  if (value >= 0.9) return { fill: "#e15a4d", text: "#fff7f5" };
  if (value >= 0.75) return { fill: "#d49a45", text: "#120f0a" };
  if (value >= 0.5) return { fill: "#3f8b6d", text: "#f2eee7" };
  if (value >= 0.25) return { fill: "#29483d", text: "#c7d6ce" };
  return { fill: "#1d211f", text: "#756f66" };
}

/* ── Heatmap ── */
function drawHeatmap(matrix, docs) {
  clearSvg(heatmapSvg);

  if (!matrix.length) return;

  const n = docs.length;
  const lpad = 100;
  const tpad = 130;
  const cell = 42;
  const gap = 3;
  const width = Math.max(420, lpad + n * (cell + gap) + 50);
  const height = Math.max(380, tpad + n * (cell + gap) + 60);
  heatmapSvg.setAttribute("viewBox", `0 0 ${width} ${height}`);

  /* Column labels (top, vertical) */
  docs.map(shortLabel).forEach((label, index) => {
    const x = lpad + index * (cell + gap) + cell / 2;
    const y = tpad - 10;
    const text = svgEl("text", {
      x,
      y,
      "text-anchor": "start",
      "font-size": "11",
      fill: "#b9b0a5",
      transform: `rotate(-45, ${x}, ${y})`,
    });
    text.textContent = label;
    heatmapSvg.appendChild(text);
  });

  /* Row labels (left side) */
  docs.map(shortLabel).forEach((label, index) => {
    const text = svgEl("text", {
      x: lpad - 8,
      y: tpad + index * (cell + gap) + cell / 2 + 4,
      "text-anchor": "end",
      "font-size": "11",
      fill: "#b9b0a5",
    });
    text.textContent = label;
    heatmapSvg.appendChild(text);
  });

  /* Cells */
  matrix.forEach((row, rowIndex) => {
    row.forEach((value, colIndex) => {
      const { fill, text } = valueColor(value);
      const x = lpad + colIndex * (cell + gap);
      const y = tpad + rowIndex * (cell + gap);
      heatmapSvg.appendChild(svgEl("rect", {
        x,
        y,
        width: cell,
        height: cell,
        fill,
        rx: 3,
      }));

      const label = svgEl("text", {
        x: x + cell / 2,
        y: y + cell / 2 + 4,
        "text-anchor": "middle",
        "font-size": "11",
        "font-weight": "500",
        fill: text,
      });
      label.textContent = Number(value).toFixed(2);
      heatmapSvg.appendChild(label);
    });
  });

  /* Legend */
  [
    { color: "#1d211f", label: "< 0.25" },
    { color: "#29483d", label: "0.25–0.50" },
    { color: "#3f8b6d", label: "0.50–0.75" },
    { color: "#d49a45", label: "0.75–0.90" },
    { color: "#e15a4d", label: "≥ 0.90" },
  ].forEach((item, index) => {
    const lx = lpad + index * 82;
    const ly = tpad + n * (cell + gap) + 16;
    heatmapSvg.appendChild(svgEl("rect", {
      x: lx,
      y: ly,
      width: 12,
      height: 12,
      fill: item.color,
      rx: 2,
    }));
    const text = svgEl("text", {
      x: lx + 16,
      y: ly + 10,
      "font-size": "10",
      fill: "#b9b0a5",
    });
    text.textContent = item.label;
    heatmapSvg.appendChild(text);
  });
}

/* ── PCA ── */
function drawPca(points, docs) {
  clearSvg(pcaSvg);
  pcaSvg.setAttribute("viewBox", "0 0 680 200");

  /* Grid lines */
  for (let gx = 40; gx < 680; gx += 60) {
    pcaSvg.appendChild(svgEl("line", {
      x1: gx,
      x2: gx,
      y1: 10,
      y2: 190,
      stroke: "#2b2f2c",
      "stroke-width": "0.5",
    }));
  }

  for (let gy = 20; gy < 200; gy += 40) {
    pcaSvg.appendChild(svgEl("line", {
      x1: 0,
      x2: 680,
      y1: gy,
      y2: gy,
      stroke: "#2b2f2c",
      "stroke-width": "0.5",
    }));
  }

  if (!points.length) return;

  const xs = points.map((point) => point[0]);
  const ys = points.map((point) => point[1]);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const xSpan = maxX - minX || 1;
  const ySpan = maxY - minY || 1;

  /* Compute screen positions first for overlap avoidance */
  const screenPoints = points.map((point, index) => ({
    x: 80 + ((point[0] - minX) / xSpan) * 520,
    y: 25 + (1 - ((point[1] - minY) / ySpan)) * 150,
    group: fileGroup(docs[index]),
    label: shortLabel(docs[index]),
  }));

  /* Simple label offset to avoid overlap */
  screenPoints.forEach((pt, i) => {
    let offsetX = 11;
    let offsetY = 5;
    let anchor = "start";

    /* Check collisions with other points */
    for (let j = 0; j < screenPoints.length; j++) {
      if (i === j) continue;
      const dx = pt.x - screenPoints[j].x;
      const dy = pt.y - screenPoints[j].y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 35) {
        /* Place label away from the neighbor */
        if (dx < 0) {
          offsetX = -11;
          anchor = "end";
        }
        if (dy < 0) {
          offsetY = -10;
        } else {
          offsetY = 14;
        }
      }
    }

    pt.labelX = pt.x + offsetX;
    pt.labelY = pt.y + offsetY;
    pt.anchor = anchor;
  });

  screenPoints.forEach((pt) => {
    const g = svgEl("g");
    g.appendChild(svgEl("circle", {
      cx: pt.x,
      cy: pt.y,
      r: 6,
      fill: groupColor[pt.group],
      stroke: "#101211",
      "stroke-width": "1.5",
    }));

    const label = svgEl("text", {
      x: pt.labelX,
      y: pt.labelY,
      "text-anchor": pt.anchor,
      "font-size": "11",
      fill: "#b9b0a5",
    });
    label.textContent = pt.label;
    g.appendChild(label);
    pcaSvg.appendChild(g);
  });
}

/* ── Pairs table ── */
function renderPairs(pairs) {
  pairsBody.innerHTML = "";
  pairNote.textContent = `${pairs.length} flagged`;

  if (!pairs.length) {
    pairsBody.innerHTML = '<tr><td colspan="3" class="empty-state">No pairs above threshold</td></tr>';
    return;
  }

  pairs.forEach((pair) => {
    const score = Number(pair["Similarity Score"]);
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeHtml(shortName(pair["Document 1"]))}</td>
      <td>${escapeHtml(shortName(pair["Document 2"]))}</td>
      <td><span class="score-pill ${scoreClass(score)}">${score.toFixed(2)}</span></td>
    `;
    pairsBody.appendChild(row);
  });
}

/* ── DBSCAN Clusters table ── */
function renderClusters(clusters) {
  clustersBody.innerHTML = "";

  if (!clusters || !clusters.length) {
    clustersBody.innerHTML = '<tr><td colspan="2" class="empty-state">No clusters detected</td></tr>';
    clusterNote.textContent = "0 clusters found";
    return;
  }

  /* Normalize and sort: grouped clusters first (ascending), noise last */
  const parsed = clusters.map((entry) => {
    const docName = entry["Document"] || entry["document"] || "";
    const raw = entry["Cluster"] ?? entry["cluster"];
    const isNoise = raw === -1 || raw === "-1" || raw === "Noise";
    const numericLabel = isNoise ? Infinity : Number(raw);
    return { docName, raw, isNoise, numericLabel };
  });

  parsed.sort((a, b) => a.numericLabel - b.numericLabel || a.docName.localeCompare(b.docName));

  /* Count unique non-noise clusters */
  const clusterIds = new Set(parsed.filter((p) => !p.isNoise).map((p) => p.numericLabel));
  const numClusters = clusterIds.size;
  clusterNote.textContent = `${numClusters} cluster${numClusters !== 1 ? "s" : ""} found`;

  parsed.forEach((entry) => {
    const displayLabel = entry.isNoise ? "Noise" : `Cluster ${entry.raw}`;
    const badgeClass = entry.isNoise ? "noise" : "grouped";

    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeHtml(shortName(entry.docName))}</td>
      <td><span class="cluster-badge ${badgeClass}">${escapeHtml(displayLabel)}</span></td>
    `;
    clustersBody.appendChild(row);
  });
}

/* ── Summary stats ── */
function renderSummary(data) {
  const pairs = data.suspicious_pairs;
  const topPair = pairs[0];
  docCount.textContent = data.documents.length;
  pairCount.textContent = pairs.length;
  topScore.textContent = topPair ? Number(topPair["Similarity Score"]).toFixed(2) : "-";
  topScoreSub.textContent = topPair
    ? `${shortName(topPair["Document 1"])} × ${shortName(topPair["Document 2"])}`
    : "no flagged pairs";
}

/* ── Analysis runner ── */
async function runAnalysis(event) {
  event.preventDefault();
  const files = [...fileInput.files];

  if (files.length < 2) {
    setStatus("Please upload at least two files", "error");
    return;
  }

  const button = form.querySelector(".run-btn");
  button.disabled = true;
  setStatus("Analyzing…", "idle");

  const body = new FormData();
  files.forEach((file) => body.append("files", file));
  body.append("threshold", threshold.value);
  body.append("eps", eps.value);
  body.append("min_samples", minSamples.value);

  try {
    const response = await fetch("/api/analyze", { method: "POST", body });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Analysis failed");

    renderSummary(data);
    renderPairs(data.suspicious_pairs);
    drawHeatmap(data.similarity_matrix, data.documents);
    drawPca(data.pca_points, data.documents);
    renderClusters(data.clusters || []);
    setStatus("Analysis complete", "complete");
  } catch (error) {
    setStatus(error.message, "error");
  } finally {
    button.disabled = false;
  }
}

/* ── Event listeners ── */
[threshold, eps, minSamples].forEach((input) => input.addEventListener("input", updateControls));

fileInput.addEventListener("change", () => {
  renderFileList();
  setStatus(fileInput.files.length ? `${fileInput.files.length} files queued` : "Waiting for files");
});

form.addEventListener("submit", runAnalysis);

/* ── Initial render ── */
updateControls();
renderFileList();
drawHeatmap([], []);
drawPca([], []);
