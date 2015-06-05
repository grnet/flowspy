$(document).ready(function() {
  	$('a#generate_token').one('click', function (ev) {
  		ev.preventDefault();
  		var url = $(this).prop('href');
  		var result = $(this).parent()
  		result.text('loading...');
  		$.ajax({
			url: url,
			success: function (data) {
				result.text(data);
			},
		})
		.fail(function() {
			result.text('An error has occured...');
		});
  	});
});
