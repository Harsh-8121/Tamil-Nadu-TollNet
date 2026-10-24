/* ============================================================
   TAMIL NADU TOLLNET
   COMPLETE FRONTEND JAVASCRIPT
   ============================================================ */

const API_BASE_URL = "http://127.0.0.1:8000";


/* ============================================================
   APPLICATION STATE
   ============================================================ */

const appState = {

    currentSection: "home",

    analysisPlazas: [],

    comparisonPlazas: [],

    predictionPlaza: null,

    analysisCategories: [
        "CAR_JEEP",
        "LCV",
        "BUS_TRUCK",
        "3_AXLE",
        "4_6_AXLE",
        "OSV"
    ],

    allPlazas: [],

    comparisonData: null,

    analysisData: null

};


/* ============================================================
   DOM READY
   ============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeNavigation();

        initializeHeroButton();

        initializePlazaSearch(
            "analysis",
            true
        );

        initializePlazaSearch(
            "comparison",
            true
        );

        initializePlazaSearch(
            "prediction",
            false
        );

        initializeCategorySelector();

        initializeAnalysis();

        initializePrediction();

        initializeComparison();

        initializeOutsideClick();

        initializeParallax();

        loadInitialPlazas();

        showSection("home");

    }
);


/* ============================================================
   NAVIGATION
   ============================================================ */

function initializeNavigation() {

    const navButtons =
        document.querySelectorAll(
            ".nav-button"
        );

    const featureCards =
        document.querySelectorAll(
            ".feature-card"
        );

    navButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    const section =
                        button.dataset.section;

                    showSection(section);

                }
            );

        }
    );


    featureCards.forEach(
        function (card) {

            card.addEventListener(
                "click",
                function () {

                    const section =
                        card.dataset.section;

                    showSection(section);

                }
            );

        }
    );


    const homeLink =
        document.getElementById(
            "home-link"
        );

    if (homeLink) {

        homeLink.addEventListener(
            "click",
            function () {

                showSection("home");

            }
        );

    }

}


/* ============================================================
   SHOW SECTION
   ============================================================ */

function showSection(sectionName) {

    const app =
        document.getElementById("app");

    const sections =
        document.querySelectorAll(
            ".dashboard-section"
        );

    const navButtons =
        document.querySelectorAll(
            ".nav-button"
        );


    sections.forEach(
        function (section) {

            section.classList.remove(
                "active-section"
            );

        }
    );


    navButtons.forEach(
        function (button) {

            button.classList.remove(
                "active"
            );

        }
    );


    /* HOME */

    if (sectionName === "home") {

        app.classList.remove(
            "dashboard-open"
        );

        appState.currentSection =
            "home";

        return;

    }


    /* DASHBOARD */

    const targetSection =
        document.getElementById(
            sectionName
        );

    if (!targetSection) {

        return;

    }


    app.classList.add(
        "dashboard-open"
    );


    targetSection.classList.add(
        "active-section"
    );


    const activeButton =
        document.querySelector(
            `.nav-button[data-section="${sectionName}"]`
        );

    if (activeButton) {

        activeButton.classList.add(
            "active"
        );

    }


    appState.currentSection =
        sectionName;


    /*
       When opening Comparison again,
       redraw the charts if data already exists.
    */

    if (
        sectionName === "comparison" &&
        appState.comparisonData
    ) {

        renderComparisonCharts(
            appState.comparisonData
        );

    }

}


/* ============================================================
   HERO BUTTON
   ============================================================ */

function initializeHeroButton() {

    const button =
        document.getElementById(
            "explore-button"
        );

    if (!button) {

        return;

    }


    button.addEventListener(
        "click",
        function () {

            showSection("analysis");

        }
    );

}


/* ============================================================
   LOAD ALL PLAZAS
   ============================================================ */

async function loadInitialPlazas() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/plazas`
            );


        if (!response.ok) {

            throw new Error(
                "Unable to load plazas."
            );

        }


        const data =
            await response.json();


        appState.allPlazas =
            data.results || [];


        console.log(
            "Tamil Nadu plazas loaded:",
            appState.allPlazas.length
        );


    } catch (error) {

        console.error(
            "Plaza loading error:",
            error
        );

    }

}


/* ============================================================
   PLAZA SEARCH INITIALIZER
   ============================================================ */

function initializePlazaSearch(
    type,
    multiSelect
) {

    let searchInput;

    let resultsBox;

    let selectedBox;


    if (type === "analysis") {

        searchInput =
            document.getElementById(
                "analysis-plaza-search"
            );

        resultsBox =
            document.getElementById(
                "analysis-plaza-results"
            );

        selectedBox =
            document.getElementById(
                "analysis-selected-plazas"
            );

    }


    if (type === "comparison") {

        searchInput =
            document.getElementById(
                "comparison-plaza-search"
            );

        resultsBox =
            document.getElementById(
                "comparison-plaza-results"
            );

        selectedBox =
            document.getElementById(
                "comparison-selected-plazas"
            );

    }


    if (type === "prediction") {

        searchInput =
            document.getElementById(
                "prediction-plaza-search"
            );

        resultsBox =
            document.getElementById(
                "prediction-plaza-results"
            );

        selectedBox =
            document.getElementById(
                "prediction-selected-plaza"
            );

    }


    if (
        !searchInput ||
        !resultsBox ||
        !selectedBox
    ) {

        return;

    }


    /* --------------------------------------------------------
       SEARCH INPUT
       -------------------------------------------------------- */

    searchInput.addEventListener(
        "input",
        async function () {

            const query =
                searchInput.value.trim();

            await performPlazaSearch(
                query,
                type,
                multiSelect
            );

        }
    );


    /* --------------------------------------------------------
       FOCUS
       -------------------------------------------------------- */

    searchInput.addEventListener(
        "focus",
        async function () {

            const query =
                searchInput.value.trim();

            await performPlazaSearch(
                query,
                type,
                multiSelect
            );

        }
    );


    /* --------------------------------------------------------
       ESCAPE
       -------------------------------------------------------- */

    searchInput.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {

                resultsBox.classList.remove(
                    "show"
                );

            }

        }
    );

}


/* ============================================================
   SEARCH PLAZAS
   ============================================================ */

async function performPlazaSearch(
    query,
    type,
    multiSelect
) {

    let resultsBox;


    if (type === "analysis") {

        resultsBox =
            document.getElementById(
                "analysis-plaza-results"
            );

    }


    if (type === "comparison") {

        resultsBox =
            document.getElementById(
                "comparison-plaza-results"
            );

    }


    if (type === "prediction") {

        resultsBox =
            document.getElementById(
                "prediction-plaza-results"
            );

    }


    if (!resultsBox) {

        return;

    }


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/plazas/search?q=${encodeURIComponent(query)}&limit=100`
            );


        if (!response.ok) {

            throw new Error(
                "Plaza search failed."
            );

        }


        const data =
            await response.json();


        renderPlazaResults(
            data.results || [],
            type,
            multiSelect
        );


    } catch (error) {

        console.error(
            "Plaza search error:",
            error
        );


        resultsBox.innerHTML = `
            <div class="search-result-item">
                <span>
                    Unable to connect to backend
                </span>
            </div>
        `;


        resultsBox.classList.add(
            "show"
        );

    }

}


/* ============================================================
   RENDER PLAZA SEARCH RESULTS
   ============================================================ */

