View = new Class({
    initialize: function(broker){
        this.broker = broker;
        
        Array.each(this.notification_channels(), function (item, index) {
            this.broker.addEventListener(item, this);
        }.bind(this));
    },

    notification_channels: function() {
        return new Array();
    },

    message: function(message){
    }

});

TextView = new Class({
    Extends: View,

    initialize: function(broker, name) {
        this.name = name
        this.parent(broker);
    },

    notification_channels: function() {
        return new Array(this.name);
    },

    message: function(message){
        if (message.op == "set") {
            $(this.name).innerHTML = message.parameters.content;
        }
        if (message.op == "append") {
            $(this.name).innerHTML += message.parameters.content;
        }

    }
});

Broker = new Class({
  initialize: function(base_url, session_id) {
      this.base_url = base_url + session_id + "/";
      this.session_id = session_id;
      this.event_source = new EventSource(this.base_url);
      this.event_source.addEventListener('open', this.open.bind(this));
      this.event_source.addEventListener('message', this.message.bind(this));
      this.event_source.addEventListener('error', this.error.bind(this));

      this.dispatch_table = new Hash();
  },  

  open: function(event) {
//      document.body.innerHTML += 'opened: ' + this.base_url;
  },

  message: function (event) {
      var msg = JSON.parse(event.data);
      name = msg.id;
      if (this.dispatch_table.has(name)) {
          var targets = this.dispatch_table.get(name)
          Array.each(targets, function (item, index) {
              item.message(msg);
          });
      }
  },
    
  error: function(event) {
//      var div = document.createElement('div');
//      div.innerHTML = 'closed: ' + event.message;
//      document.body.appendChild(div);
  },


  register: function(name) {
      var myRequest = new Request({url: this.base_url});
      
      var data = 'ids=' + name;
      myRequest.send({
          method: 'post',
          data: data});
  },

  addEventListener: function(name, target) {
      if (! this.dispatch_table.has(name)) {
          this.dispatch_table.set(name, new Array());
      }
      this.dispatch_table.get(name).include(target);
      this.register(name);
  }

});