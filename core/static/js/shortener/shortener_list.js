var host = window.location.host;


function deleteClick(elementIndex) {
$(document).ready(function() {
var url = $("#url-" + elementIndex).attr("data-url");
$.ajax({type: 'POST',
        url: url,
        data:{
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function() {
        location.reload();
        }
    });
});
}
function copyToClipboard(elementIndex) {
  console.log(elementIndex);
  let href = document.getElementById("link-" + elementIndex);
  href = href.getAttribute("href");
  var link = host + href
  console.log(link);
  navigator.clipboard.writeText(link);
  alert("Copied the text: " + link);
}