function renderPlazaResults(
    plazas,
    type,
    multiSelect
) {

    let resultsBox;


    if (type === "analysis") {

        resultsBox =
            document.getElementById(
                "analysis-plaza-results"
            );

    }


    if (type === "comparison") {

        resultsBox =
            document.getElementById(
                "comparison-plaza-results"
            );

    }


    if (type === "prediction") {

        resultsBox =
            document.getElementById(
                "prediction-plaza-results"
            );

    }


    if (!resultsBox) {

        return;

    }


    resultsBox.innerHTML = "";


    /*
       Comparison gets a larger scrollable
       result area.
    */

    if (type === "comparison") {

        resultsBox.style.maxHeight =
            "300px";

        resultsBox.style.overflowY =
            "auto";

        resultsBox.style.position =
            "absolute";

        resultsBox.style.zIndex =
            "9999";

    }


    if (plazas.length === 0) {

        resultsBox.innerHTML = `
            <div class="search-result-item">
                <span>
                    No matching toll plaza found
                </span>
            </div>
        `;

        resultsBox.classList.add(
            "show"
        );

        return;

    }


    plazas.forEach(
        function (plaza) {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "search-result-item";


            const name =
                document.createElement(
                    "span"
                );


            name.textContent =
                plaza.PLAZA_NAME;


            const id =
                document.createElement(
                    "small"
                );


            id.textContent =
                plaza.PLAZA_ID;


            item.appendChild(name);

            item.appendChild(id);


            item.addEventListener(
                "click",
                function (event) {

                    event.stopPropagation();

                    selectPlaza(
                        plaza,
                        type,
                        multiSelect
                    );


                    /*
                       For comparison we keep
                       the search box open so
                       multiple plazas can be
                       selected quickly.
                    */

                    if (
                        type === "comparison"
                    ) {

                        resultsBox.classList.add(
                            "show"
                        );

                    } else {

                        resultsBox.classList.remove(
                            "show"
                        );

                    }

                }
            );


            resultsBox.appendChild(
                item
            );

        }
    );


    resultsBox.classList.add(
        "show"
    );

}


/* ============================================================
   SELECT PLAZA
   ============================================================ */

function selectPlaza(
    plaza,
    type,
    multiSelect
) {

    if (type === "analysis") {

        addAnalysisPlaza(
            plaza
        );

    }


    if (type === "comparison") {

        addComparisonPlaza(
            plaza
        );

    }


    if (type === "prediction") {

        appState.predictionPlaza =
            plaza;


        renderPredictionPlaza();


        const input =
            document.getElementById(
                "prediction-plaza-search"
            );


        if (input) {

            input.value =
                plaza.PLAZA_NAME;

        }

    }


    /*
       Don't clear comparison search.
       This makes multi-selection easier.
    */

    if (type !== "comparison") {

        clearSearchInput(
            type
        );

    }


    /*
       For comparison, clear only the text
       but keep dropdown open.
    */

    if (type === "comparison") {

        const input =
            document.getElementById(
                "comparison-plaza-search"
            );

        if (input) {

            input.value = "";

            input.focus();

        }

    }

}


/* ============================================================
   CLEAR SEARCH INPUT
   ============================================================ */

function clearSearchInput(
    type
) {

    let input;


    if (type === "analysis") {

        input =
            document.getElementById(
                "analysis-plaza-search"
            );

    }


    if (type === "comparison") {

        input =
            document.getElementById(
                "comparison-plaza-search"
            );

    }


    if (input) {

        input.value = "";

    }

}


/* ============================================================
   ANALYSIS PLAZA
   ============================================================ */

function addAnalysisPlaza(
    plaza
) {

    const alreadySelected =
        appState.analysisPlazas.some(
            function (item) {

                return (
                    item.PLAZA_ID ===
                    plaza.PLAZA_ID
                );

            }
        );


    if (alreadySelected) {

        return;

    }


    appState.analysisPlazas.push(
        plaza
    );


    renderAnalysisPlazas();

}


/* ============================================================
   RENDER ANALYSIS PLAZAS
   ============================================================ */

function renderAnalysisPlazas() {

    const container =
        document.getElementById(
            "analysis-selected-plazas"
        );


    if (!container) {

        return;

    }


    container.innerHTML = "";


    appState.analysisPlazas.forEach(
        function (plaza) {

            const tag =
                createPlazaTag(
                    plaza,
                    function () {

                        removeAnalysisPlaza(
                            plaza.PLAZA_ID
                        );

                    }
                );


            container.appendChild(
                tag
            );

        }
    );

}


/* ============================================================
   REMOVE ANALYSIS PLAZA
   ============================================================ */

function removeAnalysisPlaza(
    plazaId
) {

    appState.analysisPlazas =
        appState.analysisPlazas.filter(
            function (plaza) {

                return (
                    plaza.PLAZA_ID !==
                    plazaId
                );

            }
        );


    renderAnalysisPlazas();

}


/* ============================================================
   COMPARISON PLAZA
   ============================================================ */

function addComparisonPlaza(
    plaza
) {

    const alreadySelected =
        appState.comparisonPlazas.some(
            function (item) {

                return (
                    item.PLAZA_ID ===
                    plaza.PLAZA_ID
                );

            }
        );


    if (alreadySelected) {

        return;

    }


    appState.comparisonPlazas.push(
        plaza
    );


    renderComparisonPlazas();

}


/* ============================================================
   RENDER COMPARISON PLAZAS
   ============================================================ */

function renderComparisonPlazas() {

    const container =
        document.getElementById(
            "comparison-selected-plazas"
        );


    if (!container) {

        return;

    }


    container.innerHTML = "";


    appState.comparisonPlazas.forEach(
        function (plaza) {

            const tag =
                createPlazaTag(
                    plaza,
                    function () {

                        removeComparisonPlaza(
                            plaza.PLAZA_ID
                        );

                    }
                );


            container.appendChild(
                tag
            );

        }
    );

}


/* ============================================================
   REMOVE COMPARISON PLAZA
   ============================================================ */

function removeComparisonPlaza(
    plazaId
) {

    appState.comparisonPlazas =
        appState.comparisonPlazas.filter(
            function (plaza) {

                return (
                    plaza.PLAZA_ID !==
                    plazaId
                );

            }
        );


    renderComparisonPlazas();

}


/* ============================================================
   CREATE PLAZA TAG
   ============================================================ */

function createPlazaTag(
    plaza,
    removeFunction
) {

    const tag =
        document.createElement(
            "div"
        );


    tag.className =
        "selected-plaza";


    const name =
        document.createElement(
            "span"
        );


    name.textContent =
        plaza.PLAZA_NAME;


    const remove =
        document.createElement(
            "button"
        );


    remove.type =
        "button";


    remove.innerHTML =
        "&times";


    remove.addEventListener(
        "click",
        function (event) {

            event.stopPropagation();

            removeFunction();

        }
    );


    tag.appendChild(name);

    tag.appendChild(remove);


    return tag;

}


/* ============================================================
   PREDICTION PLAZA
   ============================================================ */

function renderPredictionPlaza() {

    const container =
        document.getElementById(
            "prediction-selected-plaza"
        );


    if (!container) {

        return;

    }


    container.innerHTML = "";


    if (!appState.predictionPlaza) {

        return;

    }


    const tag =
        createPlazaTag(
            appState.predictionPlaza,
            function () {

                appState.predictionPlaza =
                    null;


                const input =
                    document.getElementById(
                        "prediction-plaza-search"
                    );


                if (input) {

                    input.value = "";

                }


                renderPredictionPlaza();

            }
        );


    container.appendChild(
        tag
    );

}



