$(function() {

    $('#register').click(function (e) {

        if ($('#password').val().length < 1) {
          window.alert("Password cannot be blank");
          return;
        }

        if ($('#password').val() != $('#confirmpassword').val()) {
          window.alert("Passwords do not match!");
          return;
        }

        var key_pair = sjcl.ecc.elGamal.generateKeys();

        var public_key_bits = JSON.stringify(key_pair.pub._point.toBits());
        var private_key_bits = JSON.stringify(key_pair.sec._exponent.toBits());

        var encrypted_private_key = sjcl.json.encrypt($('#password').val(), private_key_bits);

        $.post('/register', {'name': $('#name').val(), 'encrypted_private_key': encrypted_private_key, 'public_key_bits': public_key_bits}, function () {
            window.location.replace("/");
        });
    });

	var template = Handlebars.compile('<div class="panel"><button type="button" class="close unchoose" data-coupleidhash="{{coupleid_hash}}">&times;</button><h4>{{ name }}</h4></div>');
	var choose = function(person) {
        person.name = sjcl.json.decrypt(window.password, person.encrypted_name)
		var element = $(template(person));
		element.prependTo('#choices').hide().slideDown();
		return element;
	};

	var match_template = Handlebars.compile('<div class="panel match"><h4>{{name}}<span class="matchbg pull-right">match!</span></h4></div>');
	var match = function(person) {
		var element = $(match_template(person));
		element.prependTo('#matches').hide().slideDown();
		return element;
	};

	var fill_choices = function () {
		$.get('/chosen', {}, function(data) {
			$('#choices').html('');
			$.each(data, function (i, choice) {
                choose(choice);
			});
		}, 'json');
	};

	var fill_matches = function () {
		$.get('/matches', {}, function(data) {
			$('#matches').html('');
			$.each(data, function (i, choice) {
              match(choice);
			});
		}, 'json');
	};
		

	$(document).on('click', '.unchoose', function (e) {
		$(this).parent().slideUp();
		$.post('/unchoose', {'coupleid_hash': $(this).data('coupleidhash') }, function() {
		}).fail(function(jqxhr) {
		});
	});

	$(".alert-danger").hide();
	var search = $('#search input').typeahead({
		name: 'people',
		valueKey: 'name',
		remote: {
            url: '/participants'
		},
		template: Handlebars.compile('<div class="name">{{ name }} &nbsp;&nbsp;</div>'),
	});

	$(search).on('typeahead:selected', function(e, data) {
        var point = sjcl.ecc.curves.c256.fromBits(JSON.parse(data['public_key_bits']));
        var pub_key = new sjcl.ecc.elGamal.publicKey(sjcl.ecc.curves.c256, point);
        
        var coupleid_hash = sjcl.codec.hex.fromBits(window.private_key.dh(pub_key));

        var encrypted_name = sjcl.json.encrypt(window.password, data['name']);

		$.post('/choose', {'coupleid_hash': coupleid_hash, 'encrypted_name': encrypted_name}, function() {
			$(".alert-danger").hide()
			$("#search input").val('');
            fill_choices();
		}).fail(function(jqxhr) {
			var data = JSON.parse(jqxhr.responseText);
			$(".alert-danger .alerttext").html(data.error);
			$(".alert-danger").show();
            fill_choices();
		});
	});

	fill_choices();
	fill_matches();

});
