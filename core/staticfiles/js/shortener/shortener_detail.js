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
  navigator.clipboard.writeText(link);
  alert("Copied the text: " + link);
}