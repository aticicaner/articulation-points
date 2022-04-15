import * as d3 from 'd3'
import fs from 'fs'

// read data from summary.json
const summaryJson = fs.readFileSync('summary.json', 'utf8')
const summary = JSON.parse(summaryJson)
const groups = Object.keys(summary)

// use d3 to create a bar chart
const barChart = d3.select('body')
    .append('svg')
    .attr('width', 1024)
    .attr('height', 768)
    .selectAll('rect')
    .data(groups)
    .enter()
    .append('rect')
    .attr('x', (d, i) => i * 100)
    .attr('y', (d, i) => 768 - summary[d])
    .attr('width', 100)
    .attr('height', (d, i) => summary[d])
    .attr('fill', 'blue')

// render
barChart.enter().append('text')
    .attr('x', (d, i) => i * 100 + 50)
    .attr('y', (d, i) => 768 - summary[d] + 20)
    .attr('text-anchor', 'middle')
    .text(d => d)

// save pngs
barChart.enter().append('svg:image')
    .attr('xlink:href', (d, i) => `${d}.png`)
    .attr('x', (d, i) => i * 100)
    .attr('y', (d, i) => 768 - summary[d] - 100)
    .attr('width', 100)
    .attr('height', 100)

