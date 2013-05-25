$(function() {
	var template = Handlebars.compile('<div class="row"><h3 class="pull-left">{{ name }}</h3><h3 class="pull-right">{{ department }}</h3></div>');
	var choose = function(person) {
		$('#choices').prepend(template(person));
	};

	var fill_choices = function () {
		$('#choices').html('');
		$.get('/chosen', {}, function(data) {
			$.each(data, function (i, choice) {
				choose(choice);
			});
		}, 'json');
	};

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
		$.post('/choose', {'choice': data['uid']}, function() {
			$(".alert").hide()
			$(search).val('');
			choose(data);
		}).fail(function(jqxhr) {
			var data = JSON.parse(jqxhr.responseText);
			$(".alerttext").html(data.error);
			$(".alert").show();
		});
	});

	fill_choices();

});
