const googleTrends = require('google-trends-api');
const fs = require('fs');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;

const keywords = {
  CNY: 'yuanes',
  CZK: 'coronas checas',
  JPY: 'yen japones',
  MAD: 'dirhams',
  MXN: 'pesos mexicanos',
};

const startTime = new Date('2021-01-01');
const endTime = new Date('2022-01-01'); // #Podemos ajustar fechas
const results = [];

async function getTrends(keyword, code) {
  try {
    const res = await googleTrends.interestOverTime({
      keyword: keyword,
      startTime,
      endTime,
      granularTimeResolution: true,
      geo: 'ES'
    });

    const data = JSON.parse(res);
    if (!data.default || !data.default.timelineData) return;

    data.default.timelineData.forEach(entry => {
      const date = new Date(parseInt(entry.time) * 1000).toISOString().split('T')[0];
      const value = entry.value[0];
      results.push({
        date,
        divisa: code,
        term: keyword,
        trend_index: value
      });
    });

    console.log(`✅ ${code} → "${keyword}" completado`);
  } catch (error) {
    console.error(`❌ Error con ${code}:`, error.message);
  }
}

(async () => {
  for (const [code, keyword] of Object.entries(keywords)) {
    await getTrends(keyword, code);
    await new Promise(resolve => setTimeout(resolve, 3000)); // Pausa para evitar bloqueos
  }

  // Ordenar por fecha y divisa (opcional)
  results.sort((a, b) => {
    if (a.date === b.date) return a.divisa.localeCompare(b.divisa);
    return new Date(a.date) - new Date(b.date);
  });

  const csvWriter = createCsvWriter({
    path: '/workspaces/JMT1ST-ECSF-External-Variables/trends/google_trends.csv', 
    header: [
      { id: 'date', title: 'date' },
      { id: 'divisa', title: 'divisa' },
      { id: 'term', title: 'term' },
      { id: 'trend_index', title: 'trend_index' },
    ]
  });

  await csvWriter.writeRecords(results);
  console.log('📁 CSV generado: trends/google_trends_intencion_compra.csv');
})();
