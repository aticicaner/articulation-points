import fs from 'fs'
import csv from 'csv-parser'

console.log('Reading data from result.csv')

const range = (start, end, increment) => {
    const result = []
    for (let i = start; i <= end; i += increment) {
        result.push(i)
    }
    return result
}

const calculateAverage = (arr) => {
    let stdDev;
    let variance;
    let mean;

    mean = arr.reduce((a, b) => a + b) / arr.length;

    variance = arr.map(x => Math.pow(x - mean, 2)).reduce((a, b) => a + b, 0) / arr.length;

    stdDev = Math.sqrt(variance);

    return {
        mean,
        stdDev
    }
}

const divideData = (data) => {
    const result = {}
    const keys = range(36, 60, 4)
    const compileTimes = []
    const keyGenerationTimes = []
    const encryptionTimes = []
    const executionTimes = []
    const decryptionTimes = []
    const referenceExecutionTimes = []
    keys.forEach(key => {
        data[key.toString()].forEach(dataPoint => {
            compileTimes.push(dataPoint.compileTime)
            keyGenerationTimes.push(dataPoint.keyGenerationTime)
            encryptionTimes.push(dataPoint.encryptionTime)
            executionTimes.push(dataPoint.executionTime)
            decryptionTimes.push(dataPoint.decryptionTime)
            referenceExecutionTimes.push(dataPoint.referenceExecutionTime)
        })
        result[key.toString()] = {
            compileTimes: calculateAverage(compileTimes),
            keyGenerationTimes: calculateAverage(keyGenerationTimes),
            encryptionTimes: calculateAverage(encryptionTimes),
            executionTimes: calculateAverage(executionTimes),
            decryptionTimes: calculateAverage(decryptionTimes),
            referenceExecutionTimes: calculateAverage(referenceExecutionTimes),
        }
    })

    console.log(data['60'].compileTimes)

    return result
}


const data = []
const processedData = {}

fs.createReadStream('results.csv')
    .pipe(csv())
    .on('data', (row) => {

        const dataPoint = {
            nodeCount: parseInt(row.NodeCount),
            pathLength: parseInt(row.PathLength),
            simCnt: parseInt(row.SimCnt),
            compileTime: parseFloat(row.CompileTime),
            keyGenerationTime: parseFloat(row.KeyGenerationTime),
            encryptionTime: parseFloat(row.EncryptionTime),
            executionTime: parseFloat(row.ExecutionTime),
            decryptionTime: parseFloat(row.DecryptionTime),
            referenceExecutionTime: parseFloat(row.ReferenceExecutionTime),
            mse: parseFloat(row.Mse)
        }

        processedData[row.NodeCount] = processedData[row.NodeCount] || []
        processedData[row.NodeCount].push(dataPoint)

        data.push(dataPoint)
    })
    .on('end', () => {
        console.log('Read all data')
        // console.table(data)
        // console.log(processedData['40'])
        console.log(divideData(processedData))
        const output = divideData(processedData)
        fs.writeFileSync('summary.json', JSON.stringify(output))
    });