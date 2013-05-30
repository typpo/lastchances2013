$(function() {
	var template = Handlebars.compile('<div class="row entry"><h3 class="entryname">{{ name }}&nbsp;&nbsp;&nbsp;</h3> <h3 class="entrydept">{{ department }}</h3><a data-uid="{{uid}}" class="deletelink btn btn-danger btn-small"><span class="glyphicon glyphicon-remove"></span></a></div>');
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

	$(document).on('click', '.deletelink', function (e) {
		$.post('/unchoose', {'choice': $(this).data('uid') }, function() {
			fill_choices();
		}).fail(function(jqxhr) {
			fill_choices();
		});
	});

	$(".alert").hide();
	var search = $('#search input').typeahead({
		name: 'people',
		valueKey: 'name',
		remote: {
			url: 'http://dnd.hackdartmouth.org/?name=%QUERY',
	    		/*
	    		replace: function (url, encodedquery) {
				var query = decodeURIComponent(encodedquery);
				return url;
			},
			*/
			dataType: 'jsonp'
		},
		template: Handlebars.compile('<div data-uid="{{ uid }}" class="name">{{ name }}</div><div class="year">{{department}}</div>'),
	});

	$(search).on('typeahead:selected', function(e, data) {
		$.post('/choose', {'choice': data['uid']}, function() {
			$(".alert").hide()
			$("#search input").val('');
			choose(data);
		}).fail(function(jqxhr) {
			var data = JSON.parse(jqxhr.responseText);
			$(".alerttext").html(data.error);
			$(".alert").show();
		});
	});

	fill_choices();

});
