function countWords(str) {
  
    const words = str.trim().split(/\s+/);
    return words.length;
}

 
console.log(countWords("Я учусь программированию в вузе"));  

const students = [
    { name: "Азиза", grade: 95 },
    { name: "Бехруз", grade: 87 },
    { name: "Мадина", grade: 92 },
    { name: "Саид", grade: 76 }
];

function sortStudents(arr) {
    return arr.sort((a, b) => b.grade - a.grade);  
}

console.log(sortStudents(students));

function add(a, b) {
    return a + b;
}

function subtract(a, b) {
    return a - b;
}

function multiply(a, b) {
    return a * b;
}

function divide(a, b) {
    if (b === 0) {
        return "Ошибка: деление на ноль!";
    }
    return a / b;
}

 
const num1 = +prompt("Введите первое число:");
const num2 = +prompt("Введите второе число:");
const operation = prompt("Выберите операцию (+, -, *, /):");

let result;

switch (operation) {
    case '+':
        result = add(num1, num2);
        break;
    case '-':
        result = subtract(num1, num2);
        break;
    case '*':
        result = multiply(num1, num2);
        break;
    case '/':
        result = divide(num1, num2);
        break;
    default:
        result = "Неверная операция!";
}

alert(`Результат: ${result}`);
