var timeout;
var count = 0;
async function getStatus() {
  let get;

  try {
    const res = await fetch("/status");
    get = await res.json();
  } catch (e) {
    console.error("Error: ", e);
  }
  var percentage = get.percentage;
  changeStatus(percentage);

  if (get.boolean ==1){
    document.getElementById("model").innerHTML = "Pulling Local GPT Model for Data Summary ......";
  }

  if (get.boolean == 2) {
    // document.getElementById(".progress-done").innerHTML += " Done.";
    document.getElementById("model").innerHTML = "DONE:)";
    clearTimeout(timeout);
    document.getElementById("view_button").style.display='block';
    return false;
  }
  count += 1;
  timeout = setTimeout(getStatus, 600);
}

function changeStatus(percentage) {

  $("#progress1 .progress-text").text(percentage + "%");
  $("#progress1 .progress-bar").css({ width: percentage + "%" });
}


getStatus();
