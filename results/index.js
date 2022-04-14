// NodeCount,PathLength,SimCnt,
// CompileTime,KeyGenerationTime,
// EncryptionTime,ExecutionTime,
// DecryptionTime,ReferenceExecutionTime,
// Mse

const fs = require('fs')
const csv = require('csv-parser')

console.log('Reading data from result.csv')

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
        console.log(processedData['40'])
    });