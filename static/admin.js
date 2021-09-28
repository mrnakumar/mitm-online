function submit_form(form_id) {
	var form = document.getElementById(form_id);
	form.submit();
}

function showOrHideUrls(span_id, browsed_urls_panel_id) {
 var hideClass = 'display-not';
 var span = document.getElementById(span_id);
 if(span !== null && span !== undefined) {
	 var value = span.innerHTML;
	 if(value === '+') {
		document.getElementById(browsed_urls_panel_id).style.display = null;
	  span.innerHTML = '--';
	 } else {
		document.getElementById(browsed_urls_panel_id).style.display = 'none';
	  span.innerHTML = '+';
	 }
 }
}
