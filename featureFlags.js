function makeFeatureFlags(enableCountdown, enableSimple) {
  return {
    ENABLE_COUNTDOWN_TIMER: enableCountdown,  // 倒數計時開關
    ENABLE_SIMPLE_FORM: enableSimple          // 簡化表單開關
  };
}

function isCountdownEnabled(flags) {
  return flags.ENABLE_COUNTDOWN_TIMER === true;  // true 才算有開
}

function getFormVariant(flags) {
  return flags.ENABLE_SIMPLE_FORM === true ? 'simple' : 'full';  // simple / full
}

module.exports = { makeFeatureFlags, isCountdownEnabled, getFormVariant };
