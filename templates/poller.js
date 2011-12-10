// Copyright 2009 FriendFeed
//
// Licensed under the Apache License, Version 2.0 (the "License"); you may
// not use this file except in compliance with the License. You may obtain
// a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations
// under the License.
var xhrlp = '';
$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    $("#messageform").live("submit", function() {
	newMessage($(this));
	return false;
    });
    $("#messageform").live("keypress", function(e) {
	if (e.keyCode == 13) {
	    newMessage($(this));
	    return false;
	}
    });
    $("#message").select();
    {% if user.is_authenticated %}
    updater.start();
    updater.keepalive();
    
    {% endif %}
});



function newMessage(form) {
    var message = form.formToDict();
    var disabled = form.find("input[type=submit]");
    disabled.disable();
    $.postJSON("{% url fetch-new %}", message, function(response) {
	updater.showMessage(response);
	if (message.id) {
	    form.parent().remove();
	} else {
	    form.find("input[type=text]").val("").select();
	    disabled.enable();
	}
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

jQuery.postJSON = function(url, args, callback) {
    $.ajax({url: url, dataType: "text", type: "POST",
	    success: function(response) {
	if (callback) callback(eval("(" + response + ")"));
    }, error: function(response) {
	console.log("ERROR:", response)
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
    xhrlp: null,
    keepalivetime:  120000,
    keepalive: function (){
	try {
		updater.xhrlp.abort();
	}
	catch (e) {	 
	}
	updater.poll();
	if (updater.errorSleepTime == 500){
		window.setTimeout(updater.keepalive, updater.keepalivetime);
	}
	else{
		window.setTimeout(updater.keepalive, updater.keepalivetime+updater.errorSleepTime);
	}
	},
    
    start: function() {
		$.ajax({url: "{% url fetch-existing %}", type: "POST", dataType: "text",
    		success: updater.onFetchExisting,
    		error: updater.onError});
        },
    
    poll: function() {
    	{% if user.is_authenticated %}
    	if (updater.errorSleepTime > 60000){
    		window.setTimeout('location.reload()', 1000);
    		}
    	updater.xhrlp=$.ajax({url: "{% url fetch-updates %}", type: "POST", dataType: "text",
    		success: updater.onSuccess,
    		error: updater.onError});
    	{% endif %}
    },
    onSuccess: function(response) {
	try {
	    updater.newMessages(eval("(" + response + ")"));
	} catch (e) {
	    updater.onError();
	    return;
	}
	updater.errorSleepTime = 500;
	window.setTimeout(updater.poll, 0);
    },

    onFetchExisting: function(response) {
    	try {
    	    updater.existingMessages(eval("(" + response + ")"));
    	} catch (e) {
//    	    updater.onError();
    	    return;
    	}
        },
     
    onError: function(response, text) {
        	if (text != 'abort'){
				updater.errorSleepTime *= 2;
				console.log("Poll error; sleeping for", updater.errorSleepTime, "ms");
				window.setTimeout(updater.keepalive, updater.errorSleepTime);
        	}
    },

    newMessages: function(response) {
	if (!response.messages) return;
	updater.cursor = response.cursor;
	var messages = response.messages;
	updater.cursor = messages[messages.length - 1].id;
//	console.log(messages.length, "new messages, cursor:", updater.cursor);
	
	for (var i = 0; i < messages.length; i++) {
	    updater.showMessage(messages[i]);
	}
	$("#hid_mid").val('UPDATED');
	if (($('#console').dialog('isOpen')) == false){
		blink("#consolebutton");
		window.setTimeout('location.reload()', 3000);
	}
    },

    existingMessages: function(response) {
    	if (!response.messages) return;
    	updater.cursor = response.cursor;
    	var messages = response.messages;
    	updater.cursor = messages[messages.length - 1].id;
    	for (var i = 0; i < messages.length; i++) {
    	    updater.showMessage(messages[i]);
    	}
        },
   
    showMessage: function(message) {
	var existing = $("#m" + message.id);
	if (existing.length > 0) return;
	var node = $(message.html);
	node.hide();
//	 $('#inbox').val($('#inbox').val()+message.text); 
	$("#inbox").append(node);
	node.slideDown();
    }
};

function blink(selector){
	$(selector).animate({ color: "red" }, 500, function(){
	$(this).animate({ color: "#555555" }, 500, function(){
	blink(this);
	});
	});
}

