$(function() {
	var search = $('#search input').typeahead({
		name: 'people',
		valueKey: 'name',
		remote: {
			url: 'http://dnd.hackdartmouth.org/%QUERY',
			dataType: 'jsonp'
		},
		template: Handlebars.compile('<div data-uid="{{ uid }}" class="name">{{ name }}</div>'),
	});

	$(search).on('typeahead:selected', function(e, data) {
		$.post('/choose', {'choice': data['uid']}, function() {
			choose(data);
		});
	});

	var template = Handlebars.compile('<div class="row"><h3 class="pull-left">{{ name }}</h3><h3 class="pull-right">{{ department }}</h3></div>');
	var choose = function(person) {
		$('#choices').append(template(person));
	};
});
