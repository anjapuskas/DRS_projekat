var inputKolicina = document.getElementById('inputKolicina');
var inputValuta = document.getElementById('inputValuta');
var outputVrednost = document.getElementById('outputVrednost');

inputKolicina.onchange = function() {
alert(inputValuta.value)


outputVrednost.value = inputKolicina.value * inputValuta.value.vrednost

}