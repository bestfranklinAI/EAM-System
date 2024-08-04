function adjustDDLWidth(htmlEl) {
    // Assuming something is always selected (please test!)
    const displayedText = htmlEl.options[htmlEl.selectedIndex].innerText;
    const dummy = document.createElement('div');


    dummy.style.fontsize = "30px";
    dummy.style.fontWeight = "bold";

    dummy.innerText = displayedText;
    dummy.style.position = 'absolute';
    dummy.style.visibility = 'hidden';

    document.body.insertBefore(dummy, document.body.firstChild);

    
    // Add some padding (e.g., 30px) to the calculated width
    if(!isNaN(displayedText)){
        htmlEl.style.width = '100px';
    }
    else{
        console.log(dummy.clientWidth);
        htmlEl.style.width = (dummy.clientWidth+600) + 'px';
    }

    document.body.removeChild(dummy);
}

// const myDropdownEl = document.getElementById('filter');
// adjustDDLWidth(myDropdownEl);
// console.log('Dropdown width adjusted!');


const dropdowns = document.getElementsByClassName('filter');
for (var i = 0; i < dropdowns.length; i++) {
    adjustDDLWidth(dropdowns[i]);
    console.log(`Dropdown ${i} width adjusted!`);
}