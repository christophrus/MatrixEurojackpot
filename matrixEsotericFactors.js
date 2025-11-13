// matrixEsotericFactors.js
export function getEsotericSeedComponents(date, seedString = "") {
  const time = date.getTime();
  seedString = String(seedString);

  // 1. Mondphase
  const moonPhase = ((time / 86400000) % 29.53) / 29.53;

  // 2. Numerologische Quersumme des Datums
  const dateString = date.toISOString().split("T")[0].replace(/-/g, "");
  const numerology = dateString.split("").reduce((a, c) => a + Number(c), 0) % 9;

  // 3. Sternzeichen-Code
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const zodiacCode = getZodiacCode(month, day);

  // 4. Text-Seed Wert
  const textValue = seedString
    ? [...seedString.toLowerCase()].reduce((a, c) => a + c.charCodeAt(0), 0)
    : 0;

  // 5. Planck-Drift
  const drift = Math.sin((time / 86400000) * Math.PI / 137);

  // 6. Schumann-Frequenz (Basis 7.83 Hz, leichte deterministische Variation)
  const baseSchumann = 7.83;
  const variation = ((day + month + textValue) % 100) / 100; // 0..0.99 Hz
  const schumann = baseSchumann + variation;

  // Kombinierter deterministischer Seed
  const combined =
    moonPhase * 1000 +
    numerology * 13 +
    zodiacCode * 7 +
    textValue * 0.01 +
    drift * 100 +
    schumann * 10;

  return { moonPhase, numerology, zodiacCode, textValue, drift, schumann, combined };
}

function getZodiacCode(month, day) {
  const zodiacs = [
    { from: [12,22], to: [1,19], code: 11 },
    { from: [1,20], to: [2,18], code: 22 },
    { from: [2,19], to: [3,20], code: 33 },
    { from: [3,21], to: [4,19], code: 44 },
    { from: [4,20], to: [5,20], code: 55 },
    { from: [5,21], to: [6,20], code: 66 },
    { from: [6,21], to: [7,22], code: 77 },
    { from: [7,23], to: [8,22], code: 88 },
    { from: [8,23], to: [9,22], code: 99 },
    { from: [9,23], to: [10,22], code: 111 },
    { from: [10,23], to: [11,21], code: 222 },
    { from: [11,22], to: [12,21], code: 333 }
  ];
  const zodiac = zodiacs.find(z => {
    const [fm, fd] = z.from;
    const [tm, td] = z.to;
    return (month === fm && day >= fd) || (month === tm && day <= td);
  });
  return zodiac ? zodiac.code : 0;
}
