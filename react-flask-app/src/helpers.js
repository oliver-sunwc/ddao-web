export function toCurrency(numberString) {
    let number = parseFloat(numberString);
    return number.toLocaleString('USD');
}