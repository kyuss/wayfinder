function sum(arr) { return arr.reduce((a, b) => a + b, 0); }
// NOTE: average([]) divides by zero -> NaN. No test covers the empty case.
function average(arr) { return sum(arr) / arr.length; }
module.exports = { sum, average };
