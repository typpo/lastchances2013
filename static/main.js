$(function() {
	var template = Handlebars.compile('<div class="panel fade in"><button type="button" class="close unchoose" data-dismiss="alert" data-uid="{{uid}}">&times;</button><h4>{{ name }}&nbsp;&nbsp;&nbsp;{{ department }}</h4></div>');
	var choose = function(person) {
		$('#choices').prepend(template(person));
	};

	var fill_choices = function () {
		$.get('/chosen', {}, function(data) {
			$('#choices').html('');
			$.each(data, function (i, choice) {
				$.getJSON('http://dnd.hackdartmouth.org/?callback=?', {'uid':choice}, function(data, textStatus, jqXHR) {
					choose(data[0]);
				});
			});
		}, 'json');
	};

	$(document).on('click', '.unchoose', function (e) {
		$.post('/unchoose', {'choice': $(this).data('uid') }, function() {
			$(this).parent().fadeOut();
		}).fail(function(jqxhr) {
		});
	});

	$(".alert").hide();
	var search = $('#search input').typeahead({
		name: 'people',
		valueKey: 'name',
		remote: {
			url: 'http://dnd.hackdartmouth.org/%QUERY',
			dataType: 'jsonp'
		},
		template: Handlebars.compile('<div data-uid="{{ uid }}" class="name">{{ name }}</div><div class="year">{{department}}</div>'),
	});

	$(search).on('typeahead:selected', function(e, data) {
		choose(data);
		$.post('/choose', {'choice': data['uid']}, function() {
			$(".alert").hide()
			$("#search input").val('');
		}).fail(function(jqxhr) {
			var data = JSON.parse(jqxhr.responseText);
			$(".alerttext").html(data.error);
			$(".alert").show();
		});
	});

	fill_choices();

});