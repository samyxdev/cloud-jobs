$(function() {
  
// configuration
// button
var add = $('#add');

// list container
var listContainer = $('#list');



// click event for button

add.on('click', function() {

     event.preventDefault(); // stop default behaviour of submit button
    // value of input
    inputValue = $('#input').val();

    // add new list item
    if (inputValue != ''){
        listContainer.prepend('<li> ' + inputValue + '</li>');
    }

    // clear value input
    $('#input').val('');
});
  
});