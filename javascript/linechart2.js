// Set up the area and line chart function for macroeconomic data
function createMacroeconomicChart(data) {
  // Declare the chart dimensions and margins
  const width = 928;
  const height = 500;
  const marginTop = 20;
  const marginRight = 30;
  const marginBottom = 30;
  const marginLeft = 40;

  // Declare the x (horizontal position) scale
  const x = d3.scaleUtc(
    d3.extent(data, (d) => d.Date),
    [marginLeft, width - marginRight]
  );

  // Declare the y (vertical position) scale
  const y = d3.scaleLinear(
    [0, d3.max(data, (d) => d.Value)], // Change 'Close' to the macroeconomic value
    [height - marginBottom, marginTop]
  );

  // Function to set up a random gradient
  function setRandomGradient(svg) {
    const colors = ["#7C4DFF", "#448AFF", "#FF5252", "#64FFDA"];
    const baseColor = colors[Math.floor(Math.random() * colors.length)];

    // Create a gradient definition
    svg.select("defs").remove(); // Remove any existing gradients
    const defs = svg.append("defs");
    const gradient = defs.append("linearGradient")
      .attr("id", "randomGradient")
      .attr("x1", "0%")
      .attr("x2", "0%")
      .attr("y1", "0%")
      .attr("y2", "100%")
      .attr("spreadMethod", "pad");

    gradient.append("stop").attr("offset", "0%").attr("stop-color", baseColor).attr("stop-opacity", 1);
    gradient.append("stop").attr("offset", "100%").attr("stop-color", baseColor).attr("stop-opacity", 0);

    return baseColor;
  }

  // Create the SVG container
  const svg = d3.create("svg")
    .attr("viewBox", [0, 0, width, height])
    .attr("width", "100%")
    .attr("height", "100%")
    .attr(
      "style",
      "max-width: 100%; height: auto; height: intrinsic; font: 10px sans-serif;"
    )
    .style("-webkit-tap-highlight-color", "transparent")
    .style("overflow", "visible");

  svg.append("defs")
    .append("clipPath")
    .attr("id", "clip")
    .append("rect")
    .attr("width", width - marginLeft - marginRight)
    .attr("height", height - marginTop - marginBottom)
    .attr("x", marginLeft)
    .attr("y", marginTop);

  // Set the random gradient and line color
  const randomColor = setRandomGradient(svg);

  // Set up the area generator
  const area = d3.area()
    .x((d) => x(d.Date))
    .y0(height - marginBottom)
    .y1((d) => y(d.Value));

  // Set up the line generator
  const line = d3.line()
    .x((d) => x(d.Date))
    .y((d) => y(d.Value));

  // Append the area path
  svg.append("path")
    .attr("clip-path", "url(#clip)")
    .attr("class", "area")
    .attr("fill", "url(#randomGradient)")
    .attr("d", area(data));

  // Append the line path
  svg.append("path")
    .attr("clip-path", "url(#clip)")
    .attr("class", "line-path")
    .attr("fill", "none")
    .attr("stroke", randomColor)
    .attr("stroke-width", 1.5)
    .attr("d", line(data));

  // Add the x-axis
  svg.append("g")
    .attr("class", "x-axis")
    .attr("transform", `translate(0,${height - marginBottom})`)
    .call(
      d3.axisBottom(x)
        .ticks(width / 80)
        .tickSizeOuter(0)
    );

  // Add the y-axis, remove the domain line, add grid lines and a label
  svg.append("g")
    .attr("transform", `translate(${marginLeft},0)`)
    .call(d3.axisLeft(y).ticks(height / 40))
    .call((g) => g.select(".domain").remove())
    .call((g) =>
      g.selectAll(".tick line")
        .clone()
        .attr("x2", width - marginLeft - marginRight)
        .attr("stroke-opacity", 0.1)
    )
    .call((g) =>
      g.append("text")
        .attr("x", -marginLeft)
        .attr("y", 10)
        .attr("fill", "currentColor")
        .attr("text-anchor", "start")
        .text("↑ Value")
    );

  // Create the tooltip container
  const tooltip = svg.append("g");

  function formatValue(value) {
    return value.toLocaleString("en");
  }

  function formatDate(date) {
    return date.toLocaleString("en", {
      month: "short",
      day: "numeric",
      year: "numeric",
      timeZone: "UTC",
    });
  }

  // Add the event listeners that show or hide the tooltip
  const bisect = d3.bisector((d) => d.Date).center;

  function pointermoved(event) {
    const i = bisect(data, x.invert(d3.pointer(event)[0]));
    tooltip.style("display", null)
      .attr("transform", `translate(${x(data[i].Date)},${y(data[i].Value)})`);

    const path = tooltip.selectAll("path")
      .data([,])
      .join("path")
      .attr("fill", "white")
      .attr("stroke", "black");

    const text = tooltip.selectAll("text")
      .data([,])
      .join("text")
      .call((text) =>
        text.selectAll("tspan")
          .data([formatDate(data[i].Date), formatValue(data[i].Value)])
          .join("tspan")
          .attr("x", 0)
          .attr("y", (_, j) => `${j * 1.1}em`)
          .attr("font-weight", (_, j) => (j ? null : "bold"))
          .text((d) => d)
      );

    size(text, path);
  }

  function pointerleft() {
    tooltip.style("display", "none");
  }

  function size(text, path) {
    const { x, y, width: w, height: h } = text.node().getBBox();
    text.attr("transform", `translate(${-w / 2},${15 - y})`);
    path.attr(
      "d",
      `M${-w / 2 - 10},5H-5l5,-5l5,5H${w / 2 + 10}v${h + 20}h-${w + 20}z`
    );
  }

  // Listening rectangle for mouse events
  svg.append("rect")
    .attr("width", width)
    .attr("height", height - marginTop)
    .style("fill", "none")
    .style("pointer-events", "all")
    .on("pointerenter pointermove", pointermoved)
    .on("pointerleave", pointerleft);

  return svg.node();
}

// Function to load and parse the macroeconomic CSV file, then display the chart
function loadAndDisplayMacroeconomicChart(csvFile) {
  d3.csv(csvFile)
    .then((data) => {
      const parseDate = d3.timeParse("%Y-%m-%d"); // Adjust the date format as needed
      const parsedData = data.map((d) => ({
        Date: parseDate(d.DATE), // Adjust the date column name as needed
        Value: +d.DATA, // Replace 'DATA' with the appropriate column name for the numeric values
      }));

      const chart = createMacroeconomicChart(parsedData); // Create the chart
      const chartContainer = document.getElementById("close-chart");
      chartContainer.innerHTML = ""; // Clear the container
      chartContainer.appendChild(chart); // Append the new chart
    })
    .catch((error) => {
      console.log(error);
    });
}

// Event listener for chart selector
document.getElementById("chart-selector")
  .addEventListener("change", function () {
    const selectedFile = this.value; // Get the selected file from the dropdown
    loadAndDisplayMacroeconomicChart("../Macro data/" + selectedFile); // Load and display the chart for the selected file
  });

// Load the initial chart
loadAndDisplayMacroeconomicChart("../Macro data/GDP.csv");
