export function formatDecimal(value) {
    return value.toFixed(1);
}

export function calculatePercentage(value, total) {
    if (total === 0) return null;
    return (value / total) * 100;
}

export function calculateRiceIndex(inFavor, against) {
    if (inFavor === 0 && against === 0) return null;
    return calculateRiceIndex(inFavor, against);
}