/* ============================================================
   ANALYSIS INITIALIZATION
   ============================================================ */

function initializeAnalysis() {
    const button = document.getElementById("analysis-button");
    const downloadButton = document.getElementById("analysis-download");

    if (button) {
        button.addEventListener("click", async function () {
            await runAnalysis();
        });
    }

    if (downloadButton) {
        downloadButton.addEventListener("click", downloadAnalysisCSV);
    }
}


/* ============================================================
   RUN ANALYSIS
   ============================================================ */

async function runAnalysis() {
    const button = document.getElementById("analysis-button");
    const table = document.getElementById("analysis-table");

    const yearElement = document.getElementById("analysis-year");
    const monthElement = document.getElementById("analysis-month");

    const year = yearElement ? yearElement.value : "all";
    const month = monthElement ? monthElement.value : "all";

    const selectedPlazaIds = appState.analysisPlazas.map(function (plaza) {
        return plaza.PLAZA_ID;
    });

    const categories = appState.analysisCategories || [];

    if (categories.length === 0) {
        showAnalysisError("Please select at least one vehicle category.");
        return;
    }

    const allCategoryValues = [
        "CAR_JEEP", "LCV", "BUS_TRUCK", "3_AXLE", "4_6_AXLE", "OSV"
    ];

    const categoryParameter =
        categories.length === allCategoryValues.length
            ? "ALL"
            : categories.join(",");

    const parameters = new URLSearchParams();
    parameters.set(
        "plaza_ids",
        selectedPlazaIds.length > 0 ? selectedPlazaIds.join(",") : "ALL"
    );
    parameters.set("year", year || "all");
    parameters.set("month", month || "all");
    parameters.set("categories", categoryParameter);

    if (button) {
        button.disabled = true;
        button.innerHTML = '<span>ANALYZING...</span><span>&rarr;</span>';
    }

    if (table) {
        table.innerHTML = '<div class="empty-message">Loading filtered records...</div>';
    }

    try {
        const url = `${API_BASE_URL}/analysis?${parameters.toString()}`;
        console.log("Analysis request:", url);

        const response = await fetch(url);
        const data = await response.json();

        if (!response.ok) {
            let message = data.detail || "Analysis failed.";
            if (typeof message !== "string") {
                message = message.message || JSON.stringify(message);
            }
            throw new Error(message);
        }

        appState.analysisData = data;
        renderAnalysisResults(data);
    } catch (error) {
        console.error("Analysis error:", error);
        showAnalysisError(error.message || "Unable to load analysis data.");
    } finally {
        if (button) {
            button.disabled = false;
            button.innerHTML = '<span>ANALYZE</span><span>&rarr;</span>';
        }
    }
}


/* ============================================================
   RENDER ANALYSIS RESULTS
   ============================================================ */

function renderAnalysisResults(data) {
    const kpis = data.kpis || {};
    const trafficStats = (data.statistics || {}).traffic || {};

    setAnalysisText("analysis-total-traffic", formatNumber(kpis.total_traffic));
    setAnalysisText("analysis-total-revenue", formatCurrency(kpis.total_revenue));
    setAnalysisText("analysis-average-traffic", formatNumber(kpis.average_traffic));
    setAnalysisText("analysis-revenue-per-vehicle", formatCurrency(kpis.revenue_per_vehicle));

    setAnalysisText("analysis-median-traffic", formatNumber(trafficStats.median));
    setAnalysisText("analysis-min-traffic", formatNumber(trafficStats.minimum));
    setAnalysisText("analysis-max-traffic", formatNumber(trafficStats.maximum));
    setAnalysisText("analysis-std-traffic", formatNumber(trafficStats.standard_deviation));
    setAnalysisText("analysis-variance-traffic", formatNumber(trafficStats.variance));

    const correlation = kpis.traffic_revenue_correlation;
    setAnalysisText(
        "analysis-correlation",
        correlation === null || correlation === undefined
            ? "N/A"
            : Number(correlation).toFixed(3)
    );

    renderAnalysisMainChart(data.monthly || []);
    renderAnalysisCategoryChart(data.composition || []);
    renderAnalysisTable(data.records || []);
}


/* ============================================================
   ANALYSIS HELPERS
   ============================================================ */

