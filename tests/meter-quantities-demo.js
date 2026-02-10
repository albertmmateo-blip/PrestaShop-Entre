/**
 * Simple Test Suite for Meter-Based Quantity Functions
 * 
 * This file demonstrates the rounding behavior of the quantity-meters module.
 * Run in browser console or Node.js environment.
 */

// Import the functions (in a real test, these would be imported from the module)
// For demonstration, we'll define them inline

const METER_STEP = 0.05;
const METER_TO_CM = 100;

function roundToMeterStep(meters) {
  return Math.ceil(meters / METER_STEP) * METER_STEP;
}

function metersToCentimeters(meters) {
  return Math.round(meters * METER_TO_CM);
}

function centimetersToMeters(centimeters) {
  return centimeters / METER_TO_CM;
}

function formatMeters(meters) {
  return meters.toFixed(2);
}

// Test Suite
const tests = [
  // Test rounding up
  { input: 2.71, expected: 2.75, description: '2.71 meters should round up to 2.75' },
  { input: 2.73, expected: 2.75, description: '2.73 meters should round up to 2.75' },
  { input: 2.76, expected: 2.80, description: '2.76 meters should round up to 2.80' },
  { input: 2.78, expected: 2.80, description: '2.78 meters should round up to 2.80' },
  
  // Test rounding up from lower values
  { input: 2.72, expected: 2.75, description: '2.72 meters should round up to 2.75' },
  { input: 2.77, expected: 2.80, description: '2.77 meters should round up to 2.80' },
  { input: 2.23, expected: 2.25, description: '2.23 meters should round up to 2.25' },
  { input: 2.21, expected: 2.25, description: '2.21 meters should round up to 2.25' },
  
  // Test exact values
  { input: 1.00, expected: 1.00, description: '1.00 meters should stay 1.00' },
  { input: 1.25, expected: 1.25, description: '1.25 meters should stay 1.25' },
  { input: 2.45, expected: 2.45, description: '2.45 meters should stay 2.45' },
  { input: 3.75, expected: 3.75, description: '3.75 meters should stay 3.75' },
  
  // Test edge cases
  { input: 0.01, expected: 0.05, description: '0.01 meters should round up to 0.05' },
  { input: 0.02, expected: 0.05, description: '0.02 meters should round up to 0.05' },
  { input: 0.03, expected: 0.05, description: '0.03 meters should round up to 0.05' },
  { input: 0.04, expected: 0.05, description: '0.04 meters should round up to 0.05' },
  { input: 0.05, expected: 0.05, description: '0.05 meters should stay 0.05' },
];

// Conversion tests
const conversionTests = [
  { meters: 1.00, centimeters: 100, description: '1.00 meters = 100 centimeters' },
  { meters: 1.25, centimeters: 125, description: '1.25 meters = 125 centimeters' },
  { meters: 2.75, centimeters: 275, description: '2.75 meters = 275 centimeters' },
  { meters: 0.05, centimeters: 5, description: '0.05 meters = 5 centimeters' },
  { meters: 10.50, centimeters: 1050, description: '10.50 meters = 1050 centimeters' },
];

// Run rounding tests
console.log('=== Rounding Tests ===\n');
let passedRounding = 0;
let failedRounding = 0;

tests.forEach((test, index) => {
  const result = roundToMeterStep(test.input);
  const passed = Math.abs(result - test.expected) < 0.001; // Allow for floating point precision
  
  if (passed) {
    passedRounding++;
    console.log(`✓ Test ${index + 1}: ${test.description}`);
    console.log(`  Input: ${test.input} → Output: ${result} (Expected: ${test.expected})\n`);
  } else {
    failedRounding++;
    console.log(`✗ Test ${index + 1}: ${test.description}`);
    console.log(`  Input: ${test.input} → Output: ${result} (Expected: ${test.expected})\n`);
  }
});

// Run conversion tests
console.log('=== Conversion Tests ===\n');
let passedConversion = 0;
let failedConversion = 0;

conversionTests.forEach((test, index) => {
  const centimeters = metersToCentimeters(test.meters);
  const backToMeters = centimetersToMeters(centimeters);
  const passed = centimeters === test.centimeters && Math.abs(backToMeters - test.meters) < 0.001;
  
  if (passed) {
    passedConversion++;
    console.log(`✓ Test ${index + 1}: ${test.description}`);
    console.log(`  Meters → Centimeters: ${test.meters} → ${centimeters}`);
    console.log(`  Centimeters → Meters: ${centimeters} → ${backToMeters}\n`);
  } else {
    failedConversion++;
    console.log(`✗ Test ${index + 1}: ${test.description}`);
    console.log(`  Meters → Centimeters: ${test.meters} → ${centimeters} (Expected: ${test.centimeters})`);
    console.log(`  Centimeters → Meters: ${centimeters} → ${backToMeters}\n`);
  }
});

// Summary
console.log('=== Test Summary ===\n');
console.log(`Rounding Tests: ${passedRounding} passed, ${failedRounding} failed (${tests.length} total)`);
console.log(`Conversion Tests: ${passedConversion} passed, ${failedConversion} failed (${conversionTests.length} total)`);
console.log(`\nTotal: ${passedRounding + passedConversion} passed, ${failedRounding + failedConversion} failed (${tests.length + conversionTests.length} total)`);

if (failedRounding === 0 && failedConversion === 0) {
  console.log('\n✓ All tests passed!');
} else {
  console.log('\n✗ Some tests failed.');
}

// Example usage demonstrations
console.log('\n=== Usage Examples ===\n');

const examples = [
  { input: 2.71, description: 'Customer enters 2.71 meters' },
  { input: 2.76, description: 'Customer enters 2.76 meters' },
  { input: 1.23, description: 'Customer enters 1.23 meters' },
];

examples.forEach(example => {
  const rounded = roundToMeterStep(example.input);
  const centimeters = metersToCentimeters(rounded);
  console.log(`${example.description}:`);
  console.log(`  → Rounded to: ${formatMeters(rounded)} meters`);
  console.log(`  → Stored as: ${centimeters} centimeters`);
  console.log(`  → Displayed as: ${formatMeters(centimetersToMeters(centimeters))} meters\n`);
});
