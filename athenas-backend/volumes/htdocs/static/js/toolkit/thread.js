
if(typeof(toolkit) != "undefined") {

    toolkit.thread = {

        Simple: function(config) {

//            var defaults = {
//                period: 1000,
//                handler: function() {
//                    alert("Bug: Handler not defined.");
//                }
//            }

            this._period  = config.period;
            this._handler = config.handler;
            this._dei     = false;

        }
    }

    toolkit.thread.Simple.prototype = {

        _period: null,

        _handler: null,

        _dei: false,

        dei: function() {
            this._dei = true;
        },

        isDei: function() {
            return this._dei;
        },

        start: function() {
            if(!this.isDei()) {
                var job = this;
                setTimeout(function() { job.run() }, this._period);
            }
        },

        run: function() {
            this._handler(this);
            this.start();
        }

    }

}