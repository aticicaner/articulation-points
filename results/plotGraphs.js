import * as d3 from 'd3'
import fs from 'fs'

// read data from summary.json
const summaryJson = fs.readFileSync('summary.json', 'utf8')
const summary = JSON.parse(summaryJson)
const groups = Object.keys(summary)

