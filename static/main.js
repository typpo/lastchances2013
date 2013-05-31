$(function() {
	var template = Handlebars.compile('<div class="panel"><button type="button" class="close unchoose" data-uid="{{uid}}">&times;</button><h4>{{ name }}&nbsp;&nbsp;&nbsp;{{ department }}</h4></div>');
	var choose = function(person) {
		var element = $(template(person));
		element.prependTo('#choices').hide().slideDown();
		return element;
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
		$(this).parent().slideUp();
		$.post('/unchoose', {'choice': $(this).data('uid') }, function() {
		}).fail(function(jqxhr) {
		});
	});

	$(".alert").hide();
	var search = $('#search input').typeahead({
		name: 'people',
		valueKey: 'name',
		remote: {
			url: 'http://dnd.hackdartmouth.org/%QUERY&department=\'|UG|TU',
			dataType: 'jsonp'
		},
		template: Handlebars.compile('<div data-uid="{{ uid }}" class="name">{{ name }}</div><div class="year">{{department}}</div>'),
	});

	$(search).on('typeahead:selected', function(e, data) {
		var element = choose(data);
		$.post('/choose', {'choice': data['uid']}, function() {
			$(".alert").hide()
			$("#search input").val('');
		}).fail(function(jqxhr) {
			var data = JSON.parse(jqxhr.responseText);
			$(".alerttext").html(data.error);
			$(".alert").show();
			element.remove();
		});
	});

	fill_choices();

});