function setAnalysisText(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function showAnalysisError(message) {
    const table = document.getElementById("analysis-table");
    const mainChart = document.getElementById("analysis-main-chart");
    const categoryChart = document.getElementById("analysis-category-chart");

    if (table) {
        table.innerHTML = `
            <div class="empty-message">
                ${escapeHtml(message)}
            </div>
        `;
    }

    if (mainChart) {
        mainChart.innerHTML = '<div class="empty-message">No analysis chart available.</div>';
    }

    if (categoryChart) {
        categoryChart.innerHTML = '<div class="empty-message">No category chart available.</div>';
    }

    [
        "analysis-total-traffic",
        "analysis-total-revenue",
        "analysis-average-traffic",
        "analysis-revenue-per-vehicle",
        "analysis-median-traffic",
        "analysis-min-traffic",
        "analysis-max-traffic",
        "analysis-std-traffic",
        "analysis-variance-traffic",
        "analysis-correlation"
    ].forEach(function (id) {
        setAnalysisText(id, "â€”");
    });
}


/* ============================================================
   TRAFFIC AND REVENUE MONTHLY CHART
   ============================================================ */

function renderAnalysisMainChart(monthlyData) {
    const container = document.getElementById("analysis-main-chart");
    if (!container) {
        return;
    }

    if (!monthlyData || monthlyData.length === 0) {
        container.innerHTML = '<div class="empty-message">No monthly trend data available.</div>';
        return;
    }

    const data = monthlyData.slice().sort(function (a, b) {
        return String(a.month || "").localeCompare(String(b.month || ""));
    });

    const width = 1000;
    const height = 360;
    const left = 75;
    const right = 75;
    const top = 35;
    const bottom = 70;
    const chartWidth = width - left - right;
    const chartHeight = height - top - bottom;

    const maxTraffic = Math.max(...data.map(function (item) {
        return Number(item.traffic || 0);
    }), 1);

    const maxRevenue = Math.max(...data.map(function (item) {
        return Number(item.revenue || 0);
    }), 1);

    let svg = `
        <svg viewBox="0 0 ${width} ${height}" width="100%" height="100%"
             preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
            <line x1="${left}" y1="${top}" x2="${left}" y2="${height - bottom}"
                  stroke="#9aae9f" stroke-width="1"/>
            <line x1="${width - right}" y1="${top}" x2="${width - right}" y2="${height - bottom}"
                  stroke="#9aae9f" stroke-width="1"/>
            <line x1="${left}" y1="${height - bottom}" x2="${width - right}" y2="${height - bottom}"
                  stroke="#9aae9f" stroke-width="1"/>
    `;

    for (let i = 0; i <= 4; i++) {
        const y = top + chartHeight * i / 4;
        const trafficTick = maxTraffic * (1 - i / 4);
        const revenueTick = maxRevenue * (1 - i / 4);

        svg += `
            <line x1="${left}" y1="${y}" x2="${width - right}" y2="${y}"
                  stroke="#dfe8df" stroke-width="1" stroke-dasharray="3 5"/>
            
            <text x="${left - 10}" y="${y + 4}" text-anchor="end" font-size="13" font-weight="600" fill="#34483A">${escapeHtml(shortNumber(trafficTick, "TRAFFIC"))}</text>
            <text x="${width - right + 10}" y="${y + 4}" text-anchor="start" font-size="13" font-weight="600" fill="#34483A">${escapeHtml(shortNumber(revenueTick, "REVENUE"))}</text>

        `;
    }

    const trafficPoints = [];
    const revenuePoints = [];

    data.forEach(function (item, index) {
        const x = data.length === 1
            ? left + chartWidth / 2
            : left + chartWidth * index / (data.length - 1);

        const traffic = Number(item.traffic || 0);
        const revenue = Number(item.revenue || 0);

        trafficPoints.push({
            x: x,
            y: height - bottom - (traffic / maxTraffic) * chartHeight,
            value: traffic,
            month: item.month
        });

        revenuePoints.push({
            x: x,
            y: height - bottom - (revenue / maxRevenue) * chartHeight,
            value: revenue,
            month: item.month
        });

        if (data.length <= 18 || index % 2 === 0 || index === data.length - 1) {
            svg += `
                <text x="${x}" y="${height - bottom + 22}" text-anchor="middle"
                      font-size="13" font-weight="600" fill="#34483A"
                      transform="rotate(-30 ${x} ${height - bottom + 22})">
                    ${escapeHtml(formatShortMonth(item.month))}
                </text>
            `;
        }
    });

    let trafficPath = "";
    let revenuePath = "";

    trafficPoints.forEach(function (point, index) {
        trafficPath += `${index === 0 ? "M" : "L"} ${point.x} ${point.y} `;
    });

    revenuePoints.forEach(function (point, index) {
        revenuePath += `${index === 0 ? "M" : "L"} ${point.x} ${point.y} `;
    });

    svg += `
        <path d="${trafficPath}" fill="none" stroke="#355d45" stroke-width="3"
              stroke-linejoin="round" stroke-linecap="round"/>
        <path d="${revenuePath}" fill="none" stroke="#b58b4b" stroke-width="3"
              stroke-linejoin="round" stroke-linecap="round"/>
    `;

    trafficPoints.forEach(function (point) {
        svg += `
            <circle cx="${point.x}" cy="${point.y}" r="3.5" fill="#355d45">
                <title>${escapeHtml(point.month)} : Traffic: ${formatNumber(point.value)}</title>
            </circle>
        `;
    });

    revenuePoints.forEach(function (point) {
        svg += `
            <circle cx="${point.x}" cy="${point.y}" r="3.5" fill="#b58b4b">
                <title>${escapeHtml(point.month)} : Revenue: ${formatCurrency(point.value)}</title>
            </circle>
        `;
    });

    svg += `
        <text x="${left}" y="18" font-size="12" font-weight="600" fill="#355d45">Traffic</text>
        <text x="${width - right}" y="18" text-anchor="end" font-size="12"
              font-weight="600" fill="#9a7136">Revenue</text>
        </svg>
    `;

    container.innerHTML = svg;
}


/* ============================================================
   VEHICLE CATEGORY CHART
   ============================================================ */

function renderAnalysisCategoryChart(composition) {
    const container = document.getElementById("analysis-category-chart");
    if (!container) {
        return;
    }

    if (!composition || composition.length === 0) {
        container.innerHTML = '<div class="empty-message">No vehicle category data available.</div>';
        return;
    }

    const chartRows = composition.map(function (item) {
        return {
            PLAZA_NAME: item.category,
            traffic: Number(item.traffic || 0),
            revenue: Number(item.revenue || 0)
        };
    });

    drawBarChart(container, chartRows, "TRAFFIC");
}


/* ============================================================
   FILTERED RECORDS TABLE
   ============================================================ */

function renderAnalysisTable(records) {
    const container = document.getElementById("analysis-table");
    if (!container) {
        return;
    }

    if (!records || records.length === 0) {
        container.innerHTML = '<div class="empty-message">No records match the selected filters.</div>';
        return;
    }

    const columns = [
        { key: "PLAZA_NAME", label: "Toll Plaza", format: "text" },
        { key: "PLAZA_ID", label: "Plaza ID", format: "text" },
        { key: "YEAR", label: "Year", format: "text" },
        { key: "MONTH_NUMBER", label: "Month", format: "month" },
        { key: "ANALYSIS_TRAFFIC", label: "Selected Traffic", format: "number" },
        { key: "ANALYSIS_REVENUE", label: "Selected Revenue", format: "currency" },
        { key: "TOTAL_CNT", label: "Total Traffic", format: "number" },
        { key: "TOTAL_AMT", label: "Total Revenue", format: "currency" }
    ];

    let html = `
        <table>
            <thead>
                <tr>
                    ${columns.map(function (column) {
                        return `<th>${escapeHtml(column.label)}</th>`;
                    }).join("")}
                </tr>
            </thead>
            <tbody>
    `;

    records.forEach(function (record) {
        html += "<tr>";

        columns.forEach(function (column) {
            let value = record[column.key];

            if (column.format === "number") {
                value = formatNumber(value);
            } else if (column.format === "currency") {
                value = formatCurrency(value);
            } else if (column.format === "month") {
                const monthNames = [
                    "", "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ];
                value = monthNames[Number(value)] || "â€”";
            } else {
                value = value === null || value === undefined ? "â€”" : String(value);
            }

            html += `<td>${escapeHtml(value)}</td>`;
        });

        html += "</tr>";
    });

    html += `
            </tbody>
        </table>
        <div class="table-result-count">${formatNumber(records.length)} record(s)</div>
    `;

    container.innerHTML = html;
}


/* ============================================================
   EXPORT ANALYSIS RESULTS AS CSV
   ============================================================ */

function downloadAnalysisCSV() {
    const data = appState.analysisData;

    if (!data || !data.records || data.records.length === 0) {
        alert("Run an analysis before exporting records.");
        return;
    }

    const columns = [
        "PLAZA_ID", "PLAZA_NAME", "PIU", "RO", "STATE",
        "YEAR", "MONTH_NUMBER", "ANALYSIS_TRAFFIC", "ANALYSIS_REVENUE",
        "TOTAL_CNT", "TOTAL_AMT", "CAR_JEEP_CNT", "CAR_JEEP_AMT",
        "LCV_CNT", "LCV_AMT", "BUS_TRUCK_CNT", "BUS_TRUCK_AMT",
        "3_AXLE_CNT", "3_AXLE_AMT", "4_6_AXLE_CNT", "4_6_AXLE_AMT",
        "OSV_CNT", "OSV_AMT"
    ];

    const csvEscape = function (value) {
        const text = value === null || value === undefined ? "" : String(value);
        return `"${text.replace(/"/g, '""')}"`;
    };

    const rows = [columns.map(csvEscape).join(",")];

    data.records.forEach(function (record) {
        rows.push(columns.map(function (column) {
            return csvEscape(record[column]);
        }).join(","));
    });

    const blob = new Blob(["\uFEFF" + rows.join("\r\n")], {
        type: "text/csv;charset=utf-8;"
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "tamil_nadu_tollnet_analysis.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
}




/* ============================================================
   CATEGORY SELECTOR
   ============================================================ */

function initializeCategorySelector() {

    const selector =
        document.getElementById(
            "analysis-category-select"
        );


    if (!selector) {

        return;

    }


    const button =
        selector.querySelector(
            ".multi-select-button"
        );


    const dropdown =
        selector.querySelector(
            ".multi-select-dropdown"
        );


    if (!button || !dropdown) {

        return;

    }


    button.addEventListener(
        "click",
        function (event) {

            event.stopPropagation();

            selector.classList.toggle(
                "open"
            );

        }
    );


    const checkboxes =
        dropdown.querySelectorAll(
            'input[type="checkbox"]'
        );


    checkboxes.forEach(
        function (checkbox) {

            checkbox.addEventListener(
                "change",
                function () {

                    updateCategoryState(
                        checkboxes,
                        button
                    );

                }
            );

        }
    );


    const selectAll =
        document.getElementById(
            "analysis-category-all"
        );


    const clearAll =
        document.getElementById(
            "analysis-category-none"
        );


    if (selectAll) {

        selectAll.addEventListener(
            "click",
            function () {

                checkboxes.forEach(
                    function (checkbox) {

                        checkbox.checked =
                            true;

                    }
                );


                updateCategoryState(
                    checkboxes,
                    button
                );

            }
        );

    }


    if (clearAll) {

        clearAll.addEventListener(
            "click",
            function () {

                checkboxes.forEach(
                    function (checkbox) {

                        checkbox.checked =
                            false;

                    }
                );


                updateCategoryState(
                    checkboxes,
                    button
                );

            }
        );

    }


    updateCategoryState(
        checkboxes,
        button
    );

}


/* ============================================================
   UPDATE CATEGORY STATE
   ============================================================ */

function updateCategoryState(
    checkboxes,
    button
) {

    const selected = [];


    checkboxes.forEach(
        function (checkbox) {

            if (checkbox.checked) {

                selected.push(
                    checkbox.value
                );

            }

        }
    );


    appState.analysisCategories =
        selected;


    const label =
        button.querySelector(
            "span"
        );


    if (!label) {

        return;

    }


    if (selected.length === 0) {

        label.textContent =
            "No Categories";

    }

    else if (
        selected.length ===
        checkboxes.length
    ) {

        label.textContent =
            "All Categories";

    }

    else {

        label.textContent =
            `${selected.length} Categories Selected`;

    }

}


/* ============================================================
   PREDICTION
   ============================================================ */

function initializePrediction() {

    const button =
        document.getElementById(
            "prediction-button"
        );


    if (!button) {

        return;

    }


    button.addEventListener(
        "click",
        async function () {

            await runPrediction();

        }
    );

}


/* ============================================================
   RUN PREDICTION
   ============================================================ */

async function runPrediction() {

    const result =
        document.getElementById(
            "prediction-result"
        );


    if (!result) {

        return;

    }


    if (!appState.predictionPlaza) {

        showPredictionMessage(
            "Please select a toll plaza first."
        );

        return;

    }


    const selectedTarget =
        document.querySelector(
            'input[name="prediction-target"]:checked'
        );


    if (!selectedTarget) {

        showPredictionMessage(
            "Please select a prediction target."
        );

        return;

    }


    const target =
        selectedTarget.value;


    const monthSelect =
        document.getElementById(
            "prediction-month"
        );


    const forecastMonth =
        monthSelect
            ? monthSelect.value
            : "";


    if (!forecastMonth) {

        showPredictionMessage(
            "Please select a forecast month."
        );

        return;

    }


    result.innerHTML = `
        <div class="empty-message large">

            <div class="result-symbol">
                &#8599 
            </div>

            <h3>
                Generating Prediction
            </h3>

            <p>
                Please wait while the model analyzes
                the latest toll plaza information.
            </p>

        </div>
    `;


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/predict`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        plaza_id:
                            appState
                                .predictionPlaza
                                .PLAZA_ID,

                        target:
                            target,

                        forecast_month:
                            forecastMonth

                    })

                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Prediction failed."
            );

        }


        renderPredictionResult(
            data
        );


    } catch (error) {

        console.error(
            "Prediction error:",
            error
        );


        showPredictionMessage(
            error.message
        );

    }

}


/* ============================================================
   PREDICTION RESULT
   ============================================================ */

function renderPredictionResult(
    data
) {

    const result =
        document.getElementById(
            "prediction-result"
        );


    if (!result) {

        return;

    }


    const isTraffic =
        data.target ===
        "Traffic Forecast" ||
        data.target ===
        "Next-Month Traffic";


    const formattedPrediction =
        isTraffic
            ? formatNumber(
                data.prediction
            )
            : formatCurrency(
                data.prediction
            );


    const formattedCurrent =
        isTraffic
            ? formatNumber(
                data.current_value
            )
            : formatCurrency(
                data.current_value
            );


    let changeText = "â€”";


    if (
        data.expected_change_percent !== null &&
        data.expected_change_percent !== undefined &&
        Number.isFinite(
            Number(
                data.expected_change_percent
            )
        )
    ) {

        const change =
            Number(
                data.expected_change_percent
            );


        const sign =
            change >= 0
                ? "+"
                : "";


        changeText =
            `${sign}${change.toFixed(2)}%`;

    }


    result.innerHTML = `

        <div class="prediction-result-content">

            <div class="prediction-heading">

                <div>

                    <span class="section-kicker">
                        PREDICTION RESULT
                    </span>

                    <h3>
                        ${escapeHtml(
                            data.plaza_name
                        )}
                    </h3>

                </div>

                <div class="prediction-badge">

                    ${escapeHtml(
                        data.model
                    )}

                </div>

            </div>


            <div class="prediction-value">

                <span class="prediction-value-label">

                    PREDICTED
                    ${isTraffic ? "TRAFFIC" : "REVENUE"}

                </span>


                <div class="prediction-number">

                    ${formattedPrediction}

                </div>

            </div>


            <div class="prediction-meta">

                <div class="prediction-meta-item">

                    <span>
                        Latest Actual
                    </span>

                    <strong>
                        ${formattedCurrent}
                    </strong>

                </div>


                <div class="prediction-meta-item">

                    <span>
                        Predicted Month
                    </span>

                    <strong>
                        ${formatDate(
                            data.predicted_month
                        )}
                    </strong>

                </div>


                <div class="prediction-meta-item">

                    <span>
                        Expected Change
                    </span>

                    <strong>
                        ${changeText}
                    </strong>

                </div>

            </div>

        </div>

    `;

}


/* ============================================================
   PREDICTION ERROR
   ============================================================ */

function showPredictionMessage(
    message
) {

    const result =
        document.getElementById(
            "prediction-result"
        );


    if (!result) {

        return;

    }


    result.innerHTML = `

        <div class="empty-message large">

            <div class="result-symbol">
                !
            </div>

            <h3>
                Prediction Unavailable
            </h3>

            <p>
                ${escapeHtml(
                    message
                )}
            </p>

        </div>

    `;

}


/* ============================================================
   COMPARISON INITIALIZATION
   ============================================================ */

function initializeComparison() {

    const button =
        document.getElementById(
            "comparison-button"
        );


    if (!button) {

        return;

    }


    button.addEventListener(
        "click",
        async function () {

            await runComparison();

        }
    );

}


/* ============================================================
   RUN COMPARISON
   ============================================================ */

async function runComparison() {

    if (
        appState.comparisonPlazas.length === 0
    ) {

        alert(
            "Please select at least one toll plaza."
        );

        return;

    }


    const categoryElement =
        document.getElementById(
            "comparison-category"
        );


    const periodElement =
        document.getElementById(
            "comparison-period"
        );


    const category =
        categoryElement
            ? categoryElement.value
            : "ALL";


    const period =
        periodElement
            ? periodElement.value
            : "all";


    const plazaIds =
        appState.comparisonPlazas
            .map(
                function (plaza) {

                    return plaza.PLAZA_ID;

                }
            )
            .join(",");


    const button =
        document.getElementById(
            "comparison-button"
        );


    if (button) {

        button.disabled = true;

        button.innerHTML =
            `
            <span>
                LOADING...
            </span>

            <span>
                â†»
            </span>
            `;

    }


    try {

        const url =
            `${API_BASE_URL}/comparison` +
            `?plaza_ids=${encodeURIComponent(plazaIds)}` +
            `&category=${encodeURIComponent(category)}` +
            `&period=${encodeURIComponent(period)}`;


        console.log(
            "Comparison request:",
            url
        );


        const response =
            await fetch(url);


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Comparison failed."
            );

        }


        appState.comparisonData =
            data;


        renderComparisonResults(
            data
        );


        renderComparisonCharts(
            data
        );


    } catch (error) {

        console.error(
            "Comparison error:",
            error
        );


        showComparisonError(
            error.message
        );


    } finally {

        if (button) {

            button.disabled = false;

            button.innerHTML =
                `
                <span>
                    COMPARE
                </span>

                <span>
                    &#8594
                </span>
                `;

        }

    }

}


/* ============================================================
   COMPARISON KPI RESULTS
   ============================================================ */

function renderComparisonResults(
    data
) {

    if (
        !data.summary ||
        data.summary.length === 0
    ) {
        return;
    }

    const highestTraffic =
        [...data.summary].sort(
            function (a, b) {
                return (
                    Number(b.traffic ?? b.TRAFFIC ?? 0) -
                    Number(a.traffic ?? a.TRAFFIC ?? 0)
                );
            }
        )[0];

    const highestRevenue =
        [...data.summary].sort(
            function (a, b) {
                return (
                    Number(b.revenue ?? b.REVENUE ?? 0) -
                    Number(a.revenue ?? a.REVENUE ?? 0)
                );
            }
        )[0];

    const highestTrafficElement =
        document.getElementById(
            "comparison-highest-traffic"
        );

    if (highestTrafficElement) {
        const traffic =
            highestTraffic.traffic ??
            highestTraffic.TRAFFIC ??
            0;

        highestTrafficElement.textContent =
            `${highestTraffic.PLAZA_NAME}  ${formatNumber(traffic)}`;
    }

    const highestRevenueElement =
        document.getElementById(
            "comparison-highest-revenue"
        );

    if (highestRevenueElement) {
        const revenue =
            highestRevenue.revenue ??
            highestRevenue.REVENUE ??
            0;

        highestRevenueElement.textContent =
            `${highestRevenue.PLAZA_NAME} ${formatCurrency(revenue)}`;
    }

    const trafficGrowthElement =
        document.getElementById(
            "comparison-traffic-growth"
        );

    if (trafficGrowthElement) {
        const trafficGrowth =
            data.traffic_growth_percent ??
            data.traffic_growth ??
            0;

        trafficGrowthElement.textContent =
            `${Number(trafficGrowth) >= 0 ? "+" : ""}${Number(trafficGrowth).toFixed(2)}%`;
    }

    const revenueGrowthElement =
        document.getElementById(
            "comparison-revenue-growth"
        );

    if (revenueGrowthElement) {
        const revenueGrowth =
            data.revenue_growth_percent ??
            data.revenue_growth ??
            0;

        revenueGrowthElement.textContent =
            `${Number(revenueGrowth) >= 0 ? "+" : ""}${Number(revenueGrowth).toFixed(2)}%`;
    }

}



/* ============================================================
   COMPARISON CHARTS
   ============================================================ */

function renderComparisonCharts(
    data
) {

    const trafficContainer =
        document.getElementById(
            "comparison-traffic-chart"
        );


    const revenueContainer =
        document.getElementById(
            "comparison-revenue-chart"
        );


    const trendContainer =
        document.getElementById(
            "comparison-trend-chart"
        );


    if (
        !trafficContainer ||
        !revenueContainer ||
        !trendContainer
    ) {

        console.error(
            "Comparison chart containers not found."
        );

        return;

    }


    if (
        !data.summary ||
        data.summary.length === 0
    ) {

        return;

    }


    drawBarChart(
        trafficContainer,
        data.summary,
        "TRAFFIC"
    );


    drawBarChart(
        revenueContainer,
        data.summary,
        "REVENUE"
    );


    drawTrendChart(
        trendContainer,
        data.monthly
    );

}

function getPlazaColor(plazaName) {
    const colors = [
        "#52745D",
        "#B58B4B",
        "#6687A5",
        "#9B718A",
        "#7D8B52",
        "#C4775A",
        "#7A75A8",
        "#4F9690"
    ];

    let hash = 0;

    for (let i = 0; i < plazaName.length; i++) {
        hash = (hash * 31 + plazaName.charCodeAt(i)) % colors.length;
    }

    return colors[hash];
}

/* ============================================================
   BAR CHART
   Pure SVG â€” no external chart library needed.
   ============================================================ */

function drawBarChart(
    container,
    summary,
    metric
) {

    container.innerHTML = "";

    if (
        !summary ||
        summary.length === 0
    ) {
        container.innerHTML = `
            <div class="empty-message">
                No comparison data available.
            </div>
        `;
        return;
    }

    const width = 900;
    const height = 330;
    const left = 80;
    const right = 30;
    const top = 30;
    const bottom = 90;

    const chartWidth =
        width - left - right;

    const chartHeight =
        height - top - bottom;

    const values =
        summary.map(
            function (item) {
                return Number(
                    metric === "TRAFFIC"
                        ? item.traffic ?? item.TRAFFIC ?? 0
                        : item.revenue ?? item.REVENUE ?? 0
                );
            }
        );

    const labels =
        summary.map(
            function (item) {
                return item.PLAZA_NAME;
            }
        );

    const maxValue =
        Math.max(...values, 1);

    const barGap = 18;

    const barWidth =
        Math.max(
            25,
            (
                chartWidth -
                (
                    barGap *
                    (values.length + 1)
                )
            ) /
            values.length
        );

    let svg = `
        <svg
            viewBox="0 0 ${width} ${height}"
            width="100%"
            height="100%"
            preserveAspectRatio="none"
            xmlns="http://www.w3.org/2000/svg"
        >

            <line
                x1="${left}"
                y1="${top}"
                x2="${left}"
                y2="${height - bottom}"
                stroke="#9aae9f"
                stroke-width="1"
            />

            <line
                x1="${left}"
                y1="${height - bottom}"
                x2="${width - right}"
                y2="${height - bottom}"
                stroke="#9aae9f"
                stroke-width="1"
            />
    `;

    for (
        let i = 0;
        i <= 4;
        i++
    ) {

        const y =
            top +
            (
                chartHeight *
                i /
                4
            );

        const value =
            maxValue *
            (
                1 -
                i / 4
            );

        svg += `
            <line
                x1="${left}"
                y1="${y}"
                x2="${width - right}"
                y2="${y}"
                stroke="#dfe8df"
                stroke-width="1"
                stroke-dasharray="3 5"
            />

            <text
                x="${left - 10}"
                y="${y + 4}"
                text-anchor="end"
                font-size="16"
                fill="#000000"
                font-weight="600"
            >
                ${escapeHtml(
                    shortNumber(
                        value,
                        metric
                    )
                )}
            </text>
        `;
    }

    values.forEach(
        function (value, index) {

            const x =
                left +
                barGap +
                index *
                (
                    barWidth +
                    barGap
                );

            const barHeight =
                (
                    value /
                    maxValue
                ) *
                chartHeight;

            const y =
                height -
                bottom -
                barHeight;

            const displayName =
                shortenLabel(
                    labels[index],
                    18
                );

            svg += `
                <rect
                    x="${x}"
                    y="${y}"
                    width="${barWidth}"
                    height="${barHeight}"
                    rx="6"
                    fill="${getPlazaColor(labels[index])}"
                    opacity="0.88"
                >
                    <title>
                        ${escapeHtml(
                            labels[index]
                        )}:
                        ${
                            metric === "TRAFFIC"
                                ? formatNumber(value)
                                : formatCurrency(value)
                        }
                    </title>
                </rect>

                <text
                    x="${x + barWidth / 2}"
                    y="${Math.max(y - 8, 15)}"
                    text-anchor="middle"
                    font-size="14"
                    font-weight="700"
                    fill="#000000"
                >
                    ${shortNumber(
                        value,
                        metric
                    )}
                </text>

                <text
                    x="${x + barWidth / 2}"
                    y="${height - bottom + 18}"
                    text-anchor="middle"
                    font-size="16"
                    font-weight = "600"
                    fill="#000000"
                >
                    ${escapeHtml(displayName)}
                </text>
            `;
        }
    );

    svg += `
        </svg>
    `;

    container.innerHTML = svg;
}



/* ============================================================
   TREND LINE CHART
   ============================================================ */

function drawTrendChart(
    container,
    monthlyData
) {

    container.innerHTML = "";

    if (
        !monthlyData ||
        monthlyData.length === 0
    ) {
        container.innerHTML = `
            <div class="empty-message">
                No monthly trend data available.
            </div>
        `;
        return;
    }

    const width = 1000;
    const height = 380;
    const left = 70;
    const right = 35;
    const top = 35;
    const bottom = 80;

    const chartWidth =
        width - left - right;

    const chartHeight =
        height - top - bottom;

    const months = [
        ...new Set(
            monthlyData.map(
                function (item) {
                    return (
                        item.MONTH ??
                        item.DATE ??
                        ""
                    );
                }
            )
        )
    ].sort();

    const plazas = [
        ...new Set(
            monthlyData.map(
                function (item) {
                    return item.PLAZA_NAME;
                }
            )
        )
    ];

    let maxTraffic = 1;

    monthlyData.forEach(
        function (item) {
            const value =
                Number(
                    item.traffic ??
                    item.TRAFFIC ??
                    0
                );

            if (value > maxTraffic) {
                maxTraffic = value;
            }
        }
    );

    let svg = `
        <svg
            viewBox="0 0 ${width} ${height}"
            width="100%"
            height="100%"
            preserveAspectRatio="none"
            xmlns="http://www.w3.org/2000/svg"
        >

            <line
                x1="${left}"
                y1="${top}"
                x2="${left}"
                y2="${height - bottom}"
                stroke="#9aae9f"
                stroke-width="1"
            />

            <line
                x1="${left}"
                y1="${height - bottom}"
                x2="${width - right}"
                y2="${height - bottom}"
                stroke="#9aae9f"
                stroke-width="1"
            />
    `;

    for (
        let i = 0;
        i <= 4;
        i++
    ) {

        const y =
            top +
            chartHeight *
            i /
            4;

        const value =
            maxTraffic *
            (
                1 -
                i / 4
            );

        svg += `
            <line
                x1="${left}"
                y1="${y}"
                x2="${width - right}"
                y2="${y}"
                stroke="#dfe8df"
                stroke-width="1"
                stroke-dasharray="3 5"
            />

            <text
                x="${left - 10}"
                y="${y + 4}"
                text-anchor="end"
                font-size="11"
                fill="#607265"
            >
                ${shortNumber(
                    value,
                    "TRAFFIC"
                )}
            </text>
        `;
    }

    months.forEach(
        function (month, index) {

            const x =
                months.length === 1
                    ? left
                    : left +
                        (
                            chartWidth *
                            index /
                            (months.length - 1)
                        );

            const shouldShow =
                months.length <= 18 ||
                index % 2 === 0 ||
                index === months.length - 1;

            if (!shouldShow) {
                return;
            }

            svg += `
                <text
                    x="${x}"
                    y="${height - bottom + 25}"
                    text-anchor="middle"
                    font-size="10"
                    fill="#526459"
                    transform="rotate(-35 ${x} ${height - bottom + 25})"
                >
                    ${formatShortMonth(month)}
                </text>
            `;
        }
    );

    const lineColors = plazas.map(function (plazaName) {
    return getPlazaColor(plazaName);
});

    plazas.forEach(
        function (plazaName, plazaIndex) {

            const points = [];

            months.forEach(
                function (month, monthIndex) {

                    const record =
                        monthlyData.find(
                            function (item) {

                                const itemMonth =
                                    item.MONTH ??
                                    item.DATE ??
                                    "";

                                return (
                                    item.PLAZA_NAME ===
                                    plazaName &&
                                    itemMonth ===
                                    month
                                );
                            }
                        );

                    if (!record) {
                        points.push(null);
                        return;
                    }

                    const value =
                        Number(
                            record.traffic ??
                            record.TRAFFIC ??
                            0
                        );

                    const x =
                        months.length === 1
                            ? left
                            : left +
                                (
                                    chartWidth *
                                    monthIndex /
                                    (months.length - 1)
                                );

                    const y =
                        height -
                        bottom -
                        (
                            value /
                            maxTraffic
                        ) *
                        chartHeight;

                    points.push({
                        x: x,
                        y: y,
                        value: value
                    });
                }
            );

            let path = "";
            let started = false;

            points.forEach(
                function (point) {

                    if (!point) {
                        started = false;
                        return;
                    }

                    if (!started) {
                        path +=
                            `M ${point.x} ${point.y}`;
                        started = true;
                    } else {
                        path +=
                            ` L ${point.x} ${point.y}`;
                    }
                }
            );

            const color = getPlazaColor(plazaName);

            svg += `
                <path
                    d="${path}"
                    fill="none"
                    stroke="${color}"
                    stroke-width="2.5"
                    stroke-linejoin="round"
                    stroke-linecap="round"
                >
                    <title>
                        ${escapeHtml(plazaName)}
                    </title>
                </path>
            `;

            points.forEach(
                function (point) {

                    if (!point) {
                        return;
                    }

                    svg += `
                        <circle
                            cx="${point.x}"
                            cy="${point.y}"
                            r="3.5"
                            fill="${color}"
                        >
                            <title>
                                ${escapeHtml(plazaName)}
                                :
                                ${formatNumber(point.value)}
                            </title>
                        </circle>
                    `;
                }
            );
        }
    );

    let legendX = left;

    const legendY =
        height - 15;

    plazas.forEach(
        function (plazaName, index) {

            const color = getPlazaColor(plazaName);

            const label =
                shortenLabel(
                    plazaName,
                    22
                );

            svg += `
                <circle
                    cx="${legendX}"
                    cy="${legendY - 4}"
                    r="5"
                    fill="${color}"
                />

                <text
                    x="${legendX + 9}"
                    y="${legendY}"
                    font-size="10"
                    fill="#526459"
                >
                    ${escapeHtml(label)}
                </text>
            `;

            legendX +=
                125 +
                label.length * 2;

            if (
                legendX >
                width - 150
            ) {
                legendX = left;
            }
        }
    );

    svg += `
        </svg>
    `;

    container.innerHTML = svg;
}



/* ============================================================
   COMPARISON ERROR
   ============================================================ */

function showComparisonError(
    message
) {

    const containers = [
        "comparison-traffic-chart",
        "comparison-revenue-chart",
        "comparison-trend-chart"
    ];


    containers.forEach(
        function (id) {

            const container =
                document.getElementById(
                    id
                );


            if (container) {

                container.innerHTML = `

                    <div class="empty-message">

                        <div class="result-symbol">
                            !
                        </div>

                        <h3>
                            Comparison Unavailable
                        </h3>

                        <p>
                            ${escapeHtml(
                                message
                            )}
                        </p>

                    </div>

                `;

            }

        }
    );

}


/* ============================================================
   OUTSIDE CLICK
   ============================================================ */

function initializeOutsideClick() {

    document.addEventListener(
        "click",
        function (event) {

            const searchResults =
                document.querySelectorAll(
                    ".search-results"
                );


            searchResults.forEach(
                function (box) {

                    const wrapper =
                        box.closest(
                            ".search-wrapper"
                        );


                    if (
                        wrapper &&
                        !wrapper.contains(
                            event.target
                        )
                    ) {

                        box.classList.remove(
                            "show"
                        );

                    }

                }
            );


            const category =
                document.getElementById(
                    "analysis-category-select"
                );


            if (
                category &&
                !category.contains(
                    event.target
                )
            ) {

                category.classList.remove(
                    "open"
                );

            }

        }
    );

}


/* ============================================================
   PARALLAX / 3D EFFECT
   ============================================================ */

function initializeParallax() {

    const hero =
        document.querySelector(
            ".hero-section"
        );


    const background =
        document.querySelector(
            ".hero-background"
        );


    const heroContent =
        document.querySelector(
            ".hero-content"
        );


    const featureCards =
        document.querySelectorAll(
            ".feature-card"
        );


    if (
        !hero ||
        !background
    ) {

        return;

    }


    hero.addEventListener(
        "mousemove",
        function (event) {

            const rect =
                hero.getBoundingClientRect();


            const x =
                (
                    event.clientX -
                    rect.left
                ) /
                rect.width;


            const y =
                (
                    event.clientY -
                    rect.top
                ) /
                rect.height;


            const moveX =
                (x - 0.5) * 7;


            const moveY =
                (y - 0.5) * 5;


            background.style.transform =
                `
                scale(1.035)
                translate3d(
                    ${moveX}px,
                    ${moveY}px,
                    0
                )
                `;


            if (heroContent) {

                heroContent.style.transform =
                    `
                    translate3d(
                        ${moveX * -0.18}px,
                        ${moveY * -0.12}px,
                        0
                    )
                    `;

            }


            featureCards.forEach(
                function (card, index) {

                    const depth =
                        0.08 +
                        index * 0.02;


                    card.style.transform =
                        `
                        translate3d(
                            ${moveX * depth}px,
                            ${moveY * depth}px,
                            0
                        )
                        `;

                }
            );

        }
    );


    hero.addEventListener(
        "mouseleave",
        function () {

            background.style.transform =
                "scale(1.035)";


            if (heroContent) {

                heroContent.style.transform =
                    "translate3d(0, 0, 0)";

            }


            featureCards.forEach(
                function (card) {

                    card.style.transform =
                        "";

                }
            );

        }
    );

}


/* ============================================================
   FORMAT NUMBER
   ============================================================ */

function formatNumber(
    value
) {

    const number =
        Number(value);


    if (
        !Number.isFinite(
            number
        )
    ) {

        return "â€”";

    }


    return new Intl.NumberFormat(
        "en-IN",
        {
            maximumFractionDigits: 0
        }
    ).format(
        number
    );

}


/* ============================================================
   FORMAT CURRENCY
   ============================================================ */

function formatCurrency(
    value
) {

    const number =
        Number(value);


    if (
        !Number.isFinite(
            number
        )
    ) {

        return "â€”";

    }


    return new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0
        }
    ).format(
        number
    );

}


/* ============================================================
   SHORT NUMBER
   ============================================================ */

function shortNumber(
    value,
    metric
) {

    const number =
        Number(value);


    if (
        !Number.isFinite(
            number
        )
    ) {

        return "0";

    }


    if (metric === "REVENUE") {

        if (number >= 10000000) {

            return (
                "₹" +
                (
                    number /
                    10000000
                ).toFixed(1) +
                " Cr"
            );

        }


        if (number >= 100000) {

            return (
                "â‚¹" +
                (
                    number /
                    100000
                ).toFixed(1) +
                " L"
            );

        }


        return "â‚¹" +
            Math.round(
                number
            ).toLocaleString(
                "en-IN"
            );

    }


    if (number >= 10000000) {

        return (
            (
                number /
                10000000
            ).toFixed(1) +
            " Cr"
        );

    }


    if (number >= 100000) {

        return (
            (
                number /
                100000
            ).toFixed(1) +
            " L"
        );

    }


    if (number >= 1000) {

        return (
            (
                number /
                1000
            ).toFixed(1) +
            "K"
        );

    }


    return Math.round(
        number
    ).toString();

}


/* ============================================================
   SHORTEN LABEL
   ============================================================ */

function shortenLabel(
    value,
    maxLength
) {

    const text =
        String(value);


    if (
        text.length <= maxLength
    ) {

        return text;

    }


    return (
        text.substring(
            0,
            maxLength - 1
        )
    );

}


/* ============================================================
   SHORT MONTH
   ============================================================ */

function formatShortMonth(
    value
) {

    if (!value) {

        return "";

    }


    const parts =
        String(value).split("-");


    if (parts.length < 2) {

        return value;

    }


    const year =
        parts[0];


    const month =
        Number(
            parts[1]
        );


    const names = [
        "",
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec"
    ];


    return (
        names[month] +
        " " +
        year
    );

}


/* ============================================================
   FORMAT DATE
   ============================================================ */

function formatDate(
    value
) {

    if (!value) {

        return "â€”";

    }


    const date =
        new Date(
            value
        );


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return value;

    }


    return date.toLocaleDateString(
        "en-IN",
        {
            month: "long",
            year: "numeric"
        }
    );

}


/* ============================================================
   ESCAPE HTML
   ============================================================ */

function escapeHtml(
    value
) {

    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


/* ============================================================
   BACKEND HEALTH CHECK
   ============================================================ */

async function checkBackendHealth() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/health`
            );


        if (!response.ok) {

            throw new Error(
                "Backend unavailable"
            );

        }


        console.log(
            "Tamil Nadu TollNet backend connected."
        );


    } catch (error) {

        console.warn(
            "Backend is not running. Start 14_prediction.py."
        );

    }

}


checkBackendHealth();


/* ============================================================
   FINAL MESSAGE
   ============================================================ */

console.log(
    "Tamil Nadu TollNet frontend loaded successfully."
);