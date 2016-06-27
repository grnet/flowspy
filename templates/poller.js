
var xhrlp = '';
$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    $("#message").select();
    {% if user.is_authenticated %}
    updater.start();
    updater.poll();
    {% endif %}
});

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

jQuery.postJSON = function(url, args, callback) {
    $.ajax({url: url, dataType: "json", type: "POST", cache: false,
	    success: function(response) {
	if (callback) callback(response);
    }, error: function(response) {
	console.log("ERROR:", response);
    }});
};

jQuery.fn.formToDict = function() {
    var fields = this.serializeArray();
    var json = {}
    for (var i = 0; i < fields.length; i++) {
	json[fields[i].name] = fields[i].value;
    }
    if (json.next) delete json.next;
    return json;
};

jQuery.fn.disable = function() {
    this.enable(false);
    return this;
};

jQuery.fn.enable = function(opt_enable) {
    if (arguments.length && !opt_enable) {
        this.attr("disabled", "disabled");
    } else {
        this.removeAttr("disabled");
    }
    return this;
};

var updater = {
    errorSleepTime: 500,
    cursor: null,
    start: function() {
    	    var date = new Date();
			var timestamp = date.getTime();
        {% for peer in user.userprofile.peers.all %}
        $.ajax({url: "{% url 'fetch-existing'  peer.pk %}?="+timestamp, type: "POST", dataType: "json", cache:false,
    		success: updater.onFetchExisting,
    		error: updater.onError});
        {% endfor %}
        },
    poll: function() {
    	{% if user.is_authenticated %}
    	if (updater.errorSleepTime > 128000){
    		oTable.fnReloadAjax(refreshUrl);
    	}
    	timeout = {{timeout}};
    	    var date = new Date();
			var timestamp = date.getTime();
        {% for peer in user.userprofile.peers.all %}
        $.ajax({url: "{% url 'fetch-updates'  peer.pk %}?="+timestamp, type: "POST", dataType: "json", cache:false,
    		success: updater.onSuccess,
    		timeout: timeout,
    		error: updater.onError});
        {% endfor %}
    	{% endif %}
    },
    onSuccess: function(response) {
	try {
	    updater.newMessages(response);
	} catch (e) {
	    updater.onError();
	    return;
	}
	updater.errorSleepTime = 500;
	window.setTimeout(updater.poll, 0);
    },

    onFetchExisting: function(response) {
    	try {
    	    updater.existingMessages(response);

    	} catch (e) {
    	    updater.onError();
    	    return;
    	}
        },

    onError: function(response, text) {
        	if (text == 'timeout'){
        		oTable.fnReloadAjax(refreshUrl);
        	}
        	updater.errorSleepTime *= 2;
			console.log("Poll error; sleeping for", updater.errorSleepTime, "ms");
			window.setTimeout(updater.poll, updater.errorSleepTime);

    },

    newMessages: function(response) {
	if (!response.messages) return;
	if (response.messages.length == 0){
		return true;
	}
	updater.cursor = response.cursor;
	var messages = response.messages;
	updater.cursor = messages[messages.length - 1].id;
	console.log(messages.length, "new messages, cursor:", updater.cursor);

	for (var i = 0; i < messages.length; i++) {
	    updater.showMessage(messages[i]);
	}
	$("#hid_mid").val('UPDATED');
	oTable.fnReloadAjax(refreshUrl);
    },

    existingMessages: function(response) {
    	if (!response.messages) return;
    	if (response.messages.length == 0){
    		return true;
    	}
    	updater.cursor = response.cursor;
    	var messages = response.messages;
    	updater.cursor = messages[messages.length - 1].id;
    	var i = messages.length
    	for (var i = 0; i < messages.length; i++) {
    	    updater.showMessage(messages[i]);
    	}
        },

    showMessage: function(message) {
	var existing = $("#m" + message.id);
	if (existing.length > 0) return;
	var username = message.body.split("]")[0].replace("[","");
	var mbody = message.body.replace("["+username+"] ","");
	var htmlnode = '<li class="left clearfix">\
                                    <div class="chat-body clearfix" style="margin-left: 0px;"> \
                                        <div class="header"> \
                                            <small class="pull-right text-muted"> \
                                                <i class="fa fa-clock-o fa-fw"></i> '+ message.time +'  \
                                            </small>\
                                        </div>\
                                        <p><small><strong class="primary-font">'+username+'</strong>:\
                                            '+ mbody+'\
                                        </small></p>\
                                    </div>\
                                </li>';
	var node = $(htmlnode);
	node.hide();
//	 $('#inbox').val($('#inbox').val()+message.text);
	$("#inbox").prepend(node);
	node.slideDown();
    }
};

function blink(selector){
	$(selector).animate({color: "#EE5F5B"}, 500, function(){
		$(this).animate({ color: "white" }, 500, function(){
			blink(this);
		});
	});
}

