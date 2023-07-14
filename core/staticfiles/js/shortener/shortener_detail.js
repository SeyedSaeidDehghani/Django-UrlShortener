var host = window.location.host;

function deleteClick() {
$(document).ready(function() {
var url = $("#url").attr("data-url");
var url_success = $("#url-success").attr("data-url");
$.ajax({type: 'POST',
        url: url,
        data:{
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function() {
            location.href = url_success
        }
    });
});
}

function copyToClipboard() {
  let href = document.getElementById("link");
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
//  document.body.removeChild(textArea);
//
//
//
//  navigator.clipboard.writeText(link);
//  alert("Copied the text: " + link);
}