const { makeFeatureFlags, isCountdownEnabled, getFormVariant } = require('./featureFlags');

test('countdown is enabled when ENABLE_COUNTDOWN_TIMER = true', () => {
  const flags = makeFeatureFlags(true, false);                 // 開倒數、關簡化表單
  expect(isCountdownEnabled(flags)).toBe(true);                // 應該啟用倒數
});

test('countdown is disabled when ENABLE_COUNTDOWN_TIMER = false', () => {
  const flags = makeFeatureFlags(false, true);                 // 關倒數、開簡化表單
  expect(isCountdownEnabled(flags)).toBe(false);               // 應該關閉倒數
});

test('simple form variant when ENABLE_SIMPLE_FORM = true', () => {
  const flags = makeFeatureFlags(false, true);                 // 開簡化表單
  expect(getFormVariant(flags)).toBe('simple');                // 應該是 simple 版
});

test('full form variant when ENABLE_SIMPLE_FORM = false', () => {
  const flags = makeFeatureFlags(true, false);                 // 關簡化表單
  expect(getFormVariant(flags)).toBe('full');                  // 應該是 full 版
});
