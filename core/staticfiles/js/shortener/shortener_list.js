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
  const textArea = document.createElement("textarea");
  textArea.value = link;
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();
  try {
    document.execCommand('copy');
    alert("Copied the text: " + link);
  } catch (err) {
    console.error('Unable to copy to clipboard', err);
  }